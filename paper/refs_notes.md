# refs.bib: what each entry supports

One line per BibTeX key in `refs.bib` (85 entries), grouped as in the file.
"Checked" says how the bibliographic data were confirmed. "Crossref" means the
DOI's Crossref record matched authors, title, volume, issue, pages and year.

## The library and the solvers behind its statuses

- `thurauf2026bobilib`: BOBILib itself (2,654 instances, file format, statuses from MibS and MIX++ with a 1 h limit, families and their sources, 1e-4 tolerances; pp. 829-830: without coupling constraints a feasible MILP relaxation is "technically enough to conclude the instance is feasible"). MPC 18(3) 819-876 (2026), online 21 Mar 2026, open access. Checked: Crossref, the Springer landing page and the open-access PDF (read 28 Oct 2026).
- `bobilib_website`: bobilib.org, the source of the status data, solution files and feasibility checker used here (accessed 18 Oct 2026). Checked: site title fetched.
- `tahernejad2020mibs`: MibS, one of BOBILib's two solvers; the general branch-and-cut framework. Checked: Crossref.
- `mibs_software`: the MibS code (BOBILib ran version 1.2.2). Authors and year as in BOBILib's own reference list. Checked: URL as cited by BOBILib and Tahernejad-Ralphs; GitHub is not reachable from this machine.
- `denegre2009branch`: first branch-and-cut for integer bilevel programs; history in the introduction. Checked: Crossref and the Springer page (editors, ORCS vol. 47).
- `denegre2011thesis`: DeNegre's thesis; source of the inter-assig, inter-kp and denegre sets. Checked: PDF title page (Lehigh University, May 2011).
- `fischetti2017new`: MIX++ (BOBILib's second solver); source of xularge; first published optima of air03-0.100000, p0201-0.100000 and p0282-0.500000 (caption of Table 6, "more aggressive setting"; accepted manuscript, hdl.handle.net/11585/611023, read 28 Oct 2026) and of the two inter-fire trees (via its online appendix). Checked: Crossref.
- `fischetti2016appendix`: the online appendix of `fischetti2017new` (cited there as Fischetti et al. 2016a, same URL), dated 29 June 2016; Table 9 gives tree-50-1-5-5-006 and -010 at BestSol 26 = LB 26 (2,120.85 s and 1,702.69 s); the appendix gives no thread count, and the run setting (4 threads, 3,600 s wall-clock limit) is stated in Section 7 of `fischetti2017new` (accepted manuscript). No DOI. Checked: PDF downloaded 28 Oct 2026 from www.dei.unipd.it/~fisch/appendix.pdf.
- `mixpp_software`: page distributing the MIX++ binary and the instance sets. Checked: page fetched.
- `fischetti2016intersection`: intersection cuts (IPCO 2016); source of the miplib3 set. Checked: Crossref and Springer page (LNCS 9682, editors Louveaux and Skutella).
- `fischetti2018intersection`: journal version; also a source of the miplib3 set. Checked: Crossref.

## Knapsack, multidimensional knapsack and generalized interdiction

- `fischetti2019interdiction`: interdiction games and monotonicity; source of the imkp and OR sets; solved all 144 imkp; interdiction cuts behind the MKIP master. No optimum is credited to it (first-publication rule, Supp. Sec. H.2): its 2016 technical report, `fischetti2016monotonicity`, is the first publication of 26 KIP optima and of the 52 imkp optima that BOBILib lists as feasible. The journal text and online supplement could not be read (pubsonline.informs.org returns HTTP 403); its abstract was read on the Bologna and WU Vienna records. Checked: Crossref.
- `fischetti2016monotonicity`: the technical report of `fischetti2019interdiction`; first publication of 26 KIP optima (`results/literature/kip_first_publication.csv`): Table 3 (set D = inter-kp, B&C columns) for the 25 inter-kp optima and Table 1 for interdiction55-3 (z* 778, B&C 84.83 s); and of the 52 imkp optima (`results/literature/imkp_first_publication.csv`; the report introduced the 144 imkp instances): Tables 4-6, 42 in the B&C columns (gap 0.00 within 1 h) and 10 in the captions of Tables 5 and 6 ('the optimal solution value (obtained with a larger time limit)'; Section 5.6 reports these runs solved to optimality). Two versions: PDF created 30 Aug 2016 (msinnl.github.io/pdfs/independentSystems-techreport.pdf, re-hosted) and PDF created 20 Dec 2016 (www.dei.unipd.it/~fisch/papers/interdiction_games_and_monotonicity.pdf, server Last-Modified 21 Dec 2016), with identical Tables 1, 3, 4, 5 and 6 (and captions); the first posting of the August version could not be dated (the Wayback availability API lists captures of the authors' univie pages from Nov and Dec 2016, but the archived copies could not be opened); Sinnl's talks at ISCO 2016 (May) and EURO 2016 (July) came earlier, but no slides or proceedings paper could be found (none in Crossref or his ORCID record). No DOI: a Crossref title query returns only the journal version. Checked: both PDFs downloaded and read 28 Oct 2026, twice (first study and verification).
- `fischetti2018dynamic`: generalized interdiction set, the kp set (450, item classes 6 = subset sum and 7 = even-odd subset sum), plusbcpins and the 60 clique instances. Its accepted manuscript (Bologna IRIS 11585/623006, Sect. 6.4) says the optimal values of the kp instances (its LKIP) are not known; the version of record and any supplement could not be read (sciencedirect.com returns HTTP 403), which Supp. Sec. B.9 states. Checked: Crossref.
- `caprara2014complexity`: Sigma_2^p-completeness of bilevel knapsack (why KIP is hard). Checked: Crossref.
- `caprara2016bilevel`: the KIP model and the cclw set; first publication of 14 cclw optima (Tables 1 and 4, column OPT; interdiction55-4: value in Table 4, proof in the text of Section 5.1, a run with pre-processing of 2,796.20 CPU s). It lists 778 for interdiction55-3 without a proof. Read in the accepted manuscript (hdl.handle.net/11585/554199); the typeset version could not be read (HTTP 403). Checked: Crossref (record created 11 Apr 2016, issue 28(2)).
- `dellacroce2020exact`: the DCS exact algorithm for KIP (prior state of the art); its Tables 3-5 report 266 of the 336 kp optima solved earlier, as counts per group without values ("proved earlier, value not listed"; for 6 of them this assumes that the misprinted "#Opt 6/18" means 6 of 6); a later proof of the cclw optima (times only). Read in the accepted manuscript (PoliTo). Checked: Crossref (online 26 Feb 2020).
- `dellacroce2019lower`: the IPCO 2019 version of the DCS algorithm (LNCS 11480, editors Lodi and Nagarajan); earlier than the kp answer files, but its full text could not be read (paywalled; the institutional record has no file). Its abstract is the same as that of their arXiv preprint 1811.02822, which has no kp instances. Cited where the paper names the sources it could not read. Checked: Crossref (chapter record: title, authors, pages 155-167, 2019; book record: editors) and the Springer chapter page (volume 11480).
- `weninger2023fast`: Weninger-Fukasawa, IPCO 2023 (LNCS 13904, editors Del Pia and Kaibel). Checked: Crossref and Springer page.
- `weninger2025fast`: journal version, Math. Program. 210 (2025) 847-879; the method behind the answer files of `weninger_bkpsolver`; the online lower bound and greedy heuristic used here. No optimum is credited to it (first-publication rule, Supp. Sec. H.2: its per-instance values are in the repository, which came first). Full text paywalled; abstract read. Checked: Crossref.
- `weninger2022fast`: the Optimization Online preprint of `weninger2023fast` and `weninger2025fast`, published 7 Oct 2022 (landing page, "Published: 2022/10/07"; PDF bkp.pdf, Last-Modified 7 Oct 2022); it names the repository and gives counts per class only (Tables 2 and 3), no per-instance values. No DOI (Crossref title query returns only the IPCO and journal versions). Checked: landing page fetched 28 Oct 2026 and the PDF read.
- `weninger_bkpsolver`: their code and answer files; first publication of the 336 kp optima (answer files `instances/FMS_<n>_<t>/ins<i>.ans`, all in the initial commit d8c3b74, unchanged since; the repository was public by 2022-10-07T21:33Z per GH Archive and very probably became public that day, so the entry has year 2022); the 40 inter-kp and cclw answer files are later than their first publications; the run records (`full_results/`, commit c5b7486, 30 Jul 2023) give the leader vectors of `results/kip/`; commit 1838efe (4 May 2023) merges identical items into counted copies (now option `-dedup`) and plays the online DP over copy counts; commit bc1d985 (3 Aug 2026, HEAD on 28 Oct 2026) adds symmetry breaking by item dominance, "not described in the paper" (README). Checked: URL printed in their paper; repository cloned 28 Oct 2026 with its full history.
- `weninger2026approx`: Weninger, (2+eps)-approximation for knapsack interdiction, arXiv 2604.21877 (v1 23 Apr 2026, v2 16 Oct 2026): the dual form of the follower LP minimised over (x, alpha), Proposition 3 (OPT_I >= OPT_F - p*, the m = 1 case of the LP bracket), the t-row dual form, and "16 of them time out after one hour" for the 100 subset-sum instances. DataCite DOI (not in Crossref). Checked: arXiv abstract page and v2 PDF; the DOI resolves to the abstract page. Re-checked 28 Oct 2026: v2 (submitted 16 Oct, listed 19 Oct) is still the latest version and its PDF is byte-identical to the copy read. The README of the author's code repository (github.com/nwoeanhinnogaehr/ki-approx, created 19 Oct 2026; Rust source only, no result files) says the paper will appear in the SOSA 2027 proceedings; no accepted-papers list confirming this was found.
- `lozano2026network`: Lozano, Bergman, Cire, decision-diagram network relaxations ("lbc"/"LBC" in the scratch notes): 87 OR + 4 generalized + 4 MIPLIB 3 literature optima (p0201-0.100000, also in their data, is credited to its first publication, `fischetti2017new`) and the published OR bounds; the arXiv v1 of 25 Jul 2024, Table 2, already closes p0282-0.9, which `vasquez2025single` closes later. Operations Research, Articles in Advance, online 26 Aug 2026, no volume yet. The arXiv version (2407.18193) had the title "... Discrete Bilevel Optimization ...". Checked: Crossref and the repository README.
- `lozano_dbo_repo`: their solution files (optimal and improved BOBILib points) read by the reconciliation; `solution_files/optimal.csv` also gives the later proofs of 228 KIP and 26 imkp optima named in the data package (LB = UB = the optimum). Checked: repository cloned earlier; README names the paper and DOI.
- `vasquez2025single`: Vasquez, Lozano, van Hoeve, decision-diagram single-level reformulation; re-proves the p0201-0.100000 and p0282-0.500000 optima first published in `fischetti2017new` (named in the notes of `instances.csv`; no optimum is credited to this paper); a published point for cap6000-0.500000. Math. Program., online first 16 Dec 2025, no volume yet. Checked: Crossref and Springer page.
- `martello1999dynamic`: the knapsack instance generator behind cclw and kp (item classes), and the combo algorithm. Checked: Crossref.
- `dantzig1957discrete`: the greedy LP (Dantzig) bound used in the exact knapsack oracle (`src/kp.rs`) and the fractional deletion bound (Supp. Lemma B.7). Checked: Crossref.
- `brown1961note`: Brown's criterion for complete sequences of integers, the classical form of the window-extension lemma (Supp. Lemma B.5). Amer. Math. Monthly 68(6), 1961. Checked: Crossref (first page 557; the range 557-560 from the JSTOR listing as cited on Wikipedia's "Complete sequence" page).
- `martello1990knapsack`: standard knapsack reference (LP bound, dynamic programming). Book, no DOI; ISBN 0-471-92420-2. Checked: library catalogue records.
- `chu1998genetic`: the Chu-Beasley multidimensional knapsacks underlying the 810 OR instances. Checked: Crossref.
- `beasley1990orlibrary`: OR-Library, where the Chu-Beasley instances are distributed. Checked: Crossref.
- `khuri1994zero`: SAC-94 multidimensional knapsack suite underlying imkp. Checked: Crossref.

## Clique and network interdiction

- `tang2016class`: Tang-Richard-Smith; the bcpins edge clique interdiction instances; also the source of the TRS knapsack interdiction set that `fischetti2016monotonicity` counts among its 360 KIP instances (Supp. Sec. B.9; not a BOBILib set). Checked: Crossref (online 2015, issue 2016).
- `furini2019maximum`: maximum (vertex) clique interdiction, related work. Checked: Crossref.
- `furini2021branch`: exact branch and cut for the edge interdiction clique problem (BOBILib's clique family is this problem); related work, its Proposition 2 (deletions needed to bring a clique K_q below size l, after `hassan2018clique`) and its note on the n = 40-60 instances (ER graphs with budgets up to 20%). Checked: Crossref.
- `hassan2018clique`: Hassan, Kacem, Martin, Osman, J. Comb. Optim. 36(3) 1074-1101 (2018); source of Furini et al.'s Proposition 2. Checked: Crossref.
- `zhou2026exact`: Zhou, Jiang, Zhu, Rossi, RLCM exact method for edge clique interdiction (arXiv 2601.01869, 5 Jan 2026; EJOR, in press, no volume yet); uses Turan's theorem; random graphs with n in {25, 50, 75, 100} and budgets up to 20% of the edges. Checked: Crossref (Aug 2026) and the arXiv full text.
- `baggio2021multilevel`: multilevel critical node (attack-protect) problem; source of inter-fire. Checked: Crossref.
- `smith2020survey`: survey of network interdiction; applications in the introduction. Checked: Crossref.
- `brown2006defending`: defending critical infrastructure; defence applications in the introduction. Checked: Crossref.

## Bilevel optimization background and other methods

- `stackelberg1934marktform`: the leader-follower game. The entry is the 2011 English translation (*Market Structure and Equilibrium*, Springer, doi 10.1007/978-3-642-12586-7), with the 1934 original in the note, so that the DOI prints like every other DOI. Checked: Crossref (title, author, 2011, Springer Berlin Heidelberg) and the Springer page of the translation; publisher and year of the original from catalogue/secondary records.
- `moore1990mixed`: first MIBLP branch and bound; the high point relaxation. Checked: Crossref.
- `jeroslow1985polynomial`: complexity of multilevel programs (Sigma_2^p). Checked: Crossref.
- `dempe2002foundations`: textbook on bilevel programming (background). Checked: Crossref and Springer page.
- `kleinert2021survey`: survey of MIP techniques in bilevel optimization (background, optimistic convention). Checked: Crossref.
- `kleinert2021computing`: PADM; source of the miplib2010 and miplib2017 bilevel sets; the `padm` method of the coupled portfolio. Checked: Crossref.
- `mitsos2010global`: value-function (bounding) cuts, the `vcut` method of the coupled portfolio. Checked: Crossref.
- `lozano2017value`: value-function-based exact approach, also behind `vcut`. Checked: Crossref.
- `xu2014exact`: Xu-Wang algorithm; source of the xuwang set; its Lemma 2 (a follower unbounded for one leader choice makes the bilevel problem infeasible), extended by Theorem 1 of `fischetti2018intersection`. Checked: Crossref.
- `caramia2015enhanced`: Caramia-Mari, Optimization Letters 9(7) 1447-1468 (2015); named in Supp. Sec. B.9 only as a paper that was not opened in the first-publication check (it tests its own general integer bilevel instances, as Fischetti et al.'s intersection-cut paper of 2018 describes them). Checked: Crossref (title query, 28 Oct 2026: authors, title, volume, issue, pages, online 3 Apr 2015).
- `ozaltin2017branch`: Ozaltin-Zhang; source of the zhang set. Checked: Optimization Online page (published 2017/05/16).
- `rodrigues2026unboundedness`: Rodrigues, Carvalho, Anjos, Sugishita, unboundedness in bilevel optimization (complexity; algorithms tested on LP relaxations of BOBILib instances with the bounds removed; urges unboundedness checks and certificates). Math. Program., online 26 Mar 2026, no volume yet. Crossref's title has the typo "Builevel"; the entry uses the correct spelling. Checked: Crossref and the Optimization Online preprint (Feb 2025).
- `meyer1974existence`: rational MILPs that are feasible and bounded attain their optimum; basis of the recession-ray certificates (no bilevel feasible point when the follower is unbounded). Checked: Crossref.

## Extremal graph theory (clique lower bounds)

- `mantel1907problem`: Mantel's theorem (triangle-free graphs have at most floor(n^2/4) edges); value >= 3 for all 60 clique instances. No DOI or online copy; details agree in two published reference lists (Borg-Fenech, Australas. J. Combin. 78 (2020); Korandi-Roberts-Scott 2021).
- `turan1941extremal`: Turan's theorem (t_r(n)); thresholds in the clique argument. No DOI; volume 48, pages 436-452 as in most published reference lists (one Springer list gives 436-453).
- `brouwer1981lotto`: Brouwer's Theorem 2 (K4-free with at least t_3(n) - floor(n/3) + 2 edges implies 3-partite, n >= 7); value >= 4 at density 0.9. Checked: CWI repository record and the scanned report (ZW 152/81, March 1981).
- `tyomkyn2015strong`: restatement of Brouwer's theorem (their eq. (1) and Theorem 1.1), crediting Brouwer. Checked: Crossref and the arXiv full text.
- `korandi2021exact`: restatement in complemented form (Theorem 1.1), cited in the appendix. Checked: Crossref; Advances in Combinatorics 2021:9, 17 pp.
- `amin2013non`: maximum size of non-(p-1)-partite maximal K_p-free graphs; an independent cross-check of Brouwer's threshold. Checked: Crossref (first page) and the journal/DOAJ record (pages 9-23).
- `babai1990extremal`: largest K_{r+1}-free subgraphs of G(n,1/2) are r-partite (context for the 3 open clique instances). Checked: Crossref.
- `brightwell2012extremal`: the same for sparser random graphs. Checked: Crossref.

## Maximum clique algorithms (solution checks)

- `bron1973algorithm`: Bron-Kerbosch, one of the two exact clique searches in `checksol.py`. Checked: Crossref.
- `tomita2006worst`: Tomita pivoting used with Bron-Kerbosch. Checked: Crossref.
- `carraghan1990exact`: Carraghan-Pardalos, the second exact clique search. Checked: Crossref.

## MIPLIB

- `gleixner2021miplib`: MIPLIB 2017; source models of the miplib2017 set, published optima used as HPR bounds (solution file miplib2017-v37.solu, Last-Modified 24 Sep 2026, re-read 28 Oct 2026: noswot, pigeon-10, timtab1, ex10, neos-1445765 and neos-950242 unchanged), and the solution checker BOBILib's verification builds on. Checked: Crossref.
- `koch2011miplib`: MIPLIB 2010; source models of the miplib2010 set. Title as in the Crossref and Springer metadata ("MIPLIB 2010"); BOBILib's list adds the subtitle "Mixed integer programming library version 5". Checked: Crossref and the Springer page.
- `bixby1998miplib`: MIPLIB 3.0 (Optima 58, 12-15); source models of the miplib3 set. Checked: MIPLIB 3 page and the MIPLIB site's BibTeX record.

## Software used here

- `huangfu2018parallelizing`: HiGHS (version 1.15.1 here), the MILP/LP solver throughout; the citation HiGHS asks for. Checked: Crossref and highs.dev.
- `hojny2025scip`: SCIP Optimization Suite 10.0 (SCIP 10.0 via PySCIPOpt 6.3.0 here), used in the clique proofs and the OR10x100-0.75_4 check. Entry copied from scipopt.org's BibTeX (Optimization Online, Nov 2025, 28 authors). The arXiv version 2511.18580 lists 35 authors.
- `maher2016pyscipopt`: PySCIPOpt, the Python interface used to call SCIP. Checked: Crossref and Springer page (LNCS 9725).
- `perron2026cpsat`: OR-Tools CP-SAT (version 9.15, released Jan 2026), used in the clique proofs and searches. Software citation as requested on the OR-Tools "How to cite" page, with the version updated.
- `moura2021lean`: Lean 4 (toolchain v4.35.0 here). Checked: Crossref and Springer page (LNCS 12699).
- `mathlib2020`: Mathlib (v4.35.0 here). Checked: Crossref.

## Added in the review round

- `lefebvre2025dantzig`: Lefebvre and Schmidt, Dantzig-Wolfe single-level reformulation; source of published OR points (`lefebvre_schmidt_ub` in `results/literature/mkip_literature_status.csv`), of three published points for general instances (`EXTRA_PUBLISHED` in `scripts/build_data_package.py`) and of one published optimum, ex10_0_100 (run file `results-MILP.csv`, line 682; `results/literature/other_published_optima.csv`). Optimization Online preprint, June 2025 (latest version read: 20 July 2026); per-instance run files on henrilefebvre.com. Checked: Optimization Online page (title, authors) and the preprint's title page.
- `wood1993deterministic`: classical duality-based single-level reformulation in network interdiction (prior art for the LP bracket). Checked: Crossref.
- `israeli2002shortest`: the same, shortest-path interdiction. Checked: Crossref.
- `glover1968surrogate`: surrogate constraints, the merging of the leader rows in the merged-row online bound. Checked: Crossref.
- `kellerer2004knapsack`: knapsack textbook; a basic LP solution of a multidimensional knapsack has at most as many fractional variables as rows (prior art for the m*p_max gap). Checked: Crossref (book, Springer Berlin Heidelberg, 2004).
- `cheung2017verifying`: VIPR certificates for MILP results (remedy for trusted solvers). Checked: Crossref (pages 148-160, LNCS 10328, editors Eisenbrand and Koenemann).
- `eifler2023computational`: exact rational MIP in SCIP. Checked: Crossref (Math. Program. 197(2) 793-812; online January 2022, issue 2023).
- `bogaerts2023certified`: VeriPB proof logging for optimisation (also maximum clique). Checked: Crossref (JAIR 77) and the JAIR/arXiv record for pages 1539-1589.
- `mahdavipajouh2020minimum`: the minimum cost edge blocker clique problem, the decision version behind the open clique instances. Checked: Crossref (Ann. Oper. Res. 294(1-2) 345-376; online 2019, issue 2020).
- `hanson1991ksaturated`: rediscovery of Brouwer's theorem. No DOI; details agree in the reference lists of Tyomkyn-Uzzell (2015) and Korandi-Roberts-Scott (2021).
- `kang2005maximum`: rediscovery of Brouwer's theorem. No DOI; details agree in the same two reference lists.
- `tyomkyn2015strong` (existing key) now also supports the refereed proof of Brouwer's theorem (their Theorem 1.1, proved in their Section 2), and `amin2013non` the same threshold for maximal K_p-free graphs (their Theorem 14).

## Not verified

None. No entry carries `note = {unverified}`. Two entries rest on published
secondary citations only, because the originals are not online:
`mantel1907problem` and `turan1941extremal`. Their details agree across the
reference lists consulted.

## Notes for the writer

- Plain `unsrt` prints neither `doi` nor `url`. For the SPIE-style list with DOIs
  use a style that prints them (for example `unsrtnat` with natbib's
  `numbers,super` options, or a custom SPIE-format style), and load `url` (or
  `hyperref`) for the `~` and `_` in URLs and DOIs.
- Article titles are stored in sentence case with proper nouns braced, so styles
  that lowercase titles keep "BOBILib", "MIPLIB", "Lean", "SCIP", "Turan".
- Web pages carry "Accessed 18 October 2026" in `note`.

## Re-checking and compile test

The `.bib` is curated by hand; nothing generates it. To compile-test it:

```
mkdir /tmp/bibtest && cp refs.bib /tmp/bibtest && cd /tmp/bibtest
printf '%s\n' '\documentclass{article}\usepackage{mathptmx}\usepackage[super]{cite}\usepackage{url}' \
  '\begin{document}x\nocite{*}\bibliographystyle{unsrt}\bibliography{refs}\end{document}' > t.tex
pdflatex t && bibtex t && pdflatex t && pdflatex t     # 64 items, 0 BibTeX warnings
```

The same document with `unsrtnat` also builds with 0 warnings and prints every
DOI and URL. To re-check the data, look up each `doi` at
`https://api.crossref.org/works/<doi>` and compare authors, title, volume,
number, pages and year.
