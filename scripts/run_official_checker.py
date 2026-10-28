"""Run BOBILib's official feasibility checker on every solution file of the
data package and write results/notes/official_checker.tsv.

usage (from bobilib/):
  python3 -I scripts/run_official_checker.py --checker CHECKER_DIR --python GUROBI_PYTHON \
      --solchecker MIPLIB_TESTSCRIPT_DIR --collection data/collection --work WORK_DIR \
      --out results/notes/official_checker.tsv [--tight results/notes/tight_verify.tsv] \
      [-j 2] [--timeout 3600] FOLDER=DIR ...

CHECKER_DIR is BOBILib's feasibility-checker folder (feasibility_checker.py,
name_based_bilevel_parser/); GUROBI_PYTHON a Python with gurobipy; and
MIPLIB_TESTSCRIPT_DIR the unpacked miplib2017-testscript-v1.0.3 with
checker/bin/solchecker built. The checker calls
./miplib2017-testscript-v1.0.3/checker/bin/solchecker relative to the
current directory, so each file is checked in WORK_DIR, which gets a link
of that name. FOLDER is the label written in the table (e.g. kip); DIR holds
the *.res.json files (for general/large_points.tar.gz, a directory it was
extracted to).

Each file runs in its own process, as in run_feasibility_checker_website.py
and with the checker's own default tolerances:
  1. hpr_infeasibility_checker()                    (Gurobi: the HPR has a point)
  2. validate_cons_feasibility_miplib2017_checker() (MIPLIB 2017 solution checker:
                                                     integrality, rows, bounds, objective)
  3. validate_bilevel_feasibility()                 (Gurobi: the follower with the leader
                                                     fixed, relative gap 1e-4)
and, as an extra column, check_optimistic_bilevel_feasible_point() (the
leader's best value over the follower's optima at the file's leader values
equals the file's value). The verdict is pass if 1-3 pass. The columns
bobi_verify and bobi_verify_tight give the file's verdict in --tight's table
(`bobi verify` at BOBILib's tolerances passes `pass` and `benchmark-accepted`
files; --tight only `pass`), and agree compares the verdict with bobi_verify.
Per-file results are kept in WORK/official.jsonl and reused on a re-run
(delete it after changing a solution file).

Gurobi's pip license is size-limited (2,000 variables and 2,000 rows); a
larger model cannot run steps 1 and 3 and is `skipped-license`. Step 2 needs
no solver and is still run for it (for models over 150,000 variables
without the bilevel parser, whose name lookups are quadratic and which
step 2 does not use).
"""
import argparse
import concurrent.futures as cf
import contextlib
import csv
import io
import json
import os
import re
import subprocess
import sys
import time

LIMIT_VARS = 2000
LIMIT_CONS = 2000
PARSER_MAX_VARS = 150000
LINK = "miplib2017-testscript-v1.0.3"

COLS = ["folder", "name", "verdict", "hpr", "miplib", "bilevel", "optimistic", "miplib_check",
        "miplib_max_violation", "nvars", "ncons", "file_status", "file_objective", "seconds",
        "bobi_verify", "bobi_verify_tight", "agree", "note"]


# ---------------------------------------------------------------------------------------------
# one file (runs under the Gurobi Python)
# ---------------------------------------------------------------------------------------------
def miplib_log(res, outdir, mps):
    name = os.path.basename(mps).split(".mps")[0]
    log = os.path.join(outdir, name + "_MIPLIB_SOLChecker.log")
    if os.path.exists(log):
        with open(log) as f:
            txt = f.read()
        mm = re.search(r"Check SOL: (.*)", txt)
        mv = re.search(r"Maximum violations: (.*)", txt)
        res["miplib_check"] = mm.group(1).strip() if mm else None
        res["miplib_maxviol"] = mv.group(1).strip() if mv else None


