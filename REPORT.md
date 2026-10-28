# BOBILib: what can be solved, and approaches that resolve many instances at once

*Status as of 2026-10-19, with the literature check of 2026-10-28 (published
optima credited to their first publication; see "Literature" below).
`scripts/summarize.py` regenerates every count from
the files in `results/` and `runs/`; `results/summary.json` is its output.
`results/instances.csv` gives every instance's outcome and the certificate
class of each result (exact, numerical or benchmark-accepted; see
`results/README.md`).*

## The question

[BOBILib](https://bobilib.org) (the Bilevel Optimization Benchmark Instance
Library; Thürauf, Kleinert, Ljubić, Ralphs and Schmidt, *Mathematical
Programming Computation* 2026) holds 2,654 mixed-integer bilevel linear
problems (MIBLPs): a leader decides first, a follower then solves its own
optimisation problem given the leader's decision, and the leader's
objective depends on the follower's reply. BOBILib lists 1,027 instances as
optimal, 33 as infeasible, 1,175 as feasible (a point is known, no proof)
and 419 as open (no point known). We asked which of the 1,594 feasible or
open instances can be solved or improved, and whether new approaches could
resolve many of them at once.

## Short answer

Yes. Of the 1,594:

| Outcome | Instances |
| --- | ---: |
| already proven optimal in published work (BOBILib's labels are stale) | 531 |
| proven optimal here (not published before) | 79 |
| proven here to have no bilevel feasible point at all | 40 |
| verified point here where BOBILib lists none (167 of them the first anywhere) | 228 |
| status unchanged (many with better points, see below) | 716 |

So 650 (41%) are now settled, 610 of them optimal. On top of the status
changes, 474 instances of the OR set get a verified point strictly better
than every published value.

Two observations carry most of the weight.

1. **BOBILib's statuses come from two general-purpose bilevel solvers**
   (MibS and Fischetti et al.'s MIX++), one hour on one thread each. The
   specialised literature is far ahead: 376 knapsack interdiction, 140
   multidimensional knapsack interdiction, 4 generalized interdiction, 9
   MIPLIB-derived and 2 network interdiction instances are solved in
   published work (one of the MIPLIB-derived, ex10_0_100, only in Lefebvre
   and Schmidt's run files).
2. **Most unsolved instances share a structure that general solvers ignore.**
   1,254 of the 1,594 are *packing interdiction* games: the leader removes
   items within one or more budgets, the follower packs what is left into
   one or more knapsacks, and the game is zero-sum. Another 60 are clique
   interdiction on graphs whose density puts them in reach of extremal
   graph theory, and almost all of the 266 general instances are built
   from MIPLIB (the Mixed Integer Programming Library) problems whose
   published optima are lower bounds.

The approaches that resolve whole families rather than single instances:

| Approach | Family | Effect |
| --- | --- | --- |
| Robust subset-sum search (Weninger and Fukasawa's counted copies and online game, played on weight classes with an end set from each node's decided sums and rebuilt at every node) | knapsack interdiction, subset-sum and even-odd classes | all 16 instances open in the literature proven optimal (8 even-odd, 8 subset-sum), each in about 10 s of CPU time or less on one thread, and checked by an independent prover |
| Dualised follower linear program (LP) bracket and a merged-row online bound | multidimensional knapsack interdiction (OR set), one follower knapsack | paired median gap 24% → 4.0% (budget 25%) and 34% → 7.1% (budget 50%); 191 better lower bounds |
| Certified points from the follower LP | OR set, several follower knapsacks | all 360 instances with budget 50% or 75% certified; 88 first points anywhere |
| Extremal graph theory (Mantel 1907, Brouwer 1981) plus partition certificates | edge clique interdiction | 57 of 60 proven optimal at 3 or 4, where BOBILib lists 5 to 13 |
| Exhaustive attacks with an exact tree dynamic program (DP) | attack-protect network interdiction | both non-optimal instances re-proved optimal in exact arithmetic (already solved by MIX++: Fischetti et al. 2017, online appendix of 29 June 2016, Table 9) |
| Recession-ray certificates (the one-LP test of Fischetti et al., *Math. Programming* 172, 2018, Theorem 1) | MIPLIB-derived | 40 open instances have no bilevel feasible point (all 40 checked in exact arithmetic) |
| High point relaxation (HPR), then the follower, then an optimistic tie-break; a portfolio for coupling rows | MIPLIB-derived | 93 verified points where BOBILib lists none (64 without coupling rows, 29 with), 5 of them optimal (4 proven here, and ex10_0_100, a published optimum); for 9 of the others a published point already existed |
| HPR bound = published MIPLIB optimum | MIPLIB-derived | 6 proven optimal (4 of them open, with no point known before); it also confirms the published optimum of ex10_0_100 |

What stays hard: 3 clique instances (value 3 or 4), OR instances with
several follower knapsacks at budget 25% (120 still without a certified
point, and the best lower bounds 28-31% away), 8 generalized interdiction
instances with 20 or more linking bits, and 123 general instances (122 of
them MIPLIB-derived).

## Family by family

### Knapsack interdiction (599 instances; 392 not optimal in BOBILib)

* **Literature.** Weninger and Fukasawa's combinatorial branch and bound
  (IPCO 2023; *Math. Programming* 210, 2025) solves 583 of the 599. BOBILib
  lists 376 of those as not optimal; at 335 of them its value is above the
  optimum (median 8%, up to 672%). `results/kip/` holds a verified solution
  file for each of the 583 (`bobi kip-import`, checked with `bobi verify`).
  The 376 are credited to their first publications
  (`results/literature/kip_first_publication.csv`): 14 `cclw` optima to
  Caprara, Carvalho, Lodi and Woeginger (*INFORMS J. Comput.* 28, 2016;
  among them interdiction55-4, which the 2016 report below counts as
  previously unsolved, but whose proof Caprara et al.'s text reports),
  the 25 `inter-kp` optima and interdiction55-3 to Fischetti, Ljubić,
  Monaci and Sinnl's technical report of 2016 (the preprint of their
  *INFORMS J. Comput.* paper of 2019), and the 336 `kp` optima to Weninger
  and Fukasawa's answer files (the bkpsolver repository was public by
  7 Oct 2022; their preprint of that day gives counts per class only).
  Della Croce and Scatamacchia (*Math. Programming* 183, 2020) had reported
  266 of the 336 solved, as counts per group without values (for 6 of
  them this assumes that their misprinted "#Opt 6/18" means 6 of 6). Lozano, Bergman and
  Cire's solution files prove 228 of the 376 again later. Three earlier
  documents could not be read in full (the journal version of the 2016
  report with its supplement, Della Croce and Scatamacchia's IPCO 2019
  paper, and the version of record of Fischetti, Monaci and Sinnl's EJOR
  2018 paper, which introduced the `kp` set); that they list no `kp`
  values is inferred from their abstracts, from the accepted manuscript of
  the EJOR paper ("the optimal solution value is not known") and from
  Della Croce and Scatamacchia's own runs of the 2019 paper's code on the
  80 `kp` instances with 100 items.
* **The 16 left.** All have budget index 2 or 3 and 200-500 items; 8 are in
  the subset-sum class (profit equals weight) and 8 in the even-odd class.
  Weninger and Fukasawa (16 threads, 1 h), their reimplementation of Della
  Croce and Scatamacchia, and Lozano, Bergman and Cire's decision diagrams
  (2 h) all leave them open; the best lower bounds sit 2 to 8 units below
  the incumbent, which equals the follower's capacity (or capacity minus
  one for even-odd). Weninger's 2026 preprint (arXiv 2604.21877, v2 of
  16 Oct 2026) still reports 16 of the 100 subset-sum instances unsolved
  after one hour. The current version of their code (commit bc1d985, 3 Aug
  2026) adds symmetry breaking by item dominance, which its README says
  speeds up subset-sum instances by roughly an order of magnitude; no
  results of it are published, and it was not run here.
