"""Commit the pipeline's bookkeeping files and push them, even when another workflow or an authoring run pushed first.

  python3 publish/sync_commit.py "<commit message>" <path> [<path> ...]

A plain `git pull --rebase` stops on a conflict whenever two workflows touch publish/ledger.json or STATUS.md
in the same window, and the run's ledger entries are lost. Instead this script:
  * keeps the files this run changed (relative to the commit it started from),
  * moves onto the newest origin/main,
  * merges the ledger entry by entry (entries this run changed win, everything else comes from the remote),
  * regenerates STATUS.md from the merged state, commits and pushes; retries if someone pushed again meanwhile.
"""
import json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = "publish/ledger.json"
STATUS = "STATUS.md"


def git(*a, check=True, text=True):
    return subprocess.run(["git", *a], cwd=ROOT, check=check, capture_output=True, text=text)

def head_json(path):
    r = git("show", "HEAD:" + path, check=False)
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else {}

def changed(paths):
    out = git("status", "--porcelain", "--untracked-files=all", "--", *paths).stdout.splitlines()
    return [l[3:].strip().strip('"') for l in out if l.strip()]


def main():
    msg, paths = sys.argv[1], sys.argv[2:]
    base_ledger = head_json(LEDGER)
    files = [f for f in changed(paths) if f != STATUS]
    if not files:
        print("sync_commit: nothing changed"); return 0
    mine = {f: open(os.path.join(ROOT, f), "rb").read() for f in files if os.path.exists(os.path.join(ROOT, f))}
    my_ledger = json.loads(mine[LEDGER]) if LEDGER in mine else None
    print("sync_commit: this run changed", ", ".join(sorted(mine)))
    for attempt in range(6):
        git("fetch", "-q", "origin", "main")
        git("reset", "-q", "--hard", "origin/main")
        for f, data in mine.items():
            if f == LEDGER: continue
            os.makedirs(os.path.dirname(os.path.join(ROOT, f)) or ROOT, exist_ok=True)
            open(os.path.join(ROOT, f), "wb").write(data)
        if my_ledger is not None:
            merged = head_json(LEDGER)
            for k in set(my_ledger) | set(base_ledger):
                if my_ledger.get(k) != base_ledger.get(k):
                    if k in my_ledger: merged[k] = my_ledger[k]
                    else: merged.pop(k, None)
            with open(os.path.join(ROOT, LEDGER), "w") as fh:
                json.dump(merged, fh, indent=2, sort_keys=True)
        subprocess.run([sys.executable, "publish/publisher.py", "status"], cwd=ROOT, check=False)
        git("add", "--", *paths)
        if git("diff", "--cached", "--quiet", check=False).returncode == 0:
            print("sync_commit: already up to date"); return 0
        git("commit", "-q", "-m", msg)
        r = git("push", "-q", "origin", "HEAD:main", check=False)
        if r.returncode == 0:
            print(f"sync_commit: pushed (attempt {attempt + 1})"); return 0
        print("sync_commit: push refused, retrying:", r.stderr.strip()[:200])
        time.sleep(3 + attempt * 4)
    print("sync_commit: gave up after 6 attempts"); return 1


if __name__ == "__main__":
    sys.exit(main())
