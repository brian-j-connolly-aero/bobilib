# Published results used for the "literature" outcomes

Compiled for this work from the authors' published per-instance data; each
row cites its source. `instances.csv` takes the literature optima from
these files and, for knapsack interdiction (KIP), the values from Weninger and
Fukasawa's answer files (`../kip/`). Each published optimum is credited to its
first publication among these sources (`scripts/summarize.py`; for KIP and
imkp, `kip_first_publication.csv` and `imkp_first_publication.csv` below);
later proofs are named in the notes of `instances.csv`.

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
  Ljubić, Monaci and Sinnl's optimum for imkp (`flms2019_opt`, named after
  their 2019 paper; the values are read in Tables 4-6 of its technical report
  of 2016, which introduced the set and is their first publication, see
  `imkp_first_publication.csv`).
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

* `kip_first_publication.csv`: the first publication of each of the 376
  KIP optima that BOBILib lists as feasible or open (section below).
* `imkp_first_publication.csv`: the same for the 52 imkp optima that BOBILib
  lists as feasible (section below).

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

## kip_first_publication.csv: first publication of the KIP optima

One row for each of the 376 knapsack interdiction instances (sets `kp`,
`inter-kp`, `cclw`) that BOBILib lists as feasible or open and that have a
published optimum. `scripts/summarize.py` takes the `source` key of
`instances.csv` from `first_source`, and `paper/scripts/build_data_package.py`
writes the notes of `instances.csv` from the other columns (where the optimum
was first published, an earlier proof without a value, and the works that
proved it later). Both check every value against `../kip/summary.csv`.

**Rule.** The first publication of an optimum is the earliest publicly
available document (paper, online appendix or supplement, thesis, or a public
code repository with result files, dated by first public availability) that
reports the instance solved to proven optimality and lists its optimal value.
A listed value counts only if it equals the optimum here (`primal_value` =
`dual_bound` in `instances.csv`); all 376 do, so there is no discrepancy. An
earlier document that reports the instance proved optimal without listing its
value (for example, all instances of a group solved) is recorded in
`proved_earlier_no_value` and does not get the credit. The rule is applied
only to instances that BOBILib lists as feasible or open; those it lists as
optimal keep BOBILib (`ThuraufEtAl2026`) as their source (see "Out of scope"
below).

**Columns.**

| Column | Meaning |
| --- | --- |
| `instance`, `collection` | BOBILib name and set |
| `first_source` | key of the first publication (references below) |
| `first_public` | date of its first public availability, or for the 2016 report the dates that can be checked (see "Dates" below) |
| `first_location` | where in it: `LOCATOR: details` (table and row, or answer file, then the entries as printed) |
| `first_value` | the optimal value listed there |
| `proved_earlier_no_value` | `KEY, Table, row: count` of an earlier report without the value, or empty |
| `later_sources` | later documents, `KEY (what it reports)`, separated by `; ` |
| `notes` | name mapping, earlier runs that left the instance open, and how the row was checked (`checked:`) |