* **New here, and what is not.** `robust_ss` decides "can the leader keep
  the follower below the capacity?" by search over *how many copies of each
  weight survive* (identical items are interchangeable for the follower,
  and the leader should remove the cheapest copies first). Counted copies
  are Weninger and Fukasawa's: their code merges identical items into
  counted copies (option `-dedup`, commit 1838efe, May 2023). The strongest
  rule is their online relaxation and lower bound: the leader deletes one
  class at a time and may react to what the follower took from earlier
  classes, which only helps the leader, so whatever the follower can still
  guarantee holds in the real game; their code (bkpsolver) already plays
  this game class by class on classes of identical items. New here are
  only classes of one weight whose copies have different costs, the set
  the game must end in built from a node's own decided sums, and the table
  rebuilt for that end set at every node. The guarantee is antitone in the
  budget, so it is stored as one budget threshold per (class, residual
  sum), and a single backward pass computes it for the undecided classes,
  which is cheap enough to do at every node that would branch. The order of play matters a great deal: classes that
  are cheapest to delete per unit of mass go first, so the follower sees
  the leader's likely deletions before it commits, and the expensive
  classes are kept for fine adjustment. Contiguous windows of reachable
  sums and the stall analysis remain as cheaper rules. All 16 are now
  proven optimal (one thread, CPU seconds on a shared machine, where wall
  times were 2-3 times longer; "before" is the previous version of the same
  search on the same machine):

  | Instance | Optimum | Nodes | Time | Before (nodes / time) |
  | --- | ---: | ---: | ---: | ---: |
  | interKP-200-100-6-2 | 1,855 | 303 | 0.10 s | 3,926,223 / 22.77 s |
  | interKP-300-100-6-2 | 2,868 | 366 | 0.16 s | 12,302,768 / 102.59 s |
  | interKP-400-100-6-2 | 3,832 | 257 | 0.15 s | 7,217,774 / 75.29 s |
  | interKP-500-100-6-2 | 4,651 | 190 | 0.26 s | 14,290,940 / 174.28 s |
  | interKP-200-100-6-3 | 2,782 | 13,498 | 3.93 s | not finished in 4 h |
  | interKP-300-100-6-3 | 4,302 | 19,405 | 8.06 s | not finished in 3 h |
  | interKP-400-100-6-3 | 5,748 | 13,430 | 9.01 s | not run to the end |
  | interKP-500-100-6-3 | 6,976 | 10,079 | 10.04 s | not run |
  | interKP-200-100-7-2 | 1,872 | 22 | 0.06 s | 48,598 / 0.49 s |
  | interKP-300-100-7-2 | 2,894 | 27 | 0.04 s | 115,415 / 1.78 s |
  | interKP-400-100-7-2 | 3,866 | 18 | 0.05 s | 269,550 / 5.62 s |
  | interKP-500-100-7-2 | 4,694 | 1 | 0.05 s | 357,279 / 10.26 s |
  | interKP-200-100-7-3 | 2,808 | 651 | 0.10 s | 2,341,175 / 9.61 s |
  | interKP-300-100-7-3 | 4,340 | 470 | 0.20 s | 3,256,897 / 20.35 s |
  | interKP-400-100-7-3 | 5,800 | 378 | 0.17 s | 10,710,774 / 86.43 s |
  | interKP-500-100-7-3 | 7,042 | 256 | 0.15 s | 13,346,235 / 137.19 s |

  In every case BOBILib's value was already optimal; the proof is new.
  The evidence for the four index-3 proofs is independent several times
  over: `scripts/ss_check.py` (the designer's prover: own parser, plain
  search, the per-node rule written from its definition, no code shared
  with the Rust search) and `scripts/ss_judge_check.py` (a reviewer's
  prover written without reading either) confirm all 16 lower bounds; two
  other redesigns of the search, built separately (witness reuse, and
  block tables from a hitting-set view), prove 200-6-3 at 2,782 as well,
  and the witness version all four; the reviewer compared every binary
  with exhaustive enumeration on 2,990 random small instances (0
  mismatches); and every solution file passes `bobi verify`. See
  `results/ss/`. The threshold form and the per-node end set are proved
  in Lean (`lean/Bobi/Threshold.lean`, `lean/Bobi/EndTable.lean`); the range
  shortcuts and early exit inside the node-table pass are argued in the doc
  comments of `src/robust_ss.rs`. One change at a
  time on interKP-200-100-6-2 (nodes): previous search 3,926,223; same
  rules with threshold tables 3,926,223 (memory 478 to 229 MB); every band
  width 1..64 3,278,153; root tables played largest value first 1,128,566,
  or cheapest per unit of mass first 513,834; per-node tables 303. With
  100 items, the class 6 and 7 instances with budget index 4-10, which the
  previous version did not finish in two minutes, now close at the root,
  and all 20 match Weninger and Fukasawa's optima.

