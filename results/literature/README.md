# Published results used for the "literature" outcomes

Compiled for this work from the authors' published per-instance data; each
row cites its source. `instances.csv` takes the literature optima from
these files and from Weninger and Fukasawa's answer files (`../kip/`). Each
published optimum is credited to its first publication among these sources
(`scripts/summarize.py`); later proofs are named in the notes of
`instances.csv`.

* `mkip_literature_status.csv`: the 954 multidimensional knapsack
  interdiction instances (sets imkp and OR). Columns: BOBILib's status and
  value at the time of writing; Lozano, Bergman and Cire's lower bound
  (`dd_lcb2026_lb`) and point (`dd_lcb2026_ub`); Lefebvre and Schmidt's
  point where published (`lefebvre_schmidt_ub`, see below) and, for
  reference only, a lower value of theirs from a run stopped at the time
  limit (`lefebvre_schmidt_ub_timelimit`), and `KO` where their own check
  file `to_check.csv` marks the instance as not bilevel feasible
  (`lefebvre_schmidt_to_check`); the best published point
  (`best_known_ub`, the minimum of Lozano et al.'s point, Lefebvre and
  Schmidt's counted point, Fischetti et al.'s optimum and BOBILib's value);
  whether the instance is proven optimal in the literature; and Fischetti,
  Ljubić, Monaci and Sinnl's 2019 optimum for imkp (`flms2019_opt`).
* `miblp_literature_status.csv`: the 266 general (MIPLIB-derived and other)
  instances BOBILib lists as feasible or open. Columns: best published
  upper and lower bounds with their sources (Fischetti et al. 2017 MIX++
  tables; Vasquez, Lozano and van Hoeve 2025; Lozano, Bergman and Cire's
  solution files; an earlier BOBILib snapshot), whether the instance is
  closed in the literature, every source's values (`sources`), and values
  re-checked with HiGHS. A closed instance is credited to the earliest source
  whose upper and lower bounds agree, by the date of its first public
  version: Fischetti et al. 2017 (`F17`), then Lozano, Bergman and Cire
  (`LBC`; arXiv preprint of July 2024), then Vasquez, Lozano and van Hoeve
  (`VLH`, 2025); an earlier BOBILib release (`BOBILib`) only where no paper
  proves the optimum. So air03-0.100000, p0201-0.100000 and p0282-0.500000
  go to Fischetti et al. (more aggressive MIX++ setting, caption of their
  Table 6), although the later proofs of the last two are also listed.
* `other_published_optima.csv`: published optima that the two tables above
  do not hold, with the place of publication (`where`) and what this package
  adds (`confirmed_here`): tree-50_1-5-5_006 and tree-50_1-5-5_010, proven
  optimal at 26 by Fischetti et al.'s MIX++ (online appendix of their 2017
  paper, Table 9) and re-proved here exactly by enumeration (`../network/`);
  and ex10_0_100, optimal at 100 in Lefebvre and Schmidt's run file
  `results-MILP.csv` (a run that ended before the time limit with value equal
  to its bound; their paper does not name the instance), confirmed here by
  the MIPLIB bound of its HPR and a verified point (`../general/`).

Lozano, Bergman and Cire's own `optimal.csv` (their repository) is not
copied here; `instances.csv` records which instances it closes.

Lefebvre and Schmidt: H. Lefebvre and M. Schmidt, A Dantzig-Wolfe
single-level reformulation for mixed-integer linear bilevel optimization:
exact and heuristic approaches, Optimization Online preprint (June 2025),
with per-instance run files on the first author's web page
(henrilefebvre.com, open-science page of the paper). Their MKIP values are
the column `lefebvre_schmidt_ub`, written by
`python3 -I scripts/ls_mkip_points.py RUN_DIR mkip_literature_status.csv`
from their four run files (`results-MILP.csv`, `results-MILP-first.csv`,
`results-PADM.csv`, `results-PADM-interdiction.csv`) with the rule of their
own analysis script: a run counts as having found a point only if it ended
before the time limit of 3,600 s, and a PADM run only if its status is
`Feasible`. Rows that hit the limit can carry relaxation values that no
bilevel feasible point has (`../notes/lefebvre_schmidt.md`); for 21 OR
instances such a value lies below the best counted published point, for 10
of them also below Lozano, Bergman and Cire's lower bound. These are kept in
`lefebvre_schmidt_ub_timelimit` and enter no comparison. The same script
writes `lefebvre_schmidt_to_check` from their `to_check.csv` (238 OR
instances marked `KO`). The counted values are published values, not
verified here. Their run files also list points for
general instances; the three that bear on whether a point of this work is the
first one anywhere (rmine6_0_100, rmine6_50_50 and neos-631710_0_100) are
recorded in `paper/scripts/build_data_package.py` (`EXTRA_PUBLISHED`) and in
the notes of `instances.csv`. Their run files report ex10_0_100 optimal at
100 from a run that ended in time; this optimum is counted as published
(`other_published_optima.csv`), credited to their run file, and the MIPLIB
bound of its HPR with a verified point at 100 (`../general/hpr_optimal.csv`)
confirms it independently. `notes/lefebvre_schmidt.md` checks all their run
files against this package.
