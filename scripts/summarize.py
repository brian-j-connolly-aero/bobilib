"""Summarise the state of every BOBILib instance that BOBILib itself does not
list as optimal: what the literature already settles, what this work adds,
and what remains open. Writes results/summary.json and prints a table.

usage: python3 -I summarize.py --meta collection.json --mkip-lit mkip_literature_status.csv
           --runs runs --results results [--miblp-lit miblp_literature_status.csv]
           [--lbc-optimal optimal.csv] [--other-lit other_published_optima.csv]
           [--kip-lit kip_first_publication.csv] [--imkp-lit imkp_first_publication.csv]

Each published optimum is credited to its first publication: for the KIP
instances, the source named in results/literature/kip_first_publication.csv
(the default of --kip-lit; column `first_source`, KIP_FIRST below); for the
imkp instances, the one named in results/literature/imkp_first_publication.csv
(the default of --imkp-lit; Fischetti et al.'s technical report of 2016); for the
general instances, the earliest source of miblp_literature_status.csv whose
upper and lower bounds agree (column `sources`), ranked by the date of its first
public version (FIRST_PUBLIC below); results/literature/other_published_optima.csv
(the default of --other-lit) holds the published optima that no other table
has (two network instances and ex10_0_100).

Inputs (all optional except --meta; missing ones are skipped):
  results/kip/summary.csv         published KIP optima (files rebuilt from Weninger and Fukasawa's runs)
  results/literature/kip_first_publication.csv  first publication of each of these optima (required
                                   when kip/summary.csv lists a published optimum BOBILib does not)
  results/literature/imkp_first_publication.csv first publication of the imkp optima of --mkip-lit
                                   (required with --mkip-lit)
  results/literature/other_published_optima.csv  further published optima (network, ex10_0_100)
  results/ss/proofs.csv            our subset-sum optima (bobi ss-solve, verified files)
  runs/ss_*.tsv                    further local subset-sum runs (bobi ss-solve)
  results/or/compare.csv           OR bounds vs literature (scripts/compare_or.py; runs/or_compare.csv
                                   if the package copy is missing)
  results/clique/summary.csv      clique interdiction certificates
  results/network/summary.csv     attack-protect certificates (bobi fire)
  results/general/hpr_optimal.csv general points meeting the HPR bound
  runs/general.jsonl               general feasible points (bobi general)
  results/general-coupled/summary.csv  feasible points with coupling rows (bobi coupled)
  results/rays/ray_verify.jsonl    exact unbounded-follower certificates (runs/ray_verify.jsonl if the
                                   package copy is missing)
"""
import argparse
import collections
import csv
import glob
import json
import os
import re


def load_csv(path):
    return list(csv.DictReader(open(path))) if os.path.exists(path) else []


# Sources of miblp_literature_status.csv (prefix of each entry of its column `sources`), in the order of
# their first public version: Fischetti et al., Operations Research 65(6), 2017 (MIX++; its Table 6 with
# the more aggressive setting); Lozano, Bergman and Cire, arXiv 2407.18193 of 25 July 2024 (Operations
# Research 2026; its Table 2 already closes p0282-0.9); Vasquez, Lozano and van Hoeve, Mathematical
# Programming 2025 (it cites that preprint). An earlier BOBILib release counts only where no paper
# proves the optimum.
FIRST_PUBLIC = [("F17", "Fischetti et al. 2017"), ("LBC", "Lozano et al. 2026"), ("VLH", "Vasquez et al. 2025"),
                ("BOBILib", "an earlier BOBILib release")]
# First publications of the KIP optima (results/literature/kip_first_publication.csv, column first_source):
# Caprara, Carvalho, Lodi and Woeginger, INFORMS J. Comput. 28(2), 2016 (cclw); Fischetti, Ljubić, Monaci and
# Sinnl's technical report of 2016, the preprint of their 2019 paper (inter-kp and cclw 55-3); the answer files
# of Weninger and Fukasawa's bkpsolver repository, public by 7 October 2022 (kp). The same report of Fischetti et
# al. is the first publication of the imkp optima (results/literature/imkp_first_publication.csv, Tables 4-6).
KIP_FIRST = {"CapraraEtAl2016": "Caprara et al. 2016", "FischettiEtAl2016Report": "Fischetti et al. 2016, technical report",
             "WeningerFukasawa2022Code": "Weninger-Fukasawa 2022, answer files"}


