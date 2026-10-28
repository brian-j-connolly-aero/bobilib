# BOBILib instances used in this repository

Unmodified copies of 1,367 instances of [BOBILib](https://bobilib.org), the
Bilevel Optimization (Benchmark) Instance Library of J. Thürauf, T. Kleinert,
I. Ljubić, T. K. Ralphs and M. Schmidt: the `.mps.gz` and `.aux` files (2,734
files, 37.6 MB) of every knapsack, multidimensional knapsack, clique and
network interdiction instance that has a certificate or solution file in
`../results/` (`../results/instances.csv`, column `certificate`). They keep
BOBILib's own directory layout, so `instances/collection/...` is the same path
as `data/collection/...` in a full BOBILib download.

| Folder under `collection/interdiction/` | Instances | Size | Results |
| --- | ---: | ---: | --- |
| `knapsack-interdiction/cclw` | 50 | 0.14 MB | `../results/kip` |
| `knapsack-interdiction/inter-kp` | 99 | 0.24 MB | `../results/kip` |
| `knapsack-interdiction/kp` | 450 | 8.7 MB | `../results/kip` (434), `../results/ss` (16) |
| `multidimensional-knapsack-interdiction/or` | 672 | 23.6 MB | `../results/or` |
| `clique-interdiction/clique` | 60 | 4.8 MB | `../results/clique` |
| `network-interdiction/inter-fire` | 36 | 0.21 MB | `../results/network` |
| total | 1,367 | 37.6 MB | |

## Why they are here

So that the results for these families can be checked from a clone of this
repository, without downloading anything. For example, from the repository root:

```sh
cargo build --release
target/release/bobi verify --instances instances/collection/interdiction/knapsack-interdiction results/kip
python3 -I scripts/check_clique_certificates.py instances/collection/interdiction/clique-interdiction/clique \
  results/clique/certificates
```

## What is not here, and how to get it

* the 136 general bilevel instances with results in `../results/general`,
  `../results/general-coupled` and `../results/rays` (229 MB);
* BOBILib's own solution files (`.res.json`), its metadata (`collection.json`)
  and the other 1,151 instances (the whole library is 1.45 GB).

`scripts/fetch_data.py` builds `data/` from this folder and downloads the rest
from BOBILib, checking every file against the pinned manifest
`../data-manifest/bobilib_snapshot.tsv`; from the repository root:

```sh
make fetch-data                    # the 1,503 instances the results use, about 285 MB
make fetch-data SUBSET=all         # all 2,654 instances
```

See `../README.md`, section "Getting the data". The whole library, in archives
per family, is also on the Downloads page of https://bobilib.org.

## Source

* Work: BOBILib, https://bobilib.org.
* Files: https://gitlab.uni-trier.de/nlopt/bobilib-data, branch master, commit
  `126eec55a94d5f665044b488efded87b61b1ef9b` (2025-06-10), downloaded 2026-10-18.
* Every file here is byte-identical to the file at its URL in
  `../data-manifest/bobilib_snapshot.tsv` (checked on 2026-10-28 against the git
  blob ids of that commit). No file was changed or renamed.
* BOBILib collects instances from earlier papers; the BOBILib paper credits the
  original source of each set (cclw, inter-kp, kp, or, clique, inter-fire).

## Citation

If you use these instances, cite BOBILib:

> J. Thürauf, T. Kleinert, I. Ljubić, T. K. Ralphs and M. Schmidt. BOBILib:
> Bilevel Optimization (Benchmark) Instance Library. *Mathematical Programming
> Computation* 18(3):819–876, 2026. https://doi.org/10.1007/s12532-025-00294-y

```bibtex
@article{thurauf2026bobilib,
  author  = {Th{\"u}rauf, Johannes and Kleinert, Thomas and Ljubi{\'c}, Ivana and Ralphs, Ted K. and Schmidt, Martin},
  title   = {{BOBILib}: {Bilevel Optimization (Benchmark) Instance Library}},
  journal = {Mathematical Programming Computation},
  volume  = {18},
  number  = {3},
  pages   = {819--876},
  year    = {2026},
  doi     = {10.1007/s12532-025-00294-y}
}
```

and the paper that introduced each set you use.

## License

BOBILib's authors license its instances under the Creative Commons
Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0; BOBILib paper,
Section 6). These copies are redistributed under the same license; `LICENSE`
holds its legal code. Anyone sharing them must keep the attribution above and
the license, and license adapted versions under CC BY-SA 4.0 too. This README
and `SHA256SUMS` are also under CC BY-SA 4.0. The rest of the repository is
licensed separately (code: MIT, `../LICENSE`; data package: CC BY 4.0,
`../results/LICENSE`).

## Checking the copies

```sh
cd instances && sha256sum -c --quiet SHA256SUMS
```

`SHA256SUMS` lists every other file in this folder. It and the copies are
written by `../scripts/make_data_manifest.py` (maintainers only), which also
writes the manifest from a local BOBILib download and `collection.json`.
