"""Build the status-update submission for BOBILib's maintainers.

usage (from bobilib/):  python3 -I scripts/build_submission.py [--no-tar]

Reads the data package (results/instances.csv, results/bobilib_update.solu,
the certificate tables and results/notes/official_checker.tsv) and writes

  submission/status_changes.csv       one row per instance whose status or best known value changes
  submission/bobilib_update.solu      copy of results/bobilib_update.solu
  submission/README.md                for the maintainers: contents, counts, how to check each claim
  submission/bobilib_submission.tar.gz (gitignored) one file to attach or link: the solution files
                                      in BOBILib's format, the certificates and the checkers

Every count is computed from results/instances.csv and checked against
results/bobilib_update.solu; the script stops if they disagree. The archive is
deterministic (sorted members, fixed times and owners), so rebuilding from the
same repository state gives the same bytes.
"""
import csv
import gzip
import hashlib
import io
import json
import os
import re
import sys
import tarfile
import textwrap
from collections import Counter

R = "results"
OUT = "submission"
TAR = f"{OUT}/bobilib_submission.tar.gz"
MANIFEST = "data-manifest/bobilib_snapshot.tsv"
PREFIX = "bobilib_submission"
REPO = "https://github.com/brian-j-connolly-aero/bobilib"
SNAPSHOT = "2026-10-18"
META_SHA256 = "9a7c5c395a6bf8fddc405fac81fd0b1353f16671d36d5efc8e0b2b6dae4c0c10"  # collection.json of SNAPSHOT
CHECKER_SHA256 = "80286841dc3052e49f3902f8b1addd62a657ce378dbc92cdc6eab4198506138f"  # feasibility-checker.tar.gz
EPOCH = 1793145600  # 2026-10-28 00:00 UTC: time stamp of every archive member

KINDS = ["new optimum proven", "published optimum", "no bilevel feasible point", "first feasible point",
         "better feasible point"]
# Expected counts (the paper's title and results/README.md): checked, not used to compute anything.
EXPECT = {"new optimum proven": 79, "published optimum": 531, "no bilevel feasible point": 40,
          "first feasible point": 228, "better feasible point": 465}
TITLE = (f"Settling 650 unsolved BOBILib instances: {EXPECT['published optimum']} published optima, "
         f"{EXPECT['new optimum proven']} new optimality proofs and {EXPECT['no bilevel feasible point']} "
         "infeasibility certificates")

CITATION = {
    "this work": f"B. J. Connolly, {TITLE}, preprint (2026); " + REPO,
    "WeningerFukasawa2022Code": "N. Weninger and R. Fukasawa, bkpsolver repository, answer files instances/*/*.ans "
                                "(initial commit d8c3b74, repository public by 7 October 2022), "
                                "https://github.com/nwoeanhinnogaehr/bkpsolver; the code of their paper in "
                                "Math. Program. 210 (2025) 847-879, doi:10.1007/s10107-024-02133-9",
    "FischettiEtAl2016Report": "M. Fischetti, I. Ljubić, M. Monaci and M. Sinnl, Interdiction games and monotonicity, "
                               "technical report, DEI, University of Padova (2016), "
                               "www.dei.unipd.it/~fisch/papers/interdiction_games_and_monotonicity.pdf; preprint of "
                               "INFORMS J. Comput. 31(2) (2019) 390-410, doi:10.1287/ijoc.2018.0831",
    "CapraraEtAl2016": "A. Caprara, M. Carvalho, A. Lodi and G. J. Woeginger, INFORMS J. Comput. 28(2) (2016) "
                       "319-333, doi:10.1287/ijoc.2015.0676",
    "LozanoBergmanCire2026": "L. Lozano, D. Bergman and A. A. Cire, Oper. Res. (2026), Articles in Advance, "
                             "doi:10.1287/opre.2025.2457",
    "FischettiEtAl2019": "M. Fischetti, I. Ljubić, M. Monaci and M. Sinnl, INFORMS J. Comput. 31(2) (2019) "
                         "390-410, doi:10.1287/ijoc.2018.0831",
    "FischettiEtAl2017": "M. Fischetti, I. Ljubić, M. Monaci and M. Sinnl, Oper. Res. 65(6) (2017) 1615-1637, "
                         "doi:10.1287/opre.2017.1650, and its online appendix of 29 June 2016 "
                         "(www.dei.unipd.it/~fisch/appendix.pdf)",
    "VasquezLozanoVanHoeve2025": "S. Vásquez, L. Lozano and W.-J. van Hoeve, Math. Program. (2025), "
                                 "doi:10.1007/s10107-025-02294-1",
    "LefebvreSchmidt2025": "H. Lefebvre and M. Schmidt, A Dantzig-Wolfe single-level reformulation for "
                           "mixed-integer linear bilevel optimization: exact and heuristic approaches, Optimization "
                           "Online preprint (June 2025), run file results-MILP.csv on the first author's web page "
                           "(henrilefebvre.com)",
    "BOBILibEarlierRelease": "an earlier release of the BOBILib metadata, which listed the instance as optimal",
}

