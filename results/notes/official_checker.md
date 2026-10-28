# BOBILib's official feasibility checker on every solution file

BOBILib's own feasibility checker was run on all 1,478 current solution files
(the 1,469 loose ones and the nine in `general/large_points.tar.gz`), with the
checker's default tolerances. **1,370 pass, 0 fail, 108 could not be run in
full** because Gurobi's free license is limited to 2,000 variables and 2,000
rows. For those 108, only the solver-free step (the MIPLIB solution checker)
ran, and all 108 pass it. `official_checker.tsv` has one row per file.

## What was run

* **Checker.** BOBILib's `feasibility-checker.tar.gz` (bobilib.org, downloaded
  2026-10-18, sha256 `80286841dc3052e49f3902f8b1addd62a657ce378dbc92cdc6eab4198506138f`):
  `feasibility_checker.py` with `name_based_bilevel_parser/`. The checker's code
  was not changed.
* **Gurobi.** gurobipy 13.0.3 from PyPI, with the size-limited license that
  comes with it (2,000 variables, 2,000 linear rows), under Python 3.13.16.
* **MIPLIB 2017 solution checker.** `miplib2017-testscript-v1.0.3.zip` (miplib.zib.de,
  sha256 `0fbc70f35e193d33e7a990a47aa06dbead3cbd73f921fffb779d77ab3db9d467`).
  `solchecker` was built from its four `checker/src/*.cpp` files with
  `g++ -O2 ... -lgmp -lz` (g++ 13.3.0, GMP 6.3.0, zlib 1.3) rather than
  `make checker`. The sources were not changed.
* **Steps, per file**, in a separate process and in the order of
  `run_feasibility_checker_website.py`. A file passes if steps 1 to 3 pass.
  1. `hpr_infeasibility_checker()`: the HPR has a feasible point (Gurobi,
     `SolutionLimit` 1).
  2. `validate_cons_feasibility_miplib2017_checker()`: the point's
     integrality, rows, bounds and stated objective, checked by `solchecker`
     in exact rational arithmetic with tolerance 1e-4.
  3. `validate_bilevel_feasibility()`: the follower's problem with the
     leader's values fixed is solved by Gurobi (`FeasibilityTol` 1e-6,
     default `MIPGap` 1e-4). Its optimum must match the file's follower
     value to a relative 1e-4.

  An extra column records the README's fourth check,
  `check_optimistic_bilevel_feasible_point()`. It tests that the file's
  value is the leader's best over the follower's optimal responses at the
  file's leader values.
* **Driver.** `scripts/run_official_checker.py` (command below). It calls the
  checker's methods, reads `solchecker`'s log, and joins each file to its row
  in `tight_verify.tsv`.

## Results

| Folder | Files | Pass (steps 1-3) | Optimistic check pass | Fail | Skipped (license) | MIPLIB step pass on the skipped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `ss` | 16 | 16 | 16 | 0 | 0 | - |
| `kip` | 583 | 583 | 583 | 0 | 0 | - |
| `or` | 690 | 690 | 690 | 0 | 0 | - |
| `clique` | 60 | 20 | 20 | 0 | 40 | 40 |
| `network` | 36 | 36 | 36 | 0 | 0 | - |
| `general` (loose files) | 55 | 16 | 16 | 0 | 39 | 39 |
| `general/large_points.tar.gz` | 9 | 0 | 0 | 0 | 9 | 9 |
| `general-coupled` | 29 | 9 | 9 | 0 | 20 | 20 |
| **all** | **1,478** | **1,370** | **1,370** | **0** | **108** | **108** |

* **Skipped (108).** These are the 40 clique instances with n = 50 or 60,
  where the smallest model, normalClique50-70-1, has 1,764 variables and
  2,083 rows, and 68 general files with up to 799,616 variables
  (supportcase12_0_100). Gurobi's `optimize()` refuses models of this size
  under the license (error 10010, "Model too large for size-limited
  license"), so steps 1 and 3 cannot run. Step 2 does not need a solver. On the five models with more
  than 150,000 variables, step 2 ran without the bilevel parser: the
  parser's name lookups take time quadratic in the number of variables
  (hours to days at that size), and step 2 does not use it.
* **MIPLIB step.** No integrality violation in any file. The largest row or
  bound violation is 3.4e-7 (neos-3627168-kasai_0_100). The largest
  difference between the stated and the recomputed objective is 2.7e-7
  (neos-873061_0_100). 1,409 of the 1,478 files have no violation at all.
* **Runtime.** About 15 minutes with two files at a time on a shared 4-core
  machine. The slowest file, neos-4722843-widden_0_100 (77,723 variables,
  MIPLIB step only), took 237 s.

The 1,219 files of the submission package (`submission/`, built by
`scripts/build_submission.py`) are among these. In 75 of them the `status`
field is set to the new status. Run on those copies, the checker gives the
same result: 1,111 pass and 108 are skipped, each passing the MIPLIB step.

## Comparison with `bobi verify`

There are no disagreements. Every file that the official checker ran in full
passes it, and all 1,478 files also pass `bobi verify` and `bobi verify
--tight` (`tight_verify.tsv`; columns `bobi_verify`, `bobi_verify_tight` and
`agree`). The 108 skipped files are not disagreements. For them, the
official checker confirms only the rows, bounds, integrality and objective.
That the follower's response is optimal rests on `bobi verify --tight` (and,
for the clique files, on the partition argument in `clique/README.md`). With
a full Gurobi license the checker could run steps 1 and 3 on them too.