def proving_sources(sources):
    """Prefixes (F17, LBC, VLH, BOBILib) of the entries of `sources` whose ub equals their lb, earliest first."""
    found = set()
    for entry in sources.split("; "):
        key, _, rest = entry.partition(":")
        m = re.match(r"ub=([^,]*),lb=([^,]*)", rest)
        try:
            ub, lb = float(m.group(1)), float(m.group(2))
        except (AttributeError, ValueError):
            continue
        if abs(ub - lb) <= 1e-6 * max(1.0, abs(ub)):
            found.add(key.split("-")[0])
    return [k for k, _ in FIRST_PUBLIC if k in found]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", required=True)
    ap.add_argument("--mkip-lit")
    ap.add_argument("--miblp-lit")
    ap.add_argument("--lbc-optimal", help="solution_files/optimal.csv from Lozano et al.'s repository")
    ap.add_argument("--other-lit", help="default: RESULTS/literature/other_published_optima.csv")
    ap.add_argument("--kip-lit", help="default: RESULTS/literature/kip_first_publication.csv")
    ap.add_argument("--imkp-lit", help="default: RESULTS/literature/imkp_first_publication.csv")
    ap.add_argument("--runs", default="runs")
    ap.add_argument("--results", default="results")
    a = ap.parse_args()
    a.other_lit = a.other_lit or f"{a.results}/literature/other_published_optima.csv"
    a.kip_lit = a.kip_lit or f"{a.results}/literature/kip_first_publication.csv"
    a.imkp_lit = a.imkp_lit or f"{a.results}/literature/imkp_first_publication.csv"
    meta = json.load(open(a.meta))

    def family(v):
        if v["Class"] == "interdiction":
            return {"knapsack": "knapsack", "multidimensional knapsack": "multidim-knapsack", "edge clique": "clique",
                    "generalized": "generalized", "network": "network", "assignment": "assignment"}[v["Type"]]
        return "general-" + ("mixed" if v["Class"] == "mixed integer" else "pure")

    status = {}  # name -> (bobilib, outcome, source)
    for k, v in meta.items():
        status[k] = {"family": family(v), "bobilib": v["Status"], "outcome": None, "source": None}

    # Literature: KIP and imkp optima (each credited to its first publication), OR optima (Lozano et al.).
    kip_first = {r["instance"]: r for r in load_csv(a.kip_lit)}
    kip_lit = set()
    for r in load_csv(f"{a.results}/kip/summary.csv"):
        n = r["name"]
        if r.get("literature_optimum") not in ("", None) and n in status and status[n]["bobilib"] != "optimal":
            f = kip_first.get(n)
            assert f is not None, f"{n}: published KIP optimum without a row in {a.kip_lit}"
            assert float(f["first_value"]) == float(r["literature_optimum"]), f"{n}: first_value != literature_optimum"
            status[n].update(outcome="optimal", source=f"literature ({KIP_FIRST[f['first_source']]})")
            kip_lit.add(n)
    assert kip_lit == set(kip_first), f"{a.kip_lit} lists other instances than the published KIP optima"
    if a.mkip_lit:
        imkp_first = {r["instance"]: r for r in load_csv(a.imkp_lit)}
        imkp_lit = set()
        for r in load_csv(a.mkip_lit):
            n = r["name"]
            if n in status and status[n]["bobilib"] != "optimal" and r.get("proven_optimal_in_literature") == "True":
                if r.get("set") == "imkp":
                    f = imkp_first.get(n)
                    assert f is not None, f"{n}: published imkp optimum without a row in {a.imkp_lit}"
                    assert float(f["first_value"]) == float(r["flms2019_opt"]), f"{n}: first_value != flms2019_opt"
                    src = f"literature ({KIP_FIRST[f['first_source']]})"
                    imkp_lit.add(n)
                else:
                    src = "literature (Lozano et al. 2026)"
                status[n].update(outcome="optimal", source=src)
        assert imkp_lit == set(imkp_first), f"{a.imkp_lit} lists other instances than the published imkp optima"
    if a.miblp_lit:
        # General instances: the first publication among the sources that prove the optimum.
        for r in load_csv(a.miblp_lit):
            n = r["instance"]
            if n in status and status[n]["bobilib"] != "optimal" and status[n]["outcome"] is None and r["closed_in_literature"] == "True":
                first = proving_sources(r["sources"])
                assert first, f"{n}: closed in the literature, but no source with ub = lb"
                status[n].update(outcome="optimal", source=f"literature ({dict(FIRST_PUBLIC)[first[0]]})")
    if a.lbc_optimal:
        # Lozano, Bergman and Cire's optimal solution files (decision diagrams), any family.
        for r in load_csv(a.lbc_optimal):
            n = re.sub(r"(\.dd_\d+)?[-.]res\.json$", "", re.sub(r"^dd_", "", r["name"]))
            if n in status and status[n]["bobilib"] != "optimal" and status[n]["outcome"] is None:
                status[n].update(outcome="optimal", source="literature (Lozano et al. 2026)")
    # Published optima that no other table holds (network: Fischetti et al.'s online appendix; ex10_0_100:
    # Lefebvre and Schmidt's run file).
    for r in load_csv(a.other_lit):
        n = r["instance"]
        if n in status and status[n]["bobilib"] != "optimal" and status[n]["outcome"] is None:
            status[n].update(outcome="optimal", source=f"literature ({r['source']})")
    # This work: subset-sum optima (committed proofs, then local runs).
    for r in load_csv(f"{a.results}/ss/proofs.csv"):
        n = r["name"]
        if n in status and status[n]["outcome"] is None:
            status[n].update(outcome="optimal", source="this work (robust subset-sum search)")
    for p in glob.glob(f"{a.runs}/ss_*.tsv"):
        for line in open(p):
            t = line.rstrip("\n").split("\t")
            if len(t) >= 3 and t[1] == "OPTIMAL" and t[0] in status and status[t[0]]["outcome"] is None:
                status[t[0]].update(outcome="optimal", source="this work (robust subset-sum search)")
    # This work: OR closures and first points.
    p = f"{a.results}/or/compare.csv"
    for r in load_csv(p if os.path.exists(p) else f"{a.runs}/or_compare.csv"):
        n = r["name"]
        if n not in status or status[n]["outcome"]:
            continue
        f = lambda s: float(s) if s not in ("", None, "None") else None
        point, lb = f(r["our_point"]), f(r["best_lb"])
        if point is not None and lb is not None and point <= lb + 1e-6:
            status[n].update(outcome="optimal", source="this work (certified point meets best lower bound)")
        elif point is not None and status[n]["bobilib"] == "open":
            status[n].update(outcome="feasible", source="this work (first certified point)" if f(r["lit_ub"]) is None else "this work (certified point)")
    # This work: clique certificates.
    for r in load_csv(f"{a.results}/clique/summary.csv"):
        if r.get("status") == "optimal" and r["name"] in status and status[r["name"]]["outcome"] is None:
            status[r["name"]].update(outcome="optimal", source="this work (Mantel/Brouwer + partitions)")
    # This work: attack-protect trees certified by enumeration and a tree dynamic program.
    for r in load_csv(f"{a.results}/network/summary.csv"):
        if r.get("certified") == "true" and r["name"] in status and status[r["name"]]["outcome"] is None:
            status[r["name"]].update(outcome="optimal", source="this work (every attack, follower by tree DP)")
    # This work: unbounded followers (no bilevel feasible point).
    p = f"{a.results}/rays/ray_verify.jsonl"
    if not os.path.exists(p):
        p = f"{a.runs}/ray_verify.jsonl"
    if os.path.exists(p):
        for line in open(p):
            if not line.startswith("{"):
                continue
            d = json.loads(line)
            n = d["instance"].replace(".mps.gz", "")
            # A later exact check (after repair) upgrades an earlier floating one.
            if n in status and status[n]["bobilib"] == "open" and (d["verified"] or status[n]["outcome"] is None):
                status[n].update(outcome="no bilevel feasible point",
                                 source="this work (recession ray, exact)" if d["verified"] else "this work (recession ray, floating point)")
    # This work: general points meeting the HPR (MIPLIB) bound.
    for r in load_csv(f"{a.results}/general/hpr_optimal.csv"):
        if r["name"] in status and status[r["name"]]["outcome"] is None:
            status[r["name"]].update(outcome="optimal", source="this work (point meets the MIPLIB optimum of the HPR)")
    # This work: general feasible points.
    p = f"{a.runs}/general.jsonl"
    if os.path.exists(p):
        for line in open(p):
            if not line.startswith("{"):
                continue
            d = json.loads(line)
            n = d.get("name")
            if n in status and status[n]["outcome"] is None and d.get("verified") and status[n]["bobilib"] == "open":
                status[n].update(outcome="feasible", source="this work (HPR, follower, tie-break)")
    # This work: general feasible points with coupling rows (verified files).
    for r in load_csv(f"{a.results}/general-coupled/summary.csv"):
        n = r["name"]
        if n in status and status[n]["outcome"] is None and r["status"] == "point" and status[n]["bobilib"] == "open":
            status[n].update(outcome="feasible", source="this work (bobi coupled)")

    rows = collections.defaultdict(collections.Counter)
    for n, s in status.items():
        if s["bobilib"] == "optimal":
            continue
        rows[s["family"]]["not optimal in BOBILib"] += 1
        key = (s["outcome"] or "unchanged") + (" / " + s["source"] if s["source"] else "")
        rows[s["family"]][key] += 1
    os.makedirs(a.results, exist_ok=True)
    json.dump({"per_instance": status, "per_family": {k: dict(v) for k, v in rows.items()}}, open(f"{a.results}/summary.json", "w"), indent=1)
    for fam in sorted(rows):
        print(f"== {fam}")
        for k, v in sorted(rows[fam].items(), key=lambda kv: -kv[1]):
            print(f"   {v:5d}  {k}")


if __name__ == "__main__":
    main()