### Multidimensional knapsack interdiction (954; 862 not optimal)

* **imkp (144).** Fischetti, Ljubić, Monaci and Sinnl solved all 144 in
  their technical report of 2016 (the preprint of their *INFORMS Journal on
  Computing* paper of 2019), which introduced the set; BOBILib lists 52 as
  only feasible, with values up to 23% above the optimum. The 52 are credited
  to the report (`results/literature/imkp_first_publication.csv`): 42 are in
  the branch-and-cut columns of its Tables 4-6, and 10 in the captions of
  Tables 5 and 6 (runs with a longer time limit, reported solved in the
  text).
* **OR (810).** Built from Chu and Beasley's multidimensional knapsacks in
  the OR-Library (Operations Research Library): 100-500 items, 5-30 rows,
  budgets 25/50/75%, and three variants (-100: one follower knapsack; -0
  and -50: several). BOBILib has no optimum. Lozano, Bergman and Cire
  (*Operations Research* 2026) proved 87 (budget 75%); 139 had no published
  point.
* **One follower knapsack (270): published bounds, applied here.**
  Dualising the follower's LP gives U(x) = min over l >= 0 of
  l C + sum_j max(0, p_j - l w_j)(1 - x_j); with binary x the product
  linearises exactly, so min over x of U(x) is one mixed-integer linear
  program (MILP). This dualisation is the one Caprara et al.'s algorithm
  for knapsack interdiction rests on (2016), and the classical single-level
  reformulation of network interdiction (Wood 1993; Israeli and Wood
  2002). A knapsack's optimum is within one item's profit of its LP value,
  which brackets the bilevel optimum; for one follower knapsack this
  bracket is Weninger's (arXiv 2604.21877, 2026, Proposition 3). Weninger
  and Fukasawa's online relaxation, applied to several leader rows by
  merging them into one surrogate row (Glover 1968) with tuned multipliers
  and to large integer data by rounding in the safe direction, gives a
  second, usually stronger lower bound. With local search on the leader,
  all 270 get a verified point and 191 a better lower bound than
  published. Median gaps over the same
  instances:

  | Budget | Literature | Now |
  | --- | ---: | ---: |
  | 25% | 24.0% | 4.0% |
  | 50% | 34.0% | 7.1% |
  | 75% | 0.14% | 0.14% |

