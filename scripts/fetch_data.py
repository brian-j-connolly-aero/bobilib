"""Build data/ (BOBILib's instance files, solution files and metadata) and verify every file.

usage: python3 -I scripts/fetch_data.py [--subset used|unsolved|all] [--dest DIR]
           [--verify-only] [--jobs N] [--local DIR ...] [--ref COMMIT]

data/ gets BOBILib's own layout, which the code and scripts of this repository expect:
  data/collection/<class>/<family>/<set>/NAME.mps.gz, NAME.aux     instance files
  data/collection-solutions/.../NAME.res.json                      BOBILib's solution files
  data/collection.json                                             BOBILib's metadata
Subsets (instances of results/instances.csv):
  used      the 1,503 instances with a certificate or solution file in results/ (default;
            about 285 MB, of which 38 MB come from instances/)
  unsolved  the 1,594 instances BOBILib lists as feasible or open (about 970 MB)
  all       all 2,654 instances (about 1.45 GB)
Every subset also gets collection.json. Each file is taken, in this order, from DIR if it
is already there, from the copies in instances/, from each --local DIR (an existing BOBILib
download in the same layout, e.g. collection.tar.gz and collection-solutions.tar.gz from
bobilib.org unpacked into one folder), and otherwise downloaded from the URL in the
manifest. Every file is checked against data-manifest/bobilib_snapshot.tsv (size and
sha256); a file whose checksum differs is not installed and is reported (BOBILib changed
upstream: try --ref with the commit named in the manifest). Exit status 0 only if every
selected file is present and verified.

GitLab allows unauthenticated clients about 3,600 requests per hour; the script waits
when it is told to (HTTP 429) and retries failed downloads a few times. --subset all
needs about 5,200 downloads beyond instances/, so it is faster from the tarballs (--local).

Standard library only, Python 3.10 or later. Run with python3 -I.
"""
import argparse
import csv
import hashlib
import http.client
import os
import shutil
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "data-manifest", "bobilib_snapshot.tsv")
INSTANCES = os.path.join(ROOT, "instances")
TABLE = os.path.join(ROOT, "results", "instances.csv")
SUFFIXES = (".mps.gz", ".aux", ".res.json")
MAX_JOBS = 4
RETRIES = 4  # attempts per file; waits of 5, 15 and 45 s between them (longer if told to)
USER_AGENT = "bobilib-fetch-data/1 (+https://github.com/brian-j-connolly-aero/bobilib)"


class TooLarge(Exception):
    pass


class Entry:
    __slots__ = ("path", "size", "sha256", "url")

    def __init__(self, path, size, sha, url):
        self.path, self.size, self.sha256, self.url = path, size, sha, url


def read_manifest(path):
    out = []
    with open(path, encoding="utf-8") as fh:
        lines = [ln.rstrip("\n") for ln in fh if not ln.startswith("#") and ln.strip()]
    if not lines or lines[0].split("\t") != ["path", "size", "sha256", "url"]:
        sys.exit(f"{path}: missing header 'path size sha256 url'")
    for ln in lines[1:]:
        p, size, sha, url = ln.split("\t")
        parts = p.split("/")
        if p.startswith("/") or ".." in parts or "" in parts or "\\" in p:
            sys.exit(f"{path}: unsafe path {p!r}")
        out.append(Entry(p, int(size), sha, url))
    return out


def instance_name(path):
    base = path.rsplit("/", 1)[-1]
    for s in SUFFIXES:
        if base.endswith(s):
            return base[: -len(s)]
    return None