SHORT = {"WeningerFukasawa2022Code": "Weninger and Fukasawa (2022, answer files)",
         "FischettiEtAl2016Report": "Fischetti et al. (2016, technical report)", "CapraraEtAl2016": "Caprara et al. (2016)",
         "LozanoBergmanCire2026": "Lozano, Bergman and Cire (2026)",
         "FischettiEtAl2019": "Fischetti et al. (2019)", "FischettiEtAl2017": "Fischetti et al. (2017)",
         "VasquezLozanoVanHoeve2025": "Vasquez, Lozano and van Hoeve (2025)",
         "LefebvreSchmidt2025": "Lefebvre and Schmidt (2025, run file)",
         "BOBILibEarlierRelease": "an earlier BOBILib release"}

SUPP = {  # sections of the paper's supplement (paper/appendix/appendix.pdf), by title
    "ss": "Knapsack interdiction proofs",
    "clique": "Clique interdiction proofs",
    "network": "Network interdiction",
    "hpr": "General instances: rays, HPR bound and pipelines (The HPR bound and the MIPLIB optimum)",
    "ray": "General instances: rays, HPR bound and pipelines (Unbounded followers: no bilevel feasible point)",
    "or": "Multidimensional knapsack interdiction proofs (Certified points)",
    "general": "General instances: rays, HPR bound and pipelines (Feasible points without coupling rows; "
               "Coupling rows)",
    "published": "Per-instance tables (Published optima)",
}

COLS = ["instance", "collection", "family", "bobilib_status", "bobilib_value", "new_status", "new_value",
        "kind", "check", "certificate_class", "solution_file", "official_checker", "certificate_files",
        "how_to_check", "supplement", "source", "citation", "notes"]

# Files copied into the archive besides the solution files and the per-row certificates.
CHECKERS = {
    "checkers/verify_ray.py": "scripts/verify_ray.py",
    "checkers/check_clique_certificates.py": "scripts/check_clique_certificates.py",
    "checkers/ss_check.py": "scripts/ss_check.py",
    "checkers/compare_hpr.py": "scripts/compare_hpr.py",
    "checkers/run_official_checker.py": "scripts/run_official_checker.py",
    "checkers/network/parse_fire_model.py": "scripts/fire_review/parse_fire_model.py",
    "checkers/network/fire_check.c": "scripts/fire_review/fire_check.c",
    "checkers/network/check_solution.py": "scripts/fire_review/check_solution.py",
}
DOCS = ["ss/README.md", "ss/proofs.csv", "clique/README.md", "clique/summary.csv",
        "clique/certificates/README.md", "clique/certificates/check.log", "network/README.md",
        "network/summary.csv", "network/review.tsv", "rays/README.md", "general/README.md",
        "general/hpr_optimal.csv", "general-coupled/README.md", "or/README.md", "kip/README.md",
        "notes/official_checker.md", "notes/official_checker.tsv", "notes/official_checker_superseded.tsv",
        "notes/tight_verify.md",
        "notes/tight_verify.tsv"]


def fail(msg):
    sys.exit(f"build_submission: check failed: {msg}")


def check(cond, msg):
    if not cond:
        fail(msg)


def load_csv(path, delim=","):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=delim))


def num(s):
    return None if s in ("", None) else float(s)


def kind_of(r):
    ns = r["new_status"]
    if ns == "optimal":
        return "new optimum proven" if r["source"] == "this work" else "published optimum"
    if ns == "infeasible_bilevel":
        return "no bilevel feasible point"
    if ns == "feasible":
        return "first feasible point"
    if ns == "unchanged" and r["source"] == "this work":
        b, p = num(r["bobilib_value"]), num(r["primal_value"])
        check(b is not None and p < b - 1e-6 * max(1, abs(b)), f"{r['instance']}: not better than BOBILib")
        return "better feasible point"
    return None