Abbreviations in the notes: CCLW (Caprara, Carvalho, Lodi and Woeginger, and
their algorithm), FLMS (Fischetti, Ljubić, Monaci and Sinnl), FMS (Fischetti,
Monaci and Sinnl), DCS (Della Croce and Scatamacchia), WF (Weninger and
Fukasawa), Comb (WF's solver), CP (Caprara et al.'s cutting-plane method),
B&C (FLMS's branch and cut), MIX++ (FischettiEtAl2017's solver), LKIP (FMS's
name for the kp set), set D (the report's name for inter-kp; INTER-KP in
FischettiEtAl2017), TRS (Tang, Richard and Smith's KIP set).

**Result.**

| Set | Rows | First publication | Where |
| --- | ---: | --- | --- |
| `cclw` | 14 | `CapraraEtAl2016` | Tables 1 and 4 (column OPT); for interdiction55-4 the value is in Table 4 and the proof in the text (a run with pre-processing, 2,796.20 CPU s). The FLMS report counts 55-4 among its 27 previously unsolved instances ("the two unsolved instances 55-3 and 55-4"), after the time-out in Caprara et al.'s Table 4; the credit stays with Caprara et al. because their text reports the proof |
| `cclw` | 1 | `FischettiEtAl2016Report` | interdiction55-3, Table 1 (z* 778, B&C 84.83 s); Caprara et al. list 778 in Table 4 without a proof |
| `inter-kp` | 25 | `FischettiEtAl2016Report` | Table 3 (set D, B&C columns); the MIX++ online appendix of 29 June 2016 (FischettiEtAl2017) left all 25 open at the time limit |
| `kp` | 336 | `WeningerFukasawa2022Code` | answer files `instances/FMS_<n>_<t>/ins<i>.ans` |

For 266 of the 336 kp rows, DellaCroceScatamacchia2020 (online 26 February
2020, Tables 3-5) had reported every instance of the group solved, as counts
per group without values. For 6 of these the group is printed as "#Opt 6/18"
although it has 6 instances; reading it as 6 of 6 is an inference (the
average time of 141.6 s, far below the limit, and WF's count of 72
previously unsolved instances both fit it). The other 70 kp rows are in groups
that DCS solved partly (42 rows; they do not say which instances) or not at
all (28). FischettiMonaciSinnl2018, which created the kp set (LKIP), says that
its optimal values are not known. No WF paper lists per-instance values: the
Optimization Online preprint of 7 October 2022 gives counts per class; the
IPCO 2023 and journal versions were read in their abstracts only, and they are
later than the repository anyway.

Later proofs: `later_sources` also names Lozano, Bergman and Cire's
`solution_files/optimal.csv` (repository DiscreteBilevelOptimization) for the
228 rows where it has LB = UB = the optimum (203 kp, 20 inter-kp, 5 cclw); the
notes of `instances.csv` name them, with the other proving works.

**Name mapping** (checked on the instance data, not only on the names):

* cclw: Caprara et al.'s (n, INS) = FLMS's "n-INS" = BOBILib
  `interdiction<n>-<INS>` = bkpsolver `instances/CCLW/CCLW_n<n>_m<INS-1>`.
  For all 15 rows the coefficients and both capacities of the BOBILib files
  equal Carvalho's instance file `Instances_INPUT.py`
  (github.com/mxmmargarida/Bileve-Knapsack, read as data) and the bkpsolver
  `.ki` file (with its trailer `ins <INS>`).
* inter-kp: the report's and the MIX++ appendix's `K50nnWkk` = BOBILib
  `K50nnWkk.KNP` = bkpsolver `instances/DeNegre/K50nnWkk.KNP.mps.ki` (nn = number
  of items, kk = instance 01-20; the same names in the COR@L library and in
  MibS's data folder). For all 25 rows the item counts, weights, capacity,
  leader costs, budget and profits of the BOBILib files equal the bkpsolver
  file.
* kp: FMS's LKIP of type t, |N| = n, INS = i = BOBILib
  `interKP-<n>-100-<t>-<i>` = bkpsolver `instances/FMS_<n>_<t>/ins<i>.ki`
  (trailer `group FMS / class <t> / ins <i>`). For all 450 kp instances both
  capacities, the multiset of items (profit, follower weight, leader cost; the
  bkpsolver files leave out the items of zero leader cost) and the trailer
  agree. DCS (2020) number the classes in the same order. The original LKIP
  files (Google Drive, sign-in required) were not compared.

**Dates of first public availability.**

* `CapraraEtAl2016`: INFORMS J. Comput. 28(2), spring 2016; the Crossref
  record was created on 11 April 2016. Read in the accepted manuscript
  (hdl.handle.net/11585/554199, in that repository since 17 July 2016); the
  same tables are in Carvalho's thesis (issued 18 April 2016).
* `FischettiEtAl2016Report`: two 2016 versions with the same Tables 1 and 3:
  a PDF created on 30 August 2016 (Sinnl's page, re-hosted; the original host
  is gone) and a PDF created on 20 December 2016 on Fischetti's DEI page
  (server Last-Modified and directory listing 21 December 2016). It is cited as
  a 2016 DEI technical report in the February 2017 report of
  FischettiMonaciSinnl2018 and on a slide of Fischetti's talk of 18 January
  2017. When the August version was first posted cannot be checked; the
  earliest Wayback capture of the DEI copy is of 8 May 2018. Either way it
  comes before every other document that proves these optima and lists their
  values: for 55-3 the next is DCS's arXiv preprint of 7 November 2018, for
  inter-kp the bkpsolver repository of 2022, for imkp the journal version of
  April 2019 and Lozano, Bergman and Cire's preprint of 2024. Before the
  August PDF, Sinnl gave talks on interdiction problems at ISCO 2016 (May; "On
  Interdiction Problems over Independence Systems", the name of the August
  file) and at EURO 2016 (July; "Decomposition Approaches for Interdiction
  Problems"), according to his talks page (msinnl.github.io/pages/talks.html). No slides
  or proceedings paper of these talks could be found (none is linked there,
  and none is in Crossref or his ORCID record), so no per-instance values
  earlier than the report are known. The univie page that the report names
  for its instances (homepage.univie.ac.at/markus.sinnl/program-codes/bilevel/)
  now redirects elsewhere, and its archived copies could not be opened, so it
  could not be checked for result files; the Google Drive copy of IMKP.zip is
  dated 6 February 2017 (download needs sign-in).
* `WeningerFukasawa2022Code`: all 434 FMS answer files (one for each of the
  450 kp instances except the 16 subset-sum instances
  `FMS_{200,300,400,500}_{6,7}/ins{2,3}` solved here, which have none), among
  them the 336 credited here, are in the initial commit d8c3b74 (author date
  6 August 2022, committed 6 October 2022 22:30 -0400) and are unchanged since. GH Archive, which records only public
  events, has a public push to the repository at 2022-10-07T21:33Z, when the
  main branch already held d8c3b74, and no event while its history was pushed
  at 02:30-02:34 UTC the same day. So the repository was public by 7 October
  2022 and very probably became public that day (GH Archive misses some
  events). The Optimization Online preprint of the same day names the
  repository. The test script of the initial commit already treats `.ans` as
  the optimal value; the README defines it from 25 October 2022.

**Sources consulted.** Caprara et al. (2016, accepted manuscript) and
Carvalho's thesis; both 2016 versions of the FLMS report; FLMS's journal
version (abstract only, see below); the MIX++ paper (Operations Research 2017,
accepted manuscript) and its online appendix of 29 June 2016; Fischetti et
al.'s intersection-cut papers (IPCO 2016 technical report, which has no
knapsack interdiction instances; Math. Program. 2018 accepted manuscript, which
reports the DeNegre knapsack interdiction set, in its class INTERDICTION, only
as counts); FMS 2018
(accepted manuscript and the technical report of February 2017); DCS's arXiv
preprint (v2 of 12 November 2018) and their 2020 paper (accepted manuscript),
with the errata in their data folder; DeNegre's thesis (2011) and DeNegre and
Ralphs (2008), which give averages for instances with at most 17 items; the
MibS paper (arXiv version); WF's Optimization Online preprint; the bkpsolver repository with
its full history and run records; Weninger's 2026 preprint; Lozano, Bergman
and Cire (2024); the BOBILib report (Section 3.1.4); Sinnl's talks page and
his ORCID record; Crossref, DataCite,
arXiv, Optimization Online and GitHub searches; papers citing FMS 2018 or
FLMS 2019 before 2023 (Semantic Scholar), none with these instances and values.

**Could not be accessed.**

* pubsonline.informs.org returns HTTP 403: the typeset IJOC 2016 article of
  Caprara et al. (the accepted manuscript was read instead) and the IJOC 2019
  article of FLMS with its online supplement. The latter is later than the
  2016 report for inter-kp, cclw and imkp. For kp it is earlier than the
  repository; that it reports no kp results is inferred from its abstract
  (360 KIP instances, which the report names as CCLW, TRS and set D, and 144
  MKIP instances) and from DCS (2020), who ran its code themselves on the 80
  kp instances with 100 items (their errata of 27 February 2020 corrects its
  time-outs there from 36 to 22).
* DCS's IPCO 2019 paper (LNCS 11480, doi:10.1007/978-3-030-17953-3_12):
  paywalled, and the institutional record has no file. It is earlier than the
  repository; its abstract is word for word that of the arXiv preprint, which
  has no kp instances, so it presumably has none (inferred).
* The EJOR version of record of FMS 2018 and any supplement (HTTP 403); the
  accepted manuscript was read and says the optimal values are not known.
* The full texts of WF's IPCO 2023 and Math. Program. papers (paywalled; both
  later than the repository).
* Web archives: the Wayback availability API worked (earliest capture of the
  DEI copy 8 May 2018; it also lists captures of the authors' univie home
  pages of November and December 2016), but the archived copies could not be
  opened (web.archive.org snapshots and its CDX API: connection reset;
  timetravel.mementoweb.org: 502; arquivo.pt: 403), so the first posting of the
  August 2016 report could not be dated; ResearchGate (403).
* Not opened: Xu and Wang (2014), Caramia and Mari (2015) and Tang, Richard
  and Smith (2016). They test their own instances, not these, as the FLMS
  report, the MIX++ paper and the Math. Program. 2018 intersection-cut paper
  describe them: TRS's knapsack interdiction instances have at most 30 items,
  and Xu and Wang's and Caramia and Mari's are general bilevel instances.

**Out of scope.** The 98 kp, 74 inter-kp and 35 cclw instances that BOBILib
lists as optimal are not in the file: their BOBILib status stands and their
source in `instances.csv` is BOBILib (`ThuraufEtAl2026`), although earlier
documents hold the same values: bkpsolver's answer files (all 207), the MIX++
online appendix of 29 June 2016 (all 74 inter-kp, gap 0.00 within the time
limit; the FLMS report's Table 3 also lists the 35 of them with 30-50 items)
and Caprara et al.'s tables (the 35 cclw). The same holds for the 92 imkp
instances BOBILib lists as optimal (below). WF's
"53 of the 72 previously unsolved instances" mixes two baselines: 53 is their
own DCS run's 69 timeouts minus Comb's 16, and 72 is the count DCS (2020)
report unsolved.

**References** (keys of `first_source`, `proved_earlier_no_value` and
`later_sources`):

* `CapraraEtAl2016`: A. Caprara, M. Carvalho, A. Lodi and G. J. Woeginger,
  Bilevel knapsack with interdiction constraints, INFORMS Journal on Computing
  28(2) (2016) 319-333, doi:10.1287/ijoc.2015.0676.
* `Carvalho2016`: M. Carvalho, Computation of equilibria on integer
  programming games, PhD thesis, Universidade do Porto (2016),
  hdl.handle.net/10216/83362.
* `FischettiEtAl2016Report`: M. Fischetti, I. Ljubić, M. Monaci and M. Sinnl,
  Interdiction games and monotonicity, technical report, DEI, University of
  Padova (2016), www.dei.unipd.it/~fisch/papers/interdiction_games_and_monotonicity.pdf
  (version of 30 August 2016: msinnl.github.io/pdfs/independentSystems-techreport.pdf).
* `FischettiEtAl2017`: M. Fischetti, I. Ljubić, M. Monaci and M. Sinnl, A new
  general-purpose algorithm for mixed-integer bilevel linear programs,
  Operations Research 65(6) (2017) 1615-1637, doi:10.1287/opre.2017.1650, and
  its online appendix of 29 June 2016 (www.dei.unipd.it/~fisch/appendix.pdf).
* `FischettiEtAl2019`: M. Fischetti, I. Ljubić, M. Monaci and M. Sinnl,
  Interdiction games and monotonicity, with application to knapsack problems,
  INFORMS Journal on Computing 31(2) (2019) 390-410, doi:10.1287/ijoc.2018.0831.
* `LozanoBergmanCire2026`: L. Lozano, D. Bergman and A. A. Cire, Network
  relaxations for combinatorial bilevel optimization under linear
  interactions, Operations Research (2026), doi:10.1287/opre.2025.2457
  (arXiv:2407.18193), and their repository
  https://github.com/andrecire/DiscreteBilevelOptimization
  (`solution_files/optimal.csv`).
* `FischettiMonaciSinnl2018`: M. Fischetti, M. Monaci and M. Sinnl, A dynamic
  reformulation heuristic for generalized interdiction problems, European
  Journal of Operational Research 267(1) (2018) 40-51,
  doi:10.1016/j.ejor.2017.11.043.
* `DellaCroceScatamacchia2018`: F. Della Croce and R. Scatamacchia, A new
  exact approach for the bilevel knapsack with interdiction constraints, arXiv
  preprint 1811.02822 (v1 7 November 2018, v2 12 November 2018).
* `DellaCroceScatamacchia2020`: F. Della Croce and R. Scatamacchia, An exact
  approach for the bilevel knapsack problem with interdiction constraints and
  extensions, Mathematical Programming 183 (2020) 249-281,
  doi:10.1007/s10107-020-01482-5.
* `WeningerFukasawa2022`: N. Weninger and R. Fukasawa, A fast combinatorial
  algorithm for the bilevel knapsack problem with interdiction constraints,
  Optimization Online preprint (7 October 2022).
* `WeningerFukasawa2022Code`: N. Weninger and R. Fukasawa, bkpsolver,
  https://github.com/nwoeanhinnogaehr/bkpsolver (answer files from the
  initial commit d8c3b74; run records `full_results/` from commit c5b7486 of
  30 July 2023).
* `WeningerFukasawa2023`: the same title, IPCO 2023, LNCS 13904, 438-452,
  doi:10.1007/978-3-031-32726-1_31.
* `WeningerFukasawa2025`: the same title, Mathematical Programming 210 (2025)
  847-879, doi:10.1007/s10107-024-02133-9.
* `Weninger2026`: N. Weninger, A simple (2+eps)-approximation for knapsack
  interdiction, arXiv preprint 2604.21877 (v2 16 October 2026).

## imkp_first_publication.csv: first publication of the imkp optima

One row for each of the 52 imkp instances that BOBILib lists as feasible and
whose optimum is published (`mkip_literature_status.csv`, `proven_optimal_in_literature`).
The other 92 imkp instances, which BOBILib lists as optimal, are not in the
file and keep BOBILib (`ThuraufEtAl2026`) as their source, although the
report's Tables 4-6 give their values earlier.
Same rule and columns as `kip_first_publication.csv` above;
`scripts/summarize.py` takes the `source` key of `instances.csv` from
`first_source`, and `paper/scripts/build_data_package.py` writes the notes
from the other columns. Every `first_value` equals `flms2019_opt` of
`mkip_literature_status.csv`, a second transcription of the same tables, and
`instances.csv` takes its value from `flms2019_opt`; so, unlike the KIP rows,
whose values are checked against verified solution files, these values are
used as published and not re-proved here. 26 of the 52 are proved again by
Lozano, Bergman and Cire (`solution_files/optimal.csv`, LB = UB = the value).
No published point or bound contradicts any of the 52 (for all 144 imkp rows
no published lower bound lies above the report's value and no published point
below it), and for the 92 imkp instances BOBILib lists as optimal the report's
value equals BOBILib's.

**Result.** All 52 go to `FischettiEtAl2016Report`, the report that
introduced the 144 imkp instances (Section 5.1, paragraph "MKIP instances
from SAC-94 library"; Section 4.1 in the August version):

* 42 are in the B&C columns of Tables 4-6 (types -100, -50 and -0) with
  %gap 0.00 and a time within the 1 h limit.
* 10 hit the limit there; their optimal values are given in the captions of
  Table 5 (weish22-50, weish27-50, weish29-50) and Table 6 (weish22-0,
  weish23-0, weish25-0 to weish29-0): "The optimal solution value (obtained
  with a larger time limit) for ... is ...". Section 5.6 (4.6 in the August
  version) reports these runs: the three -50 instances "could be solved to
  optimality within 3900 seconds", the seven -0 instances "to proven
  optimality within 19000 seconds, except weish27-0 that required about 30000
  seconds".