* **New, several follower knapsacks (540).** The follower's LP at the
  minimiser of U is a valid upper bound on the optimum for every instance,
  and whenever HiGHS solves the follower exactly at that leader choice the
  point is certified. All 360 instances with budget 50% or 75% are
  certified, including the 500-item, 30-row ones with no point anywhere; at
  budget 25%, 60 of 180. Lower bounds here are the literature's, so the
  median gaps move only through better points:

  | Variant, budget | Median gap, literature | Median gap, now | No published point: first point here |
  | --- | ---: | ---: | ---: |
  | -0, 25% | 33.3% | 31.4% | 0 of 31 |
  | -0, 50% | 36.6% | 29.1% | 31 of 31 |
  | -0, 75% | 5.2% | 0.05% | 27 of 27 |
  | -50, 25% | 30.1% | 28.2% | 0 of 20 |
  | -50, 50% | 41.3% | 34.9% | 20 of 20 |
  | -50, 75% | 11.8% | 1.4% | 10 of 10 |

  (Medians are over the instances with both a published lower and upper
  bound, without OR10x100-0.75_4.dat-0, whose published bounds conflict.
  Lefebvre and Schmidt's values count as published points only from runs
  that ended before the time limit, as in most of their own analysis;
  `scripts/ls_mkip_points.py`.)