The official checker is weaker than `bobi verify --tight` in one respect.
Gurobi solves the follower to its default relative gap of 1e-4, and the
checker then compares the result with the file's value at a further
relative 1e-4. The 26 superseded files in `*/tolerance/` show this. Their
results are in `official_checker_superseded.tsv`: 25 of the 26 are
benchmark-accepted, with the follower 5e-8 to 1.02e-7 relative above its
optimum. Five of the 26 fit the license, and the official checker passes
all five, including four benchmark-accepted ones (ic97_potential_0_100,
ic97_potential_50_50, exp-1-500-5-5_0_100 and tr12-30_0_100). The other 21
pass the MIPLIB step. This is what class (iii) of the paper means: these
points pass BOBILib's checker only because of its tolerances. None of the
current files is of that class.

## Notes on the checker

None of the following affects a result above. They may be useful to
BOBILib's maintainers.

* The checker passes `solchecker` its two tolerances as one argument,
  `[0.0001 0.0001]`. `solchecker` reads the digits of both numbers as a
  single number, so both of its tolerances are 100001/10^9 = 1.00001e-4. The
  log prints `Linear tolerance: 100001/1000000000`. This is the intended
  1e-4 to within 1e-9.
* The checker creates its output directory with an exists-then-`makedirs`
  test. When two checks start at the same moment, one fails with
  `FileExistsError`. The driver creates the directory first.
* `name_based_bilevel_parser.determine_variable_bounds()` records the bounds
  of the last lower-level variable for every upper-level variable (it uses
  `var` from the previous loop). The checks do not use those lists.

## Command

```sh
cd bobilib
python3 -m venv /tmp/grb && /tmp/grb/bin/pip install gurobipy==13.0.3
# BOBILib's checker unpacked to CHK/; MIPLIB's test script unpacked to CHK/miplib2017-testscript-v1.0.3
# and solchecker built there: g++ -O2 -o checker/bin/solchecker checker/src/*.cpp -lgmp -lz
mkdir -p /tmp/large && tar xzf results/general/large_points.tar.gz -C /tmp/large
python3 -I scripts/run_official_checker.py --checker CHK --python /tmp/grb/bin/python \
    --solchecker CHK/miplib2017-testscript-v1.0.3 --collection data/collection --work /tmp/fchk \
    --out results/notes/official_checker.tsv -j 2 --timeout 3600 \
    ss=results/ss kip=results/kip or=results/or clique=results/clique network=results/network \
    general=results/general general/large_points.tar.gz=/tmp/large general-coupled=results/general-coupled
# the superseded files, renamed to .res.json as in tight_verify.md (/tmp/tolc, /tmp/tolg):
python3 -I scripts/run_official_checker.py ... --out results/notes/official_checker_superseded.tsv \
    general-coupled/tolerance=/tmp/tolc general/tolerance=/tmp/tolg
```

`official_checker_superseded.tsv` has the same columns as `official_checker.tsv`.

## `official_checker.tsv`

The file is tab separated, with one row per file. Its columns:

* `folder`, `name`.
* `verdict`: `pass`, `fail-hpr`, `fail-miplib`, `fail-bilevel`,
  `skipped-license`, `timeout` or `error`.
* `hpr`, `miplib`, `bilevel`, `optimistic`: the result of each step, `pass`,
  `fail`, or `-` if the step was not run.
* `miplib_check` and `miplib_max_violation`: `solchecker`'s "Check SOL" and
  "Maximum violations" lines.
* `nvars`, `ncons`: the model's size as Gurobi reads it.
* `file_status`, `file_objective`: as stated in the file.
* `seconds`.
* `bobi_verify` and `bobi_verify_tight`: the file's verdict at BOBILib's
  tolerances and under the tight test, from `tight_verify.tsv`. A
  `benchmark-accepted` file passes the first and fails the second.
* `agree`: whether the official verdict matches `bobi_verify`; `n/a` if the
  file was skipped.
* `note`.