def one(checker_dir, mps, aux, sol, outdir):
    sys.path.insert(0, os.path.abspath(checker_dir))
    import gurobipy as gp
    from feasibility_checker import Feasibility_Checker

    res = {"gurobi": ".".join(map(str, gp.gurobi.version())), "steps": {}}
    with open(sol) as f:
        d = json.load(f)
    res["status_in_file"] = d.get("status")
    res["objective_in_file"] = d.get("objective_value")
    if d.get("status") in (None, "infeasible", "open"):
        res["verdict"] = "no-point"
        return res
    with gp.Env(empty=True) as env:
        env.setParam("OutputFlag", 0)
        env.start()
        m = gp.read(mps, env)
        res["nvars"], res["ncons"] = m.NumVars, m.NumConstrs
        m.dispose()
    os.makedirs(outdir, exist_ok=True)  # the checker's own exists/makedirs races between processes
    buf = io.StringIO()
    t0 = time.time()
    if res["nvars"] > LIMIT_VARS or res["ncons"] > LIMIT_CONS:
        res["verdict"] = "skipped-license"
        try:
            with contextlib.redirect_stdout(buf):
                if res["nvars"] > PARSER_MAX_VARS:
                    fc = Feasibility_Checker.__new__(Feasibility_Checker)
                    fc.__dict__.update(_path_mps_file=mps, _path_aux_file=aux, _path_sol_file=sol,
                                       _instance_name=os.path.basename(mps).split(".mps")[0],
                                       _store_dir_sol_MIPLIB_Checker=outdir, _sol_format_website="True",
                                       _MIPLIB_SOLChecker_linear_cons_tolerance=1e-4,
                                       _MIPLIB_SOLChecker_linear_integer_tolerance=1e-4)
                    res["parser_bypassed"] = True
                else:
                    fc = Feasibility_Checker(mps, aux, sol, outdir, "True")
                res["steps"]["miplib"] = bool(fc.validate_cons_feasibility_miplib2017_checker())
        except Exception as e:  # noqa: BLE001 - the checker raises bare Exception
            res["error"] = "%s: %s" % (type(e).__name__, e)
    else:
        steps = res["steps"]
        try:
            with contextlib.redirect_stdout(buf):
                fc = Feasibility_Checker(mps, aux, sol, outdir, "True")
                steps["hpr"] = bool(fc.hpr_infeasibility_checker())
                if steps["hpr"]:
                    steps["miplib"] = bool(fc.validate_cons_feasibility_miplib2017_checker())
                    if steps["miplib"]:
                        steps["bilevel"] = bool(fc.validate_bilevel_feasibility())
                        if steps["bilevel"]:
                            steps["optimistic"] = bool(fc.check_optimistic_bilevel_feasible_point())
            res["verdict"] = ("fail-hpr" if not steps.get("hpr") else "fail-miplib" if not steps.get("miplib")
                              else "fail-bilevel" if not steps.get("bilevel") else "pass")
        except gp.GurobiError as e:
            res["verdict"] = "skipped-license" if e.errno == 10010 else "error"
            res["error"] = "GurobiError %s: %s" % (e.errno, e)
        except Exception as e:  # noqa: BLE001
            res["verdict"] = "error"
            res["error"] = "%s: %s" % (type(e).__name__, e)
    res["seconds"] = round(time.time() - t0, 2)
    res["messages"] = [ln.strip() for ln in buf.getvalue().splitlines() if ln.strip()][-5:]
    miplib_log(res, outdir, mps)
    return res


# ---------------------------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------------------------
def index(coll):
    idx = {}
    for root, _, files in os.walk(coll, followlinks=True):
        for f in files:
            if f.endswith(".mps.gz"):
                idx[f[: -len(".mps.gz")]] = os.path.join(root, f)
    return idx