def read_solu(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if ln.startswith("#") or not ln.strip():
                continue
            t = ln.split()
            out.setdefault(t[0], {})[t[1]] = t[2] if len(t) > 2 else None
    return out


def load_solution(rel):
    """rel relative to results/; 'ARCHIVE.tar.gz:MEMBER' names an archive member. Returns (bytes, json)."""
    if ":" in rel:
        arc, member = rel.split(":", 1)
        with tarfile.open(f"{R}/{arc}") as tf:
            data = tf.extractfile(member).read()
    else:
        with open(f"{R}/{rel}", "rb") as f:
            data = f.read()
    return data, json.loads(data)


def with_status(data, d, status):
    """The file's bytes with its top-level status set to `status` (only that field changes)."""
    if d["status"] == status:
        return data
    txt = data.decode("utf-8")
    pat = re.compile(r'^(\s*"status"\s*:\s*)"%s"' % re.escape(d["status"]), re.M)
    check(len(pat.findall(txt)) == 1, f"{d['name']}: status field not unique")
    new = pat.sub(lambda m: m.group(1) + json.dumps(status), txt).encode("utf-8")
    nd = json.loads(new)
    check(nd["status"] == status and {k: v for k, v in nd.items() if k != "status"} ==
          {k: v for k, v in d.items() if k != "status"}, f"{d['name']}: status rewrite changed other fields")
    return new


def reflow(md, width=100):
    """Re-wrap the Markdown's paragraphs and bullets (not headings, tables or code) to `width`."""
    out, para, fence = [], [], False

    def flush():
        if not para:
            return
        items = []
        for ln in para:
            if ln.startswith("* "):
                items.append(("* ", [ln[2:].strip()]))
            elif items and (items[-1][0] == "" or ln.startswith("  ")):
                items[-1][1].append(ln.strip())
            else:
                items.append(("", [ln.strip()]))
        for bullet, words in items:
            text = re.sub(r"`[^`]*`", lambda m: m.group(0).replace(" ", "\0"), " ".join(words))
            out.extend(ln.replace("\0", " ") for ln in
                       textwrap.wrap(text, width, initial_indent=bullet, subsequent_indent=" " * len(bullet),
                                     break_on_hyphens=False, break_long_words=False))
        para.clear()

    for ln in md.split("\n"):
        if ln.startswith("```"):
            flush()
            fence = not fence
            out.append(ln)
        elif fence or ln.startswith(("|", "#")) or not ln.strip():
            flush()
            out.append(ln)
        else:
            para.append(ln)
    flush()
    return "\n".join(out)


def main():
    make_tar = "--no-tar" not in sys.argv[1:]
    check(os.path.isdir(R) and os.path.isfile(f"{R}/instances.csv"), "run from bobilib/ (results/instances.csv)")
    rows = load_csv(f"{R}/instances.csv")
    check(len(rows) == 2654, "2,654 instances")
    orv = {r["name"]: r["variant"] for r in load_csv(f"{R}/or/compare.csv")}
    clq = {r["name"]: r for r in load_csv(f"{R}/clique/summary.csv")}
    ssp = {r["name"]: r for r in load_csv(f"{R}/ss/proofs.csv")}
    hpr = {r["name"]: r for r in load_csv(f"{R}/general/hpr_optimal.csv")}
    off = {}
    if os.path.exists(f"{R}/notes/official_checker.tsv"):
        off = {(r["folder"], r["name"]): r for r in load_csv(f"{R}/notes/official_checker.tsv", "\t")}
    solu = read_solu(f"{R}/bobilib_update.solu")
    tight = {(r["folder"], r["name"]): r for r in load_csv(f"{R}/notes/tight_verify.tsv", "\t")}

    out, solutions, certs = [], {}, set()
    status_rewritten = Counter()
    for r in rows:
        k = kind_of(r)
        if k is None:
            continue
        n, fam, cert = r["instance"], r["family"], r["certificate"]
        new_status = {"optimal": "optimal", "infeasible_bilevel": "infeasible"}.get(r["new_status"], "feasible")
        row = dict(instance=n, collection=r["collection"], family=fam, bobilib_status=r["bobilib_status"],
                   bobilib_value=r["bobilib_value"], new_status=new_status,
                   new_value=r["primal_value"] if new_status != "infeasible" else "", kind=k,
                   certificate_class=r["certificate_class"], solution_file="", official_checker="-",
                   certificate_files="", how_to_check="", supplement="", source=r["source"],
                   citation=CITATION[r["source"]], notes=r["notes"])
        # the solution file (a bilevel feasible point at new_value)
        if cert.endswith(".res.json"):
            check(r["verified"] == "yes", f"{n}: certificate not verified")
            data, d = load_solution(cert)
            check(d["name"] == n, f"{n}: name in file")
            fv, nv = float(d["objective_value"]), float(r["primal_value"])
            check(abs(fv - nv) <= 1e-9 * max(1, abs(nv)), f"{n}: file objective {fv} != {nv}")
            if d["status"] != new_status:
                status_rewritten[(k, d["status"])] += 1
            solutions[n] = with_status(data, d, new_status)
            row["solution_file"] = f"results/{cert}"
            folder = os.path.dirname(cert) if ":" not in cert else cert.split(":")[0]
            t = tight.get((folder, n))
            check(t is not None and t["class"] == "pass", f"{n}: bobi verify --tight ({folder})")
            o = off.get((folder, n))
            if off:
                check(o is not None, f"{n}: no row in notes/official_checker.tsv")
                check(o["verdict"] in ("pass", "skipped-license") and o["miplib"] == "pass",
                      f"{n}: official checker verdict {o['verdict']}")
                row["official_checker"] = ("pass" if o["verdict"] == "pass" else
                                           "MIPLIB step pass; Gurobi steps skipped (license size limit)")
        # what else the claim needs, and its class
        if k in ("first feasible point", "better feasible point"):
            row["check"] = "checker"
            row["how_to_check"] = "run BOBILib's feasibility checker on the solution file"
            row["supplement"] = SUPP["or"] if fam == "multidim-knapsack" else (
                SUPP["clique"] if fam == "clique" else SUPP["general"])
            if k == "better feasible point":  # instances.csv leaves the class na (status unchanged)
                check(r["certificate_class"] == "na", f"{n}: class of an unchanged row")
                if fam == "multidim-knapsack":
                    # one follower knapsack: integer data, exact knapsack oracle; several: HiGHS
                    row["certificate_class"] = "exact" if orv[n] == "100" else "numerical"
                else:
                    check(fam == "clique" and clq[n]["status"] != "optimal", f"{n}: unexpected better point")
                    row["certificate_class"] = "exact"  # follower optimum by the partition argument
        elif k == "published optimum":
            row["check"] = "citation"
            how = "optimality as published (not re-proved here)"
            row["supplement"] = SUPP["published"]
            if r["certificate_class"] == "exact":  # the two attack-protect optima, re-proved exactly here
                check(fam == "network" and r["source"] == "FischettiEtAl2017", f"{n}: exact published optimum")
                certs.update({"network/summary.csv", "network/review.tsv"})
                row["certificate_files"] = "results/network/summary.csv;results/network/review.tsv"
                how = ("optimality as published, and re-proved here: every attack enumerated, follower by exact "
                       "tree DP (bobi fire in the repository or, independently, checkers/network/fire_check enum)")
                row["supplement"] = SUPP["network"]
            elif n in hpr:  # the MIPLIB bound of the HPR: a verified point here confirms the published optimum
                h = hpr[n]
                certs.add("general/hpr_optimal.csv")
                row["certificate_files"] = "results/general/hpr_optimal.csv"
                bound = (f"the HPR equals MIPLIB's {h['miplib_instance']} (python3 -I checkers/compare_hpr.py "
                         f"INSTANCE.mps.gz INSTANCE.aux {h['miplib_instance']}.mps.gz), whose published optimum "
                         f"is {h['miplib_optimum']}")
                if r["verified"] == "yes":  # ex10_0_100: the solution file here is at the bound
                    how = f"optimality as published; confirmed here: {bound}"
                else:  # neos-950242_0_100: BOBILib's own point, not re-verified here
                    check(h["point_from"].startswith("BOBILib"), f"{n}: unverified point at the MIPLIB bound")
                    how = (f"optimality as published (not re-proved here); MIPLIB bound: {bound}; BOBILib's own "
                           f"solution file has that value (not re-verified here)")
            row["how_to_check"] = how + ("; the solution file attains it: run the checker" if row["solution_file"]
                                         else "" if n in hpr
                                         else "; no solution file here")
        elif k == "no bilevel feasible point":
            row["check"] = "certificate"
            check(cert.startswith("rays/") and r["certificate_class"] == "exact", f"{n}: ray")
            certs.add(cert)
            row["certificate_files"] = f"results/{cert}"
            row["how_to_check"] = "python3 -I checkers/verify_ray.py INSTANCE.mps.gz INSTANCE.aux " + \
                                  f"certificates/{cert} (exact rational check of a recession direction)"
            row["supplement"] = SUPP["ray"]
        else:  # new optimum proven: the point gives the upper bound, the certificate the lower bound
            row["check"] = "certificate"
            if fam == "knapsack":
                check(n in ssp, f"{n}: ss proof")
                certs.add("ss/proofs.csv")
                row["certificate_files"] = "results/ss/proofs.csv"
                row["how_to_check"] = (f"lower bound {ssp[n]['optimum']}: exhaustive search (bobi ss-solve) and, "
                                       f"independently, python3 -I checkers/ss_check.py INSTANCE.mps.gz "
                                       f"INSTANCE.aux - {ssp[n]['optimum']}")
                row["supplement"] = SUPP["ss"]
            elif fam == "clique":
                c = clq[n]
                certs.add("clique/summary.csv")
                if c["lb_argument"].startswith("Mantel"):
                    row["certificate_files"] = "results/clique/summary.csv"
                    row["how_to_check"] = (f"lower bound 3: {c['lb_argument']} (Mantel's theorem); upper bound: "
                                           f"the file's {c['ub_certificate']}")
                else:
                    cf = f"clique/certificates/{n}.cert.jsonl.gz"
                    check(os.path.exists(f"{R}/{cf}"), f"{n}: clique certificate")
                    certs.add(cf)
                    row["certificate_files"] = f"results/clique/summary.csv;results/{cf}"
                    row["how_to_check"] = ("lower bound 4: Brouwer (1981) Thm 2 and w3(G) > k, checked by "
                                           "python3 -I checkers/check_clique_certificates.py INSTANCE_DIR "
                                           f"certificates/clique/certificates {n}; upper bound: the file's "
                                           f"{c['ub_certificate']}")
                row["supplement"] = SUPP["clique"]
            elif fam == "network":
                certs.update({"network/summary.csv", "network/review.tsv"})
                row["certificate_files"] = "results/network/summary.csv;results/network/review.tsv"
                row["how_to_check"] = ("every attack enumerated, follower by exact tree DP: bobi fire "
                                       "(repository) or, independently, checkers/network/fire_check enum")
                row["supplement"] = SUPP["network"]
            else:
                h = hpr[n]
                certs.add("general/hpr_optimal.csv")
                row["certificate_files"] = "results/general/hpr_optimal.csv"
                row["how_to_check"] = (f"lower bound: the HPR equals MIPLIB's {h['miplib_instance']} "
                                       f"(python3 -I checkers/compare_hpr.py INSTANCE.mps.gz INSTANCE.aux "
                                       f"{h['miplib_instance']}.mps.gz), whose published optimum is "
                                       f"{h['miplib_optimum']}")
                if float(h["miplib_optimum"]) != float(h["optimum"]):
                    check(float(h["optimum"]) == int(float(h["optimum"])) and
                          float(h["optimum"]) - 1 < float(h["miplib_optimum"]) < float(h["optimum"]),
                          f"{n}: HPR bound rounding")
                    row["how_to_check"] += (f"; the objective takes integer values only, so the bound rounds up "
                                            f"to {h['optimum']}")
                if not row["solution_file"]:
                    row["how_to_check"] += "; the point is BOBILib's own solution file"
                    row["official_checker"] = "-"
                row["supplement"] = SUPP["hpr"]
        if not row["solution_file"]:
            row["solution_file"] = "-"
        row["certificate_files"] = row["certificate_files"] or "-"
        out.append(row)

    # ---- consistency with instances.csv, the .solu file and the paper ----------------------------
    kinds = Counter(r["kind"] for r in out)
    check(dict(kinds) == EXPECT, f"kind counts {dict(kinds)}")
    ns = Counter(r["new_status"] for r in rows)
    check(kinds["new optimum proven"] + kinds["published optimum"] == ns["optimal"], "optimal rows")
    check(kinds["no bilevel feasible point"] == ns["infeasible_bilevel"], "infeasible rows")
    check(kinds["first feasible point"] == ns["feasible"], "feasible rows")
    opt = {r["instance"]: r["new_value"] for r in out if r["new_status"] == "optimal"}
    inf = {r["instance"] for r in out if r["new_status"] == "infeasible"}
    best = {r["instance"]: r["new_value"] for r in out if r["new_status"] == "feasible"}
    check(solu.get("=opt=", {}) == opt, "=opt= lines of bobilib_update.solu")
    check(set(solu.get("=inf=", {})) == inf, "=inf= lines of bobilib_update.solu")
    check(solu.get("=best=", {}) == best, "=best= lines of bobilib_update.solu")
    check((len(opt), len(inf), len(best)) == (610, 40, 693), "solu counts")
    for r in out:
        b = num(r["bobilib_value"])
        if r["new_status"] in ("optimal", "feasible") and b is not None:
            v = float(r["new_value"])
            check(v <= b + 1e-6 * max(1, abs(b)), f"{r['instance']}: new value above BOBILib's")
    classes = Counter((r["kind"], r["certificate_class"]) for r in out)
    check(all(c in ("exact", "numerical") for _, c in classes), f"classes {classes}")
    check(Counter(r["certificate_class"] for r in rows if r["certificate_class"] != "na") ==
          Counter(r["certificate_class"] for r in out if r["kind"] != "better feasible point"),
          "certificate classes agree with instances.csv")
    n_files = sum(r["solution_file"] != "-" for r in out)
    check(n_files == len(solutions), "one solution file per row with a file")
    offc = Counter(r["official_checker"] for r in out if r["solution_file"] != "-")
    first_anywhere = sum("first point anywhere" in r["notes"] for r in out if r["kind"] == "first feasible point")
    pub_elsewhere = sum("published point" in r["notes"] for r in out if r["kind"] == "first feasible point")
    check(first_anywhere + pub_elsewhere == kinds["first feasible point"], "first points: anywhere or published")
    already = sum("BOBILib value already optimal" in r["notes"] for r in out if r["new_status"] == "optimal")
    nofile_pub = sum(r["solution_file"] == "-" for r in out if r["kind"] == "published optimum")
    bestdual = solu.get("=bestdual=", {})

    os.makedirs(OUT, exist_ok=True)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(out)
    csv_bytes = buf.getvalue().encode("utf-8")
    with open(f"{R}/bobilib_update.solu", "rb") as f:
        solu_bytes = f.read()

    # ---- README ---------------------------------------------------------------------------------
    by = lambda k: [r for r in out if r["kind"] == k]  # noqa: E731
    before = {k: Counter(r["bobilib_status"] for r in by(k)) for k in KINDS}

    def fmt_before(k):
        return ", ".join(f"{v} {s}" for s, v in sorted(before[k].items()))

    def cls(k):
        c = Counter(r["certificate_class"] for r in by(k))
        return ", ".join(f"{v} {s}" for s, v in sorted(c.items()))

    newopt = Counter()
    for r in by("new optimum proven"):
        newopt[{"knapsack": "ss", "clique": "clique", "network": "network"}.get(r["family"], "hpr")] += 1
    check(newopt["network"] == 0, "the attack-protect optima are published (Fischetti et al. 2017)")
    pub_exact = [r for r in by("published optimum") if r["certificate_class"] == "exact"]
    pub_hpr = [r for r in by("published optimum") if r["instance"] in hpr]
    check(len(pub_exact) == 2 and sorted(r["instance"] for r in pub_hpr) == ["ex10_0_100", "neos-950242_0_100"],
          "published optima re-proved or confirmed here")
    ver = {r["instance"]: r["verified"] for r in rows}  # instances.csv
    pub_hpr_conf = [r["instance"] for r in pub_hpr if ver[r["instance"]] == "yes"]  # a verified point here at the bound
    pub_hpr_bob = [r["instance"] for r in pub_hpr if ver[r["instance"]] != "yes"]   # BOBILib's point, not re-verified
    check(pub_hpr_conf == ["ex10_0_100"] and pub_hpr_bob == ["neos-950242_0_100"], "MIPLIB-bound published optima")
    clique_brouwer = sum("Brouwer" in r["how_to_check"] for r in by("new optimum proven"))
    pub_src = Counter(r["source"] for r in by("published optimum"))
    kip_pub = sum(r["family"] == "knapsack" for r in by("published optimum"))
    kip_earlier = sum("proved optimal earlier, value not listed" in r["notes"] for r in by("published optimum"))
    check(kip_pub == 376 and kip_earlier == 266 and pub_src["WeningerFukasawa2022Code"] == 336
          and pub_src["FischettiEtAl2016Report"] == 78 and pub_src["CapraraEtAl2016"] == 14, "KIP first publications")
    imkp_pub = [r for r in by("published optimum") if r["collection"] == "imkp"]
    check(len(imkp_pub) == 52 and all(r["source"] == "FischettiEtAl2016Report" for r in imkp_pub)
          and "FischettiEtAl2019" not in pub_src, "imkp first publications")
    n_pass = offc.get("pass", 0)
    n_skip = sum(v for k, v in offc.items() if k.startswith("MIPLIB"))
    n_hpr_bob = sum(r["solution_file"] == "-" for r in by("new optimum proven"))
    rewritten = sum(status_rewritten.values())
    plural = {"new optimum proven": "new optima", "published optimum": "published optima"}
    rewritten_text = "the repository's files of " + " and ".join(
        f"{v} {plural[k]}" for (k, a), v in sorted(status_rewritten.items(), key=lambda t: -t[1])) + \
        " say `" + "`/`".join(sorted({a for (_, a) in status_rewritten})) + "`"
    snapshot_text = (f"BOBILib's metadata (`collection.json`, sha256 `{META_SHA256[:16]}...`) as downloaded on "
                     f"{SNAPSHOT}, its instance files, and its feasibility checker (`feasibility-checker.tar.gz` "
                     f"from bobilib.org, sha256 `{CHECKER_SHA256[:16]}...`).")
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as f:
            head = "".join(ln for ln in f if ln.startswith("#"))
        mc = re.search(r"commit ([0-9a-f]{40}) \((\d{4}-\d\d-\d\d)\)", head)
        ml = re.search(r"Last-Modified (\d{4}-\d\d-\d\d)", head)
        check(mc is not None and META_SHA256 in open(MANIFEST, encoding="utf-8").read(), "snapshot manifest")
        snapshot_text = (f"BOBILib's metadata (`collection.json`" + (f", Last-Modified {ml.group(1)}" if ml else "") +
                         f", downloaded {SNAPSHOT}, sha256 `{META_SHA256[:16]}...`), the instance and solution files "
                         f"of bobilib-data commit `{mc.group(1)[:12]}` ({mc.group(2)}), listed file by file with "
                         f"their sha256 in `{MANIFEST}`, and BOBILib's feasibility checker "
                         f"(`feasibility-checker.tar.gz` from bobilib.org, sha256 `{CHECKER_SHA256[:16]}...`).")
    readme = f"""# BOBILib status update: submission

From Brian J. Connolly (Beehive Industries, brian.connolly@beehiveind.com), with the paper
"{TITLE}" (preprint, 2026). Repository: {REPO}; paths that start with
`results/`, `scripts/`, `paper/` or `data-manifest/` are relative to its root (the paper's supplement is
`paper/appendix/appendix.pdf`), the others to the archive `bobilib_submission.tar.gz`.

Reference: {snapshot_text}

## What changes

{len(out):,} instances change status or best known value relative to that metadata
(`status_changes.csv`, one row each; the same in MIPLIB/SCIP form in `bobilib_update.solu`):

| Kind | Instances | BOBILib now | New status | Check | Certificate class |
| --- | ---: | --- | --- | --- | --- |
| new optimum proven | {kinds['new optimum proven']} | {fmt_before('new optimum proven')} | optimal | certificate | {cls('new optimum proven')} |
| published optimum | {kinds['published optimum']} | {fmt_before('published optimum')} | optimal | citation | {cls('published optimum')} |
| no bilevel feasible point | {kinds['no bilevel feasible point']} | {fmt_before('no bilevel feasible point')} | infeasible | certificate | {cls('no bilevel feasible point')} |
| first feasible point | {kinds['first feasible point']} | {fmt_before('first feasible point')} | feasible | checker | {cls('first feasible point')} |
| better feasible point | {kinds['better feasible point']} | {fmt_before('better feasible point')} | feasible (value improves) | checker | {cls('better feasible point')} |

* New optima: {newopt['ss']} subset-sum knapsack interdiction, {newopt['clique']} clique interdiction
  and {newopt['hpr']} general instances whose HPR is a MIPLIB model with a published optimum. For
  {already} of the {kinds['new optimum proven'] + kinds['published optimum']} optima BOBILib's value was
  already optimal and only the status changes.
* Published optima: {', '.join(f'{v} {SHORT[k]}' for k, v in pub_src.most_common())} (full references in
  `status_changes.csv`, column `citation`), each credited to its first publication among the sources
  we compiled (later proofs are named in `notes`). For the {kip_pub} knapsack interdiction optima,
  `results/literature/kip_first_publication.csv` names the table or answer file of each first
  publication; for {kip_earlier} of them Della Croce and Scatamacchia (2020) had reported the
  instance's group solved, without values. The {len(imkp_pub)} `imkp` optima are first published in
  Tables 4-6 of Fischetti et al.'s technical report of 2016
  (`results/literature/imkp_first_publication.csv`). For {nofile_pub} of the {kinds['published optimum']} published
  optima there is no solution file here; only the published value is used. The {len(pub_exact)} attack-protect games (`inter-fire`)
  {' and '.join(r['instance'] for r in pub_exact)}, which Fischetti et al.'s MIX++ solved (online
  appendix of their 2017 paper, Table 9), are re-proved here exactly by enumeration (class `exact`).
  ex10_0_100 is optimal in Lefebvre and Schmidt's run file `results-MILP.csv` (a run that ended
  before the time limit with value equal to bound; their paper does not name the instance); it is
  credited to them, and the MIPLIB bound of its HPR with the solution file here confirms it.
* First feasible points: BOBILib lists no point; for {first_anywhere} it is the first point anywhere, for
  the other {pub_elsewhere} a published point existed (named in `notes`).
* `bobilib_update.solu` also has {len(bestdual)} `=bestdual=` lines (proven lower bounds better than any
  published: OR instances with one follower knapsack and the 3 open clique instances). BOBILib's
  metadata has no field for them; they are not rows of `status_changes.csv`.

## Easy to check: the feasible points (column `check` = `checker`)

`solutions/` holds {len(solutions):,} solution files in BOBILib's format (`<instance>.res.json`), one for
every row with a `solution_file`: the {kinds['first feasible point']} first and {kinds['better feasible point']}
better points, and the points at the new and published optima (the {nofile_pub} published optima without a
file and the {n_hpr_bob} optima at BOBILib's own point need none). Each one is checked by your feasibility
checker alone. We ran it (Gurobi {GUROBI_VERSION}, pip's size-limited license, default tolerances;
`notes/official_checker.md`): **{n_pass:,} pass** all three steps (HPR, MIPLIB solution checker, follower
optimal with the leader fixed), and the optimistic tie-break check too; the other **{n_skip}** exceed
the license's 2,000 variables or rows, so only the solver-free MIPLIB step ran, and it passed. All
{len(solutions):,} also pass this repository's `bobi verify --tight` (follower within max(1e-6, 1e-9 |phi|)
of its proven optimum; `notes/tight_verify.md`). No file fails any check. With a full Gurobi license
the solver steps would also run on the {n_skip} large ones.

Each file's `status` is the new status. {rewritten} files differ from the repository's copy in that
field only: {rewritten_text}, the status under which the point was found. Everything else is byte for
byte the same.

## Needs more: optimality and infeasibility (column `check` = `certificate` or `citation`)

A point only gives an upper bound. The lower bound or the infeasibility proof is:

| Claim | Instances | Certificate (in `certificates/`, same path as under `results/`) | How to check | Supplement section |
| --- | ---: | --- | --- | --- |
| subset-sum knapsack interdiction optimum | {newopt['ss']} | `ss/proofs.csv` | exhaustive search (`bobi ss-solve`); independent prover `checkers/ss_check.py` | {SUPP['ss']} |
| clique interdiction optimum, value 3 | {newopt['clique'] - clique_brouwer} | `clique/summary.csv` | Mantel's theorem: m - k > floor(n^2/4) (arithmetic) | {SUPP['clique']} |
| clique interdiction optimum, value 4 | {clique_brouwer} | `clique/certificates/*.cert.jsonl.gz` | Brouwer (1981) Thm 2 plus w3(G) > k, `checkers/check_clique_certificates.py` (integer arithmetic) | {SUPP['clique']} |
| attack-protect optimum (published, re-proved here) | {len(pub_exact)} | `network/summary.csv`, `network/review.tsv` | every attack enumerated, 2,138,410 per instance (`bobi fire`; independently `checkers/network/fire_check.c`) | {SUPP['network']} |
| optimum at the MIPLIB bound of the HPR | {newopt['hpr']} | `general/hpr_optimal.csv` | `checkers/compare_hpr.py` (HPR = MIPLIB model) and MIPLIB's published optimum | {SUPP['hpr']} |
| no bilevel feasible point | {kinds['no bilevel feasible point']} | `rays/*.ray.json` | `checkers/verify_ray.py`: exact rational check of a recession direction of the follower | {SUPP['ray']} |
| published optimum | {kinds['published optimum']} | (the cited paper) | as published; apart from the {len(pub_exact)} above not re-proved here ({' and '.join(pub_hpr_conf)} is confirmed by the MIPLIB bound with a verified point, `general/hpr_optimal.csv`; BOBILib's point of {' and '.join(pub_hpr_bob)}, not re-verified here, meets that bound too) | {SUPP['published']} |

The upper bound of each new optimum is its solution file (in the clique files the leader deletes
exactly the edges inside the parts of a partition, so the follower's clique number is at most the
number of parts).
For {n_hpr_bob} of the HPR-bound optima the point is BOBILib's own solution file, so there is no file here.
The supplement has the proofs; `lean/` in the repository formalises the knapsack interdiction lemmas.

## Certificate classes (column `certificate_class`)

* `exact`: checked in exact rational or integer arithmetic, or a proof plus an exhaustive integer
  computation; no tolerance enters. The {len(pub_exact)} published attack-protect optima are in this class
  because of their re-proof here; all other published optima are `numerical`.
* `numerical`: rests on a floating-point LP/MILP solver run with tolerances (rows within 1e-6, follower
  optimum by HiGHS within max(1e-6, 1e-9 |phi|)), or on a published optimum used as published, or on
  MIPLIB's published floating-point optimum.
* `benchmark` (a point accepted only because of the checker's 1e-4 tolerances): none here. The
  repository keeps 25 superseded points of this class in `results/*/tolerance/`; the four of them
  that fit Gurobi's free license pass your checker (`notes/official_checker.md`).

For the {kinds['better feasible point']} better points, `results/instances.csv` gives no class (the status does not
change); here the class of the point follows the same rules: OR points with one follower knapsack
are `exact` (integer data, exact knapsack oracle), with several `numerical`, and the 3 clique points
`exact` (partition argument).

## Contents of `bobilib_submission.tar.gz`

```
bobilib_submission/
  README.md              this file
  status_changes.csv     one row per change: instance, BOBILib's status and value, new status and value,
                         kind, check, certificate class, solution and certificate files (repository
                         paths), official checker result, how to check, supplement section, citation, notes
  bobilib_update.solu    the same changes in MIPLIB/SCIP .solu form (plus =bestdual= lower bounds)
  solutions/             {len(solutions):,} solution files in BOBILib's format
  certificates/          the certificates and tables named in status_changes.csv, with their READMEs
  checkers/              the stand-alone checkers named above (Python 3; ss_check.py needs numpy; fire_check.c
                         is C) and run_official_checker.py, which runs your checker over solutions/
  notes/                 our runs of your checker and of bobi verify --tight, per file
  snapshot/              the BOBILib snapshot used: every instance and solution file with its sha256
  LICENSE-data, LICENSE-code, SHA256SUMS
```

To run your checker over all files (it calls `./miplib2017-testscript-v1.0.3/checker/bin/solchecker`):

```sh
python3 -I checkers/run_official_checker.py --checker feasibility-checker --python python3 \\
    --solchecker miplib2017-testscript-v1.0.3 --collection collection --work work \\
    --out official.tsv --tight '' all=solutions
```

## License

Solution files, certificates and tables: CC BY 4.0 (`LICENSE-data`), which allows BOBILib to
redistribute them under its CC BY-SA 4.0. Checkers: MIT (`LICENSE-code`). Please cite the paper above.
"""
    readme_bytes = reflow(readme).encode("utf-8")
    for path, data in (("status_changes.csv", csv_bytes), ("bobilib_update.solu", solu_bytes),
                       ("README.md", readme_bytes)):
        with open(f"{OUT}/{path}", "wb") as f:
            f.write(data)

    print(f"status_changes.csv: {len(out)} rows; " + ", ".join(f"{k} {kinds[k]}" for k in KINDS))
    print(f"solution files: {len(solutions)} (status field rewritten in {rewritten}); "
          f"certificates: {len(certs)}; official checker: {dict(offc)}")
    if not make_tar:
        return

    # ---- the archive ----------------------------------------------------------------------------
    members = {"README.md": readme_bytes, "status_changes.csv": csv_bytes, "bobilib_update.solu": solu_bytes}
    for n, data in solutions.items():
        members[f"solutions/{n}.res.json"] = data
    for rel in sorted(certs | {d for d in DOCS if d.startswith(("ss/", "clique/", "network/", "rays/",
                                                                   "general/", "general-coupled/", "or/",
                                                                   "kip/"))}):
        with open(f"{R}/{rel}", "rb") as f:
            members[f"certificates/{rel}"] = f.read()
    for rel in DOCS:
        if rel.startswith("notes/"):
            if os.path.exists(f"{R}/{rel}"):
                with open(f"{R}/{rel}", "rb") as f:
                    members[rel] = f.read()
    for dst, src in CHECKERS.items():
        with open(src, "rb") as f:
            members[dst] = f.read()
    if os.path.exists(MANIFEST):
        with open(MANIFEST, "rb") as f:
            members["snapshot/bobilib_snapshot.tsv"] = f.read()
    with open(f"{R}/LICENSE", "rb") as f:
        members["LICENSE-data"] = f.read()
    with open("LICENSE", "rb") as f:
        members["LICENSE-code"] = f.read()
    members["SHA256SUMS"] = "".join(f"{hashlib.sha256(members[p]).hexdigest()}  {p}\n"
                                    for p in sorted(members)).encode("utf-8")
    raw = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tf:
            dirs = sorted({os.path.dirname(p) for p in members} - {""})
            alld = set()
            for d in dirs:
                parts = d.split("/")
                alld.update("/".join(parts[:i + 1]) for i in range(len(parts)))
            for d in [""] + sorted(alld):
                ti = tarfile.TarInfo(f"{PREFIX}/{d}".rstrip("/"))
                ti.type, ti.mode, ti.mtime = tarfile.DIRTYPE, 0o755, EPOCH
                tf.addfile(ti)
            for p in sorted(members):
                ti = tarfile.TarInfo(f"{PREFIX}/{p}")
                ti.size, ti.mode, ti.mtime = len(members[p]), 0o644, EPOCH
                tf.addfile(ti, io.BytesIO(members[p]))
    with open(TAR, "wb") as f:
        f.write(raw.getvalue())
    print(f"{TAR}: {len(members)} files, {len(raw.getvalue()):,} bytes, "
          f"sha256 {hashlib.sha256(raw.getvalue()).hexdigest()}")


GUROBI_VERSION = "13.0.3"

if __name__ == "__main__":
    main()
