#!/usr/bin/env python3
"""Refresh podcast.json from the Ride or Die Laughing YouTube playlist.

Run daily by .github/workflows/update-podcast.yml. Uses yt-dlp to read the
playlist (no downloads), writes id + display label per episode, newest first.
If extraction yields nothing (e.g. YouTube blocks the runner), it leaves the
existing podcast.json untouched so the site never goes blank.
"""
import datetime
import json
import pathlib
import re
import subprocess
import sys

PLAYLIST = "https://www.youtube.com/playlist?list=PLLt0n3szG-OYno9YcF4ouiB5I7Y3s7cGz"
OUT = pathlib.Path(__file__).resolve().parent.parent / "podcast.json"

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def fetch_entries():
    try:
        res = subprocess.run(
            ["yt-dlp", "--flat-playlist", "-J", PLAYLIST],
            capture_output=True, text=True, timeout=180,
        )
    except Exception as exc:  # noqa: BLE001
        print("yt-dlp error:", exc, file=sys.stderr)
        return []
    if res.returncode != 0:
        print("yt-dlp failed:", res.stderr[:500], file=sys.stderr)
        return []
    try:
        data = json.loads(res.stdout)
    except json.JSONDecodeError as exc:
        print("bad JSON from yt-dlp:", exc, file=sys.stderr)
        return []
    entries = []
    for e in data.get("entries") or []:
        vid = e.get("id")
        title = (e.get("title") or "").strip()
        if vid:
            entries.append({"id": vid, "title": title})
    return entries


def parse_date(title):
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", title)
    if not m:
        return None
    mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if y < 100:
        y += 2000
    try:
        return datetime.date(y, mo, d)
    except ValueError:
        return None


def make_label(title):
    dt = parse_date(title)
    date_str = "%s %d, %d" % (MONTHS[dt.month - 1], dt.day, dt.year) if dt else None
    ep = re.search(r"[Ee]pisode\s*(\d+)", title)
    ep_str = "Episode %s" % ep.group(1) if ep else None
    if ep_str and date_str:
        return "%s — %s" % (ep_str, date_str)
    return date_str or ep_str or (title or "Episode")


def main():
    eps = fetch_entries()
    if not eps:
        print("No episodes parsed; keeping existing podcast.json", file=sys.stderr)
        return 0
    for e in eps:
        e["label"] = make_label(e["title"])
    eps.sort(key=lambda e: parse_date(e["title"]) or datetime.date(1900, 1, 1),
             reverse=True)  # newest first
    payload = {
        "playlist": PLAYLIST,
        "updated": datetime.date.today().isoformat(),
        "episodes": eps,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("Wrote %d episode(s) to %s" % (len(eps), OUT.name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