* Over all 810: 690 verified points, 474 strictly better than every
  published value (BOBILib's included), 88 the first anywhere
  (`results/or/compare.csv` per instance, next to the solution files).
* OR10x100-0.75_4.dat-0 is optimal in the published data: the lower bound
  8,814 in Lozano et al.'s table comes from runs they mark numerically
  inconsistent, but their repository's branch-and-cut bound of 8,813 meets
  their point of 8,813. Our verified point (also checked with SCIP) confirms
  it; the instance counts as a literature closure, not ours.
* Tried and dropped: an interdiction-cut loop (the leader's MILP with one
  cut per follower packing) stalls far below the published bounds (4,515
  against 8,747 after 600 s on OR10x100-0.75_3.dat-0).

### Edge clique interdiction (220; 60 not optimal)

The leader deletes at most k edges (a quarter of them) and the follower
takes a maximum clique of what remains. The 60 `clique` instances (40-60
vertices, density 0.7 or 0.9) are unsolved in the literature, and BOBILib's
values are 5 to 13. With m edges, m - k remain after any deletion:

* **Density 0.7, value 3 (27 of 30).** m - k > floor(n^2/4), so by Mantel's
  theorem a triangle always survives (value >= 3). Deleting the edges inside
  the parts of a 3-way vertex partition with at most k inside edges leaves a
  3-partite graph (value <= 3).
* **Density 0.9, value 4 (all 30).** m - k >= t_3(n) - floor(n/3) + 2, so by
  Brouwer's theorem (A. E. Brouwer, *Some lotto numbers from an extension
  of Turán's theorem*, Mathematisch Centrum ZW 152/81, 1981, Theorem 2; n >=
  2r + 1 holds) a K4-free remainder would be 3-partite, and the deletion
  would contain every inside edge of some 3-partition. Every 3-partition
  has more than k inside edges (170 part-size cases, each decided by solver
  runs and certified by an explicit branch-and-bound tree that a short
  integer-only checker verifies), so value >= 4; a 4-partition gives <= 4.
* **Open:** normalClique60-70-2, -3 and -5, between 3 and 4. Value 3 needs a
  set of at most 309 edges meeting every K4; the best found has 310-311,
  and LP bounds on that set stop near 296.
* The same arguments reproduce all 160 optimal values of the `bcpins` and
  `plusbcpins` sets.

`results/clique/` holds the 60 solution files, the partitions, the solver
logs, the case certificates (`certificates/`) and an independent review.

### Network interdiction (72; 2 not optimal)

In the attack-protect game (`inter-fire`, Baggio et al. 2021) the leader
attacks at most Phi nodes, the follower then protects at most Lambda, and
the attack spreads from attacked nodes through unprotected neighbours; the
follower maximises the nodes it saves and the leader minimises them. For
tree-50_1-5-5_006 and _010, `bobi fire` enumerates all 2,138,410 attacks of
up to 5 of the 49 nodes and solves the follower on each forest exactly by a
DP over (protected, saved) per node with the budget as a knapsack
dimension, so the minimum over attacks is a proven bound. Both are optimal
at 26, BOBILib's value. This is not new: Fischetti, Ljubić, Monaci and
Sinnl's MIX++ had already proved all 72 `inter-fire` instances optimal, these
two at 26 in 2,121 s and 1,703 s on four threads (*Operations Research* 65,
2017, Table 1; online appendix of 29 June 2016, Table 9). The enumeration
re-proves the published values in exact arithmetic, and both instances count
as published optima, with certificate class `exact` because of the re-proof
(all other published optima are `numerical`). The same code reproduces all 34 tree values BOBILib
lists as optimal; with brute force on the small random graphs, 54 of
BOBILib's 70 optimal values are re-derived (`results/network/`).

