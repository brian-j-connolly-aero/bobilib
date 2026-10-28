# BOBILib status update: submission

From Brian J. Connolly (Beehive Industries, brian.connolly@beehiveind.com), with the paper "Settling
650 unsolved BOBILib instances: 528 published optima, 82 new optimality proofs and 40 infeasibility
certificates" (preprint, 2026). Repository: https://github.com/brian-j-connolly-aero/bobilib; paths
that start with `results/`, `scripts/`, `paper/` or `data-manifest/` are relative to its root (the
paper's supplement is `paper/appendix/appendix.pdf`), the others to the archive
`bobilib_submission.tar.gz`.

Reference: BOBILib's metadata (`collection.json`, Last-Modified 2026-05-27, downloaded 2026-10-18,
sha256 `9a7c5c395a6bf8fd...`), the instance and solution files of bobilib-data commit `126eec55a94d`
(2025-06-10), listed file by file with their sha256 in `data-manifest/bobilib_snapshot.tsv`, and
BOBILib's feasibility checker (`feasibility-checker.tar.gz` from bobilib.org, sha256
`80286841dc3052e4...`).

## What changes

1,343 instances change status or best known value relative to that metadata (`status_changes.csv`,
one row each; the same in MIPLIB/SCIP form in `bobilib_update.solu`):

| Kind | Instances | BOBILib now | New status | Check | Certificate class |
| --- | ---: | --- | --- | --- | --- |
| new optimum proven | 82 | 77 feasible, 5 open | optimal | certificate | 75 exact, 7 numerical |
| published optimum | 528 | 513 feasible, 15 open | optimal | citation | 528 numerical |
| no bilevel feasible point | 40 | 40 open | infeasible | certificate | 40 exact |
| first feasible point | 228 | 228 open | feasible | checker | 228 numerical |
| better feasible point | 465 | 465 feasible | feasible (value improves) | checker | 232 exact, 233 numerical |

* New optima: 16 subset-sum knapsack interdiction, 57 clique interdiction, 2 attack-protect
  (`inter-fire`) and 7 general instances whose HPR is a MIPLIB model with a published optimum. For
  52 of the 610 optima BOBILib's value was already optimal and only the status changes.
* Published optima: 376 Weninger and Fukasawa (2025), 97 Lozano, Bergman and Cire (2026), 52
  Fischetti et al. (2019), 1 an earlier BOBILib release, 1 Fischetti et al. (2017), 1 Vasquez,
  Lozano and van Hoeve (2025) (full references in `status_changes.csv`, column `citation`). For 82
  of them there is no solution file here; only the published value is used.
* First feasible points: BOBILib lists no point; for 167 it is the first point anywhere, for the
  other 61 a published point existed (named in `notes`).
* `bobilib_update.solu` also has 194 `=bestdual=` lines (proven lower bounds better than any
  published: OR instances with one follower knapsack and the 3 open clique instances). BOBILib's
  metadata has no field for them; they are not rows of `status_changes.csv`.

## Easy to check: the feasible points (column `check` = `checker`)

`solutions/` holds 1,219 solution files in BOBILib's format (`<instance>.res.json`), one for every
row with a `solution_file`: the 228 first and 465 better points, and the points at the new and
published optima (the 82 published optima without a file and the 2 optima at BOBILib's own point
need none). Each one is checked by your feasibility checker alone. We ran it (Gurobi 13.0.3, pip's
size-limited license, default tolerances; `notes/official_checker.md`): **1,111 pass** all three
steps (HPR, MIPLIB solution checker, follower optimal with the leader fixed), and the optimistic
tie-break check too; the other **108** exceed the license's 2,000 variables or rows, so only the
solver-free MIPLIB step ran, and it passed. All 1,219 also pass this repository's
`bobi verify --tight` (follower within max(1e-6, 1e-9 |phi|) of its proven optimum;
`notes/tight_verify.md`). No file fails any check. With a full Gurobi license the solver steps would
also run on the 108 large ones.

Each file's `status` is the new status. 75 files differ from the repository's copy in that field
only: the repository's files of 70 published optima and 5 new optima say `feasible`, the status
under which the point was found. Everything else is byte for byte the same.

## Needs more: optimality and infeasibility (column `check` = `certificate` or `citation`)

A point only gives an upper bound. The lower bound or the infeasibility proof is:

| Claim | Instances | Certificate (in `certificates/`, same path as under `results/`) | How to check | Supplement section |
| --- | ---: | --- | --- | --- |
| subset-sum knapsack interdiction optimum | 16 | `ss/proofs.csv` | exhaustive search (`bobi ss-solve`); independent prover `checkers/ss_check.py` | Knapsack interdiction proofs |
| clique interdiction optimum, value 3 | 27 | `clique/summary.csv` | Mantel's theorem: m - k > floor(n^2/4) (arithmetic) | Clique interdiction proofs |
| clique interdiction optimum, value 4 | 30 | `clique/certificates/*.cert.jsonl.gz` | Brouwer (1981) Thm 2 plus w3(G) > k, `checkers/check_clique_certificates.py` (integer arithmetic) | Clique interdiction proofs |
| attack-protect optimum | 2 | `network/summary.csv`, `network/review.tsv` | every attack enumerated, 2,138,410 per instance (`bobi fire`; independently `checkers/network/fire_check.c`) | Network interdiction |
| optimum at the MIPLIB bound of the HPR | 7 | `general/hpr_optimal.csv` | `checkers/compare_hpr.py` (HPR = MIPLIB model) and MIPLIB's published optimum | General instances: rays, HPR bound and pipelines (The HPR bound and the MIPLIB optimum) |
| no bilevel feasible point | 40 | `rays/*.ray.json` | `checkers/verify_ray.py`: exact rational check of a recession direction of the follower | General instances: rays, HPR bound and pipelines (Unbounded followers: no bilevel feasible point) |
| published optimum | 528 | (the cited paper) | as published; not re-proved here | Per-instance tables (Published optima) |

The upper bound of each new optimum is its solution file (in the clique files the leader deletes
exactly the edges inside the parts of a partition, so the follower's clique number is at most the
number of parts). For 2 of the HPR-bound optima the point is BOBILib's own solution file, so there
is no file here. The supplement has the proofs; `lean/` in the repository formalises the knapsack
interdiction lemmas.

## Certificate classes (column `certificate_class`)

* `exact`: checked in exact rational or integer arithmetic, or a proof plus an exhaustive integer
  computation; no tolerance enters.
* `numerical`: rests on a floating-point LP/MILP solver run with tolerances (rows within 1e-6,
  follower optimum by HiGHS within max(1e-6, 1e-9 |phi|)), or on a published optimum used as
  published, or on MIPLIB's published floating-point optimum.
* `benchmark` (a point accepted only because of the checker's 1e-4 tolerances): none here. The
  repository keeps 25 superseded points of this class in `results/*/tolerance/`; the four of them
  that fit Gurobi's free license pass your checker (`notes/official_checker.md`).

For the 465 better points, `results/instances.csv` gives no class (the status does not change); here
the class of the point follows the same rules: OR points with one follower knapsack are `exact`
(integer data, exact knapsack oracle), with several `numerical`, and the 3 clique points `exact`
(partition argument).

## Contents of `bobilib_submission.tar.gz`

```
bobilib_submission/
  README.md              this file
  status_changes.csv     one row per change: instance, BOBILib's status and value, new status and value,
                         kind, check, certificate class, solution and certificate files (repository
                         paths), official checker result, how to check, supplement section, citation, notes
  bobilib_update.solu    the same changes in MIPLIB/SCIP .solu form (plus =bestdual= lower bounds)
  solutions/             1,219 solution files in BOBILib's format
  certificates/          the certificates and tables named in status_changes.csv, with their READMEs
  checkers/              the stand-alone checkers named above (Python 3; ss_check.py needs numpy; fire_check.c
                         is C) and run_official_checker.py, which runs your checker over solutions/
  notes/                 our runs of your checker and of bobi verify --tight, per file
  snapshot/              the BOBILib snapshot used: every instance and solution file with its sha256
  LICENSE-data, LICENSE-code, SHA256SUMS
```

To run your checker over all files (it calls
`./miplib2017-testscript-v1.0.3/checker/bin/solchecker`):

```sh
python3 -I checkers/run_official_checker.py --checker feasibility-checker --python python3 \
    --solchecker miplib2017-testscript-v1.0.3 --collection collection --work work \
    --out official.tsv --tight '' all=solutions
```

## License

Solution files, certificates and tables: CC BY 4.0 (`LICENSE-data`), which allows BOBILib to
redistribute them under its CC BY-SA 4.0. Checkers: MIT (`LICENSE-code`). Please cite the paper
above.