def select(entries, subset):
    if subset == "all":
        return entries
    with open(TABLE, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if subset == "used":
        names = {r["instance"] for r in rows if r["certificate"]}
    else:
        names = {r["instance"] for r in rows if r["bobilib_status"] in ("feasible", "open")}
    known = {instance_name(e.path) for e in entries}
    if names - known:
        sys.exit(f"{len(names - known)} instances of {TABLE} are not in the manifest, e.g. "
                 f"{sorted(names - known)[0]}")
    return [e for e in entries if instance_name(e.path) in names or e.path == "collection.json"]


def digest(path):
    h = hashlib.sha256()
    n = 0
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
            n += len(chunk)
    return n, h.hexdigest()


def matches(path, e):
    """None if path is missing, else whether its size and sha256 are e's."""
    if not os.path.isfile(path):
        return None
    if os.path.getsize(path) != e.size:
        return False
    return digest(path) == (e.size, e.sha256)


class Fetcher:
    def __init__(self, dest, locals_, ref):
        self.dest, self.locals, self.ref = dest, locals_, ref
        self.lock = threading.Lock()
        self.pause_until = {}  # host -> monotonic time before which no request is sent
        self.count = {"present": 0, "instances/": 0, "local": 0, "downloaded": 0}
        self.bytes_down = 0
        self.failed = []  # (path, reason)
        self.done = 0

    def url(self, e):
        if self.ref and "/-/raw/master/" in e.url:
            return e.url.replace("/-/raw/master/", f"/-/raw/{self.ref}/", 1)
        return e.url

    def note(self, key, e, nbytes=0):
        with self.lock:
            self.count[key] += 1
            self.bytes_down += nbytes
            self.done += 1

    def fail(self, e, reason):
        with self.lock:
            self.failed.append((e.path, reason))
            self.done += 1

    def wait_turn(self, host):
        while True:
            with self.lock:
                left = self.pause_until.get(host, 0.0) - time.monotonic()
            if left <= 0:
                return
            time.sleep(min(left, 5.0))

    def pause(self, host, seconds):
        with self.lock:
            until = time.monotonic() + seconds
            self.pause_until[host] = max(self.pause_until.get(host, 0.0), until)

    def download(self, e, target):
        tmp = target + ".part"
        url = self.url(e)
        host = urllib.parse.urlsplit(url).netloc
        last = "no attempt"
        for attempt in range(RETRIES):
            self.wait_turn(host)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                h = hashlib.sha256()
                n = 0
                with urllib.request.urlopen(req, timeout=60) as r, open(tmp, "wb") as out:
                    while True:
                        chunk = r.read(1 << 16)
                        if not chunk:
                            break
                        if n + len(chunk) > e.size:
                            raise TooLarge(f"larger than the manifest's {e.size} bytes")
                        out.write(chunk)
                        h.update(chunk)
                        n += len(chunk)
                if (n, h.hexdigest()) != (e.size, e.sha256):
                    os.remove(tmp)
                    return (f"checksum differs from the manifest (got {n} bytes, sha256 "
                            f"{h.hexdigest()[:16]}..., expected {e.size} bytes, "
                            f"{e.sha256[:16]}...): changed upstream at {url}")
                os.replace(tmp, target)
                self.note("downloaded", e, n)
                return None
            except TooLarge as exc:
                return f"{exc}: changed upstream at {url}"
            except urllib.error.HTTPError as exc:
                last = f"HTTP {exc.code} from {url}"
                if exc.code == 404:
                    return last + " (removed or renamed upstream)"
                wait = 5.0 * 3 ** attempt
                if exc.code == 429:
                    try:
                        wait = max(wait, float(exc.headers.get("Retry-After", "60")))
                    except ValueError:
                        wait = max(wait, 60.0)
                    wait = min(wait, 900.0)
                elif exc.code < 500:
                    return last
                if attempt + 1 < RETRIES:
                    self.pause(host, wait)
                    print(f"  {last}; pausing {host} for {wait:.0f} s", file=sys.stderr)
            except (urllib.error.URLError, http.client.HTTPException, OSError) as exc:
                last = f"{type(exc).__name__}: {getattr(exc, 'reason', exc)} ({url})"
                if attempt + 1 < RETRIES:
                    time.sleep(5.0 * 3 ** attempt)
            finally:
                if os.path.exists(tmp):
                    os.remove(tmp)
        return f"gave up after {RETRIES} attempts: {last}"

    def fetch(self, e):
        try:
            self._fetch(e)
        except Exception as exc:  # report and go on with the other files
            self.fail(e, f"{type(exc).__name__}: {exc}")

    def _fetch(self, e):
        target = os.path.join(self.dest, *e.path.split("/"))
        ok = matches(target, e)
        if ok:
            self.note("present", e)
            return
        os.makedirs(os.path.dirname(target), exist_ok=True)
        if ok is False:
            print(f"  {e.path}: present but differs from the manifest; replacing it", file=sys.stderr)
        for key, base in [("instances/", INSTANCES)] + [("local", d) for d in self.locals]:
            src = os.path.join(base, *e.path.split("/"))
            got = matches(src, e)
            if got:
                tmp = target + ".part"
                shutil.copyfile(src, tmp)
                os.replace(tmp, target)
                self.note(key, e)
                return
            if got is False and key == "instances/":
                self.fail(e, f"{src} differs from the manifest (instances/ was modified?)")
                return
        reason = self.download(e, target)
        if reason:
            self.fail(e, reason)


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1000 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1000


def main():
    ap = argparse.ArgumentParser(description="Build data/ from instances/ and BOBILib's GitLab, "
                                 "verifying every file against the pinned manifest.")
    ap.add_argument("--subset", choices=("used", "unsolved", "all"), default="used",
                    help="used: instances with a certificate or solution file in results/ "
                    "(default); unsolved: BOBILib status feasible or open; all: every instance")
    ap.add_argument("--dest", default=os.path.join(ROOT, "data"), help="target folder (default: data/)")
    ap.add_argument("--verify-only", action="store_true", help="only check the files already in DEST")
    ap.add_argument("--jobs", type=int, default=MAX_JOBS, help=f"parallel downloads (1 to {MAX_JOBS})")
    ap.add_argument("--local", action="append", default=[], metavar="DIR",
                    help="an existing BOBILib download in the same layout to copy from first")
    ap.add_argument("--ref", default=None, metavar="COMMIT",
                    help="download from this commit of bobilib-data instead of master")
    ap.add_argument("--manifest", default=MANIFEST, help=argparse.SUPPRESS)
    args = ap.parse_args()
    jobs = max(1, min(MAX_JOBS, args.jobs))

    entries = select(read_manifest(args.manifest), args.subset)
    total = sum(e.size for e in entries)
    n_inst = len({instance_name(e.path) for e in entries} - {None})
    print(f"subset {args.subset}: {n_inst} instances, {len(entries)} files, {human(total)}; "
          f"destination {args.dest}", flush=True)

    if args.verify_only:
        bad = []
        for i, e in enumerate(entries, 1):
            ok = matches(os.path.join(args.dest, *e.path.split("/")), e)
            if not ok:
                bad.append((e.path, "missing" if ok is None else "differs from the manifest"))
            if i % 1000 == 0:
                print(f"  checked {i}/{len(entries)}")
        for p, why in bad[:50]:
            print(f"  {why}: {p}")
        if len(bad) > 50:
            print(f"  ... and {len(bad) - 50} more")
        print(f"verified {len(entries) - len(bad)} of {len(entries)} files "
              f"({'all match' if not bad else f'{len(bad)} missing or different'})")
        sys.exit(1 if bad else 0)

    for d in args.local:
        if not os.path.isdir(d):
            sys.exit(f"--local {d}: not a folder")
    f = Fetcher(args.dest, args.local, args.ref)
    t0 = time.monotonic()
    pool = ThreadPoolExecutor(max_workers=jobs)
    futures = [pool.submit(f.fetch, e) for e in entries]
    try:
        last = time.monotonic()
        while any(not x.done() for x in futures):
            time.sleep(1.0)
            now = time.monotonic()
            if now - last >= 30:
                last = now
                with f.lock:
                    print(f"  {f.done}/{len(entries)} files, {human(f.bytes_down)} downloaded, "
                          f"{len(f.failed)} failed, {now - t0:.0f} s", flush=True)
    except KeyboardInterrupt:
        pool.shutdown(wait=False, cancel_futures=True)
        print("interrupted: the files already in place are verified; rerun to fetch the rest",
              file=sys.stderr)
        sys.exit(130)
    pool.shutdown()

    c = f.count
    print(f"{len(entries) - len(f.failed)} of {len(entries)} files verified in {args.dest}: "
          f"{c['present']} already there, {c['instances/']} from instances/, {c['local']} from --local, "
          f"{c['downloaded']} downloaded ({human(f.bytes_down)}) in {time.monotonic() - t0:.0f} s",
          flush=True)
    if f.failed:
        print(f"{len(f.failed)} files NOT installed:", file=sys.stderr)
        for p, why in sorted(f.failed):
            print(f"  {p}: {why}", file=sys.stderr)
        if any(p == "collection.json" for p, _ in f.failed):
            print("collection.json is BOBILib's metadata, the table behind the Instances pages of "
                  "https://bobilib.org; only the scripts that read BOBILib's statuses need it. Save "
                  "a copy as DEST/collection.json (or pass it with --local DIR) and rerun.",
                  file=sys.stderr)
        if any("changed upstream" in why for _, why in f.failed):
            m = os.path.abspath(args.manifest)
            m = os.path.relpath(m, ROOT) if m.startswith(ROOT + os.sep) else m
            print(f"A checksum differs: BOBILib changed these files after the snapshot in {m}. "
                  "Try --ref with the commit named there.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