### Generalized interdiction (90; 12 not optimal)

Lozano et al. prove 4. BOBILib's solution file for general20-30-20-20-20-2
does not pass a check at tight tolerances: its follower value is
106,899,984.14 against the follower's optimum 106,899,953 at the same leader
choice (31 units, relative 2.9e-7), and its rows are violated by up to
3.3e-4 (`results/notes/general20-30-20-20-20-2.verify.tsv`). A relative
follower tolerance of 1e-4 accepts this, because follower objectives are
near 1e8.
Enumerating the linking bits reproduces the published optimum 299,577 for
general30-30-10-20-20-8 (10 bits); with 20 bits the same takes about 58 CPU
hours per instance, so the other 8 need a pruned search.

### General instances (266 not optimal: 265 MIPLIB-derived, 1 misc; not counting 33 infeasible)

* **Literature (9).** 3 MIPLIB 3 instances by Fischetti et al. (2017, caption
  of Table 6, "more aggressive setting": air03-0.100000, p0201-0.100000 and
  p0282-0.500000; the last two were proved optimal again later by Vasquez,
  Lozano and van Hoeve, 2025, and the first of them also by Lozano, Bergman
  and Cire), 4 by Lozano et al. (decision diagrams), ex10_0_100 in Lefebvre
  and Schmidt's run file `results-MILP.csv` (Optimal/Proved, value 100 =
  bound 100, 624 s, posted 12 June 2025; their paper does not name it; the
  MIPLIB bound and a verified point confirm it here), and neos-950242_0_100
  in an earlier BOBILib release.
* **No bilevel feasible point at all (40 open instances).** The follower's
  own rows admit a direction d with follower objective e.d < 0. Leader
  variables only shift right-hand sides, so d is a recession direction for
  every leader choice, and with rational data a feasible mixed-integer
  follower whose LP relaxation is unbounded is itself unbounded (Meyer
  1974): no leader choice has an optimal response. The test is one LP, as
  in Theorem 1 of Fischetti et al. (*Math. Programming* 172, 2018), which
  extends Lemma 2 of Xu and Wang (2014); new here are its application to
  BOBILib's unsolved general instances and the exact check. All 40 directions are
  checked in exact rational arithmetic (`scripts/verify_ray.py`); for the
  two supportcase42 instances the direction is a single continuous follower
  variable, found in exact arithmetic by `scripts/exact_ray.py`
  (`results/rays/`).
* **Verified feasible points without coupling rows (64).** Solve the HPR (the
  rows of both levels with the leader's objective, without the follower's
  optimality), fix the leader, solve the follower to optimality, and break
  ties optimistically. This handles continuous linking variables, which
  neither BOBILib solver accepts (`results/general/`).
* **Verified feasible points with coupling rows (29).** When leader rows
  contain follower variables, the follower's optima at the HPR's leader
  values can violate them. `bobi coupled` certifies or rules out a choice
  of the linking variables with one MILP and searches for a usable one: 21
  points at the HPR's own values, 5 from a penalised HPR, 3 from
  best-response dynamics, out of 52 candidates run
  (`results/general-coupled/`).
