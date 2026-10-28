"""Write the pinned manifest of BOBILib's files and the copies in instances/ (maintainers only).

usage: python3 -I scripts/make_data_manifest.py --data DIR --meta collection.json
           [--manifest data-manifest/bobilib_snapshot.tsv] [--instances instances]

DIR is a local BOBILib download in BOBILib's own layout (collection/... and
collection-solutions/..., the contents of collection.tar.gz and
collection-solutions.tar.gz from bobilib.org). collection.json is BOBILib's
metadata (https://bobilib.org/subpages/collection.json); its links give the
source URL of every instance file (.mps.gz, .aux) and solution file (.res.json).

Writes, from the repository root:
  data-manifest/bobilib_snapshot.tsv   path, size, sha256, url of every file that
                                       scripts/fetch_data.py can put in data/
  instances/collection/...             unmodified copies of the .mps.gz and .aux files of
                                       the knapsack, multidimensional knapsack, clique and
                                       network interdiction instances that have a certificate
                                       or solution file in results/ (results/instances.csv)
  instances/SHA256SUMS                 sha256 of every other file in instances/
instances/LICENSE and instances/README.md are written by hand; run this script
after changing them, since SHA256SUMS covers them.

Standard library only; run with python3 -I (it reads downloaded files).
"""
import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAPSHOT_DATE = "2026-10-18"
CHECKED_DATE = "2026-10-28"
GITLAB = "https://gitlab.uni-trier.de/nlopt/bobilib-data"
COMMIT = "126eec55a94d5f665044b488efded87b61b1ef9b"  # master on both dates (2025-06-10)
META_URL = "https://bobilib.org/subpages/collection.json"
SMALL_FAMILIES = ("knapsack", "multidim-knapsack", "clique", "network")
LINK_KEYS = ("Instance file (mps)", "Instance file (aux)", "Solution file (json)")
SUFFIXES = (".mps.gz", ".aux", ".res.json")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def index(data):
    """basename -> path relative to data/ for every instance and solution file."""
    out = {}
    for top in ("collection", "collection-solutions"):
        for dp, dn, fn in os.walk(os.path.join(data, top), followlinks=True):
            dn.sort()
            for f in sorted(fn):
                if f.startswith("._") or not f.endswith(SUFFIXES):
                    continue
                rel = os.path.relpath(os.path.join(dp, f), data).replace(os.sep, "/")
                if f in out:
                    sys.exit(f"two files named {f}: {out[f]} and {rel}")
                out[f] = rel
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data", required=True, help="local BOBILib download (collection/, collection-solutions/)")
    ap.add_argument("--meta", required=True, help="BOBILib collection.json")
    ap.add_argument("--manifest", default=os.path.join(ROOT, "data-manifest", "bobilib_snapshot.tsv"))
    ap.add_argument("--instances", default=os.path.join(ROOT, "instances"))
    args = ap.parse_args()

    with open(args.meta, encoding="utf-8") as fh:
        meta = json.load(fh)
    files = index(args.data)
    rows = []
    for name in sorted(meta):
        rec = meta[name]
        for key, suffix in zip(LINK_KEYS, SUFFIXES):
            m = re.search(r'href="([^"]+)"', rec.get(key, ""))
            if not m:
                sys.exit(f"{name}: no link in {key!r}")
            url = m.group(1)
            base = name + suffix
            if not url.startswith(GITLAB + "/-/raw/master/") or not url.endswith("/" + base):
                sys.exit(f"{name}: unexpected URL {url}")
            if base not in files:
                sys.exit(f"{name}: {base} not found under {args.data}")
            p = os.path.join(args.data, files[base])
            rows.append((files[base], os.path.getsize(p), sha256(p), url))
    if len(rows) != 3 * len(meta) or len(files) != len(rows):
        sys.exit(f"{len(files)} files under {args.data}, {len(rows)} linked from collection.json")
    rows.sort()
    rows.append(("collection.json", os.path.getsize(args.meta), sha256(args.meta), META_URL))

    os.makedirs(os.path.dirname(args.manifest), exist_ok=True)
    with open(args.manifest, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(
            "# BOBILib snapshot: every file that scripts/fetch_data.py can put in data/.\n"
            "# BOBILib (https://bobilib.org) by J. Thurauf, T. Kleinert, I. Ljubic, T. K. Ralphs and\n"
            "# M. Schmidt; instances and solution files under CC BY-SA 4.0.\n"
            f"# Instance and solution files: {GITLAB},\n"
            f"# branch master, commit {COMMIT} (2025-06-10), downloaded\n"
            f"# {SNAPSHOT_DATE}; on {CHECKED_DATE} every file matched that commit's git blob ids.\n"
            f"# Metadata: collection.json from {META_URL}\n"
            f"# (Last-Modified 2026-05-27), downloaded {SNAPSHOT_DATE}.\n"
            f"# {len(meta)} instances: {len(rows) - 1} instance and solution files plus collection.json.\n"
            "# Columns: path (relative to data/), size (bytes), sha256, url.\n"
            "path\tsize\tsha256\turl\n"
        )
        for r in rows:
            fh.write("\t".join(map(str, r)) + "\n")
    print(f"{args.manifest}: {len(rows)} files, {sum(r[1] for r in rows):,} bytes")

    # ---- instances/ ------------------------------------------------------------------------------
    with open(os.path.join(ROOT, "results", "instances.csv"), encoding="utf-8") as fh:
        table = list(csv.DictReader(fh))
    pick = sorted(r["instance"] for r in table if r["certificate"] and r["family"] in SMALL_FAMILIES)
    want = set()
    for name in pick:
        for suffix in (".mps.gz", ".aux"):
            want.add(files[name + suffix])
    coll = os.path.join(args.instances, "collection")
    for dp, dn, fn in os.walk(coll):
        for f in fn:
            rel = os.path.relpath(os.path.join(dp, f), args.instances).replace(os.sep, "/")
            if rel not in want:
                os.remove(os.path.join(dp, f))
    total = 0
    for rel in sorted(want):
        src, dst = os.path.join(args.data, rel), os.path.join(args.instances, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst) or sha256(dst) != sha256(src):
            shutil.copyfile(src, dst)
        total += os.path.getsize(dst)
    sums = []
    for dp, dn, fn in os.walk(args.instances):
        for f in fn:
            rel = os.path.relpath(os.path.join(dp, f), args.instances).replace(os.sep, "/")
            if rel != "SHA256SUMS":
                sums.append((rel, sha256(os.path.join(dp, f))))
    sums.sort()
    with open(os.path.join(args.instances, "SHA256SUMS"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("".join(f"{h}  {rel}\n" for rel, h in sums))
    print(f"{args.instances}: {len(pick)} instances, {len(want)} files, {total:,} bytes; "
          f"SHA256SUMS: {len(sums)} files")


if __name__ == "__main__":
    main()