def run(a, job):
    folder, sol, mps = job
    name = os.path.basename(sol)[: -len(".res.json")]
    base = {"folder": folder, "name": name}
    if mps is None:
        return dict(base, verdict="error", error="instance not found")
    aux = mps[: -len(".mps.gz")] + ".aux"
    outdir = os.path.join(a.work, "out", folder.replace("/", "_"))
    t0 = time.time()
    try:
        p = subprocess.run([a.python, "-I", os.path.abspath(__file__), "--one", a.checker, mps, aux, sol, outdir],
                           cwd=a.work, capture_output=True, text=True, timeout=a.timeout)
    except subprocess.TimeoutExpired:
        return dict(base, verdict="timeout", seconds=round(time.time() - t0, 1))
    res = None
    for ln in p.stdout.splitlines():
        if ln.startswith("@@RESULT "):
            res = json.loads(ln[len("@@RESULT "):])
    if res is None:
        return dict(base, verdict="error", error="rc=%s; %s" % (p.returncode, p.stderr[-300:]))
    res.update(base)
    return res


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--one":
        res = one(*sys.argv[2:7])
        sys.stdout.write("@@RESULT " + json.dumps(res) + "\n")
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("--checker", required=True)
    ap.add_argument("--python", required=True)
    ap.add_argument("--solchecker", required=True)
    ap.add_argument("--collection", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jsonl", help="raw per-file results (default: WORK/official.jsonl)")
    ap.add_argument("--tight", default="results/notes/tight_verify.tsv")
    ap.add_argument("-j", type=int, default=2)
    ap.add_argument("--timeout", type=float, default=3600)
    ap.add_argument("folders", nargs="+")
    a = ap.parse_args()
    a.checker, a.work, a.collection = (os.path.abspath(x) for x in (a.checker, a.work, a.collection))
    os.makedirs(a.work, exist_ok=True)
    link = os.path.join(a.work, LINK)
    if not os.path.exists(link):
        os.symlink(os.path.abspath(a.solchecker), link)
    assert os.access(os.path.join(link, "checker", "bin", "solchecker"), os.X_OK), "solchecker not built"
    jsonl = a.jsonl or os.path.join(a.work, "official.jsonl")
    idx = index(a.collection)
    todo = []
    for arg in a.folders:
        folder, d = arg.split("=", 1)
        for f in sorted(os.listdir(d)):
            if f.endswith(".res.json"):
                todo.append((folder, os.path.abspath(os.path.join(d, f)), idx.get(f[: -len(".res.json")])))
    done = {}
    if os.path.exists(jsonl):  # resume
        with open(jsonl) as f:
            for ln in f:
                r = json.loads(ln)
                done[(r["folder"], r["name"])] = r
    keys = {(j[0], os.path.basename(j[1])[: -len(".res.json")]) for j in todo}
    pending = [j for j in todo if (j[0], os.path.basename(j[1])[: -len(".res.json")]) not in done]
    print(f"{len(todo)} files, {len(pending)} to run", file=sys.stderr, flush=True)
    with open(jsonl, "a") as fo, cf.ThreadPoolExecutor(a.j) as ex:
        for i, r in enumerate(ex.map(lambda j: run(a, j), pending)):
            done[(r["folder"], r["name"])] = r
            fo.write(json.dumps(r) + "\n")
            fo.flush()
            if (i + 1) % 100 == 0:
                print(f"  {i + 1} done", file=sys.stderr, flush=True)

    tight = {}
    if a.tight and os.path.exists(a.tight):
        with open(a.tight, newline="") as f:
            for t in csv.DictReader(f, delimiter="\t"):
                tight[(t["folder"], t["name"])] = t
    rows = []
    for key in sorted(keys):
        r = done[key]
        st = r.get("steps", {})
        t = tight.get(key)
        # bobi verify at BOBILib's tolerances passes a file the tight test calls pass or benchmark-accepted
        bv = "" if not t else "pass" if t["class"] in ("pass", "benchmark-accepted") else "fail"
        tv = "" if not t else "pass" if t["class"] == "pass" else "fail"
        v = r["verdict"]
        if v == "pass" or v.startswith("fail"):
            agree = "-" if not bv else "yes" if (v == "pass") == (bv == "pass") else "no"
        else:
            agree = "n/a"
        note = r.get("error", "")
        if v == "skipped-license":
            note = (f"model has {r.get('nvars')} variables and {r.get('ncons')} rows (license limit "
                    f"{LIMIT_VARS} and {LIMIT_CONS}): Gurobi steps not run")
            if r.get("parser_bypassed"):
                note += "; MIPLIB step run without the bilevel parser"
        rows.append({
            "folder": key[0], "name": key[1], "verdict": v,
            "hpr": {True: "pass", False: "fail"}.get(st.get("hpr"), "-"),
            "miplib": {True: "pass", False: "fail"}.get(st.get("miplib"), "-"),
            "bilevel": {True: "pass", False: "fail"}.get(st.get("bilevel"), "-"),
            "optimistic": {True: "pass", False: "fail"}.get(st.get("optimistic"), "-"),
            "miplib_check": r.get("miplib_check") or "-",
            "miplib_max_violation": r.get("miplib_maxviol") or "-",
            "nvars": r.get("nvars", ""), "ncons": r.get("ncons", ""),
            "file_status": r.get("status_in_file", ""), "file_objective": r.get("objective_in_file", ""),
            "seconds": r.get("seconds", ""), "bobi_verify": bv or "-", "bobi_verify_tight": tv or "-",
            "agree": agree, "note": note or "-",
        })
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print(Counter((r["folder"], r["verdict"]) for r in rows), file=sys.stderr)


if __name__ == "__main__":
    main()