* **Strict tolerance.** In 26 of the 93 files (17 without coupling rows, 9
  with) the follower's value had used BOBILib's tolerance (up to 1e-7
  relative above its optimum), and 25 of them failed the tight test of `bobi
  verify --tight`. All 26 were re-derived with the follower within 1e-9 of
  its optimum (`bobi coupled-tighten`), each leader value worse than before
  by the old slack; the superseded files are in `results/*/tolerance/`. All
  1,478 solution files of the package now pass `bobi verify --tight`
  (`results/notes/tight_verify.md`).
* **Optimal at the MIPLIB bound (6, and one published optimum confirmed).**
  The HPR of these instances is the MIPLIB problem they were built from
  (checked in exact arithmetic by `scripts/compare_hpr.py`), so its
  published optimum bounds the bilevel optimum from below. pigeon-10_0_100,
  pigeon-10_50_50 (-9,000), timtab1_0_100 (764,772) and neos-1445765_0_100
  (-17,783), all open, get points at that bound; BOBILib's own points for
  noswot_0_100 and noswot_50_50 (-41) already met it. ex10_0_100 (100, open)
  gets a point at the bound too; its optimum is credited to Lefebvre and
  Schmidt's run files, which report it, and the bound and the point confirm
  it independently (`results/notes/lefebvre_schmidt.md`).

## How the results are checked

* **Solution files.** Every file in `results/` passes `bobi verify`, which
  checks the way BOBILib's own checker does: every row and bound within
  1e-6, integrality, the stated objective, and the follower re-solved with
  the leader fixed (exact knapsack oracle for one follower row, a HiGHS
  MILP otherwise) and found optimal within BOBILib's relative 1e-4. The
  batch outputs behind this report: 270 of 270 (OR, one follower
  knapsack), 420 of 420 (OR, several), 64 of 64 (MIPLIB-derived), and all
  of the 16 subset-sum, 60 clique, 36 network and 29 coupled files.
* **Independent reviews.** The clique, network and coupled results were
  each re-derived by a separate reviewer, with its own instance reader and
  different solvers or code (its own maximum-clique searches, HiGHS and a
  hand-written branch and bound for the 3-partition bounds, a separate C
  implementation of the tree DP compared at all 9.3 M attacks). The
  reviewers found only wording errors, now fixed; their notes are in each
  `results/*/README.md`.
* **Tight re-verification.** `bobi verify --tight` holds the follower to
  max(1e-6, 1e-9 |phi|) of its proven optimum instead of BOBILib's relative
  1e-4: all 1,478 solution files pass (`results/notes/tight_verify.md`).
* **Optimality proofs** are published (cited), ours by an exact search
  whose pruning rules are proved in Lean (subset sum), arguments with
  checkable certificates (clique, rays, MIPLIB bounds), or exhaustive
  enumeration (network). The 170 part-size cases behind the density-0.9
  clique bounds each have a branch-and-bound certificate, checked by a
  short integer-only script (`scripts/check_clique_certificates.py`,
  `results/clique/certificates/`).

## Proofs in Lean

`lean/` (Lean 4 with Mathlib) proves the lemmas the new methods rest on:

* monotonicity of interdiction and the cheapest-copies count formulation;
* window extension and the stall test;
* Weninger and Fukasawa's online lower bound, for any item order;
* soundness of the robust online table, of the band tables and of both
  pruning rules; the tables with an arbitrary end set and the per-node rule
  of the subset-sum search, for any play order; antitonicity in the budget
  and the threshold (min-max) form the code stores (the range shortcuts
  inside the node-table pass and the match between the Rust loops and the
  recursion are argued in the code and tested against brute force, not
  formalised);
* for clique interdiction, Mantel's theorem in deletion form (more than
  n^2/4 edges left after deleting k means a triangle survives, checked for
  the three density-0.7 sizes) and the partition upper bound (deleting the
  edges inside an r-colouring leaves no clique on r + 1 vertices).

There is no `sorry` and no axiom beyond Lean's standard three.
`lean/README.md` maps each theorem to the code and lists what is not
formalised: scaling, the LP bracket, the search code itself, Brouwer's
stability theorem and the solver runs behind the density-0.9 bounds.