Both 2016 versions (30 August and 20 December) have the same 144 rows and the
same captions. Their dates are as for the KIP rows above. Nothing earlier
reports these instances: the report created them, and the MIX++ runs it
compares with were made for it (same tables; none of the 52 is solved by
MIX++ there). Sinnl's talks at ISCO 2016 and EURO 2016 came before the August
PDF, but no slides or proceedings paper could be found, and the univie
instance page the report names could not be checked for result files (see
`FischettiEtAl2016Report` under "Dates of first public availability" above).

**Name mapping.** The report's `<name>-<type>` (for example `weish22-0`) =
BOBILib `<name>.dat-<type>`, with one exception: the nine instances with two
constraints, pb4 and weing1-weing8, appear in the report only as type -100
(Table 4, one leader row and one follower row), and BOBILib stores them as
`<name>.dat-50` (it has no `.dat-100` or `.dat-0` files for them). All nine are
among the 92 that BOBILib lists as optimal, with the report's values. For all 52 rows the number of items and of
leader rows (`KL*`) and follower rows (`KF*`) of BOBILib's file equal the
row's |N|, #LC and #FC.

**Later sources.** `FischettiEtAl2019`: the journal text and supplement could
not be read (HTTP 403); its abstract mentions the 144 instances and gives no
values. `LozanoBergmanCire2026`: `solution_files/optimal.csv` has LB = UB =
the optimum for 26 of the 52; the notes of `instances.csv` name these as later
proofs.