## Reproduce

```sh
cd bobilib
cargo build --release
D=data/collection
# subset-sum knapsack interdiction
./target/release/bobi ss-solve $D/interdiction/knapsack-interdiction/kp/interKP-200-100-6-3.mps.gz --out runs/ss_sol
python3 -I scripts/ss_check.py $D/interdiction/knapsack-interdiction/kp/interKP-200-100-6-3.{mps.gz,aux}
# OR set: bounds and certified points
./target/release/bobi bounds $D/interdiction/multidimensional-knapsack-interdiction/or/OR10x100-0.25_1.dat-100.mps.gz --out runs/or100
./target/release/bobi upper-multi $D/interdiction/multidimensional-knapsack-interdiction/or/OR10x250-0.75_1.dat-0.mps.gz --out runs/ormulti
# network interdiction
./target/release/bobi fire $D/interdiction/network-interdiction/inter-fire --only tree-50_1-5-5 --out results/network
# MIPLIB-derived: unbounded followers, feasible points, coupling rows
./target/release/bobi ray $D/general-bilevel/.../gen-ip054_0_100.mps.gz --out results/rays
python3 -I scripts/verify_ray.py INSTANCE.mps.gz INSTANCE.aux results/rays/gen-ip054_0_100.exact.ray.json
./target/release/bobi general $D/general-bilevel/.../mik-250-1-100-1_0_100.mps.gz --out runs/general
./target/release/bobi coupled $D/general-bilevel/.../pigeon-10_50_50.mps.gz --out runs/coupled
python3 -I scripts/compare_hpr.py INSTANCE.mps.gz INSTANCE.aux pigeon-10.mps.gz
# check any solution file the way BOBILib does
./target/release/bobi verify --instances $D results/kip results/ss results/network results/or
./target/release/bobi verify --instances $D --generic results/general results/general-coupled results/clique
```

Clique scripts and commands are in `results/clique/README.md`.

## Caveats

* "Literature" counts use the per-instance data the authors publish
  (Caprara et al.'s and Fischetti et al.'s tables, Weninger and Fukasawa's
  answer files, Fischetti et al.'s online appendix, Lozano et al.'s
  solution files). For 449 of the 531
  published optima a solution file at the published optimum is verified
  here (for the 376 knapsack interdiction optima rebuilt from Weninger and
  Fukasawa's leader choices); for the other 82, where only a value is
  published, the instance is counted as solved and no file is given.
  Each optimum is credited to its first publication among these sources
  (for knapsack interdiction, `results/literature/kip_first_publication.csv`;
  for imkp, `results/literature/imkp_first_publication.csv`). The rule
  covers only instances BOBILib lists as feasible or open; the 207 KIP and
  92 imkp instances it lists as optimal keep BOBILib as their source,
  although earlier documents give the same values.
  Lefebvre and Schmidt's run files count for one optimum (ex10_0_100),
  which a verified point and the MIPLIB bound confirm; their other reported
  optima on unsolved instances (ex10_50_50, no point known;
  mine-166-5_50_50, rejected by their own check file) are not counted.
* The 6 optima at the MIPLIB bound rest on MIPLIB's published
  floating-point optima (optimal by accepted benchmark conventions), and
  the OR lower bounds from the LP bracket on HiGHS's dual bound (with a
  safety margin); `results/instances.csv` marks such results `numerical`.
* The OR medians compare instances that have both a published lower and
  upper bound; instances without a published point are counted separately.
* Machine: 4 shared cores, often oversubscribed, so times are indicative
  only.

## Next steps

* Send the new optima, certificates and solution files to the BOBILib
  maintainers, who update statuses from submitted solutions.
* OR with several follower knapsacks: a lower bound that exploits the
  structure (the single-knapsack bracket does not carry over), and points
  for the 120 budget-25% instances without one.
* Generalized interdiction with 20 linking bits: a pruned enumeration.
