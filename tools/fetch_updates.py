#!/usr/bin/env python3
import argparse
import importlib.util
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://plugins.jetbrains.com"
CDN = "https://downloads.marketplace.jetbrains.com/files/"
JETBRAINS_DIR = Path("/mnt/c/Program Files/JetBrains")
GITHUB_FILE_LIMIT = 95 * 1024 * 1024
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

TOOLS = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gen_update_plugins", TOOLS / "gen_update_plugins.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)


def request(url, data=None):
    body = json.dumps(data).encode() if data is not None else None
    headers = dict(HEADERS, **({"Content-Type": "application/json"} if body else {}))
    with urllib.request.urlopen(urllib.request.Request(url, data=body, headers=headers), timeout=120) as resp:
        return resp.read()


def get_json(url, data=None):
    return json.loads(request(url, data))


def installed_builds():
    builds = []
    for info in sorted(JETBRAINS_DIR.glob("*/product-info.json")):
        meta = json.loads(info.read_text(encoding="utf-8"))
        builds.append(f"{meta['productCode']}-{meta['buildNumber']}")
    return builds


def compatible_updates(build, xml_ids):
    found = get_json(f"{API}/api/search/compatibleUpdates", {"build": build, "pluginXMLIds": xml_ids})
    return {u["id"]: (u["pluginXmlId"], u["version"], build) for u in found}


def latest_update(xml_id):
    plugin = get_json(f"{API}/api/plugins/intellij/{urllib.parse.quote(xml_id)}")
    updates = get_json(f"{API}/api/plugins/{plugin['id']}/updates?size=1")
    if not updates:
        return {}
    return {updates[0]["id"]: (xml_id, updates[0]["version"], "latest")}


def cdn_url(file_path):
    return CDN + "/".join(urllib.parse.quote(part) for part in file_path.split("/"))


def target_path(root, file_path, update_id):
    name = Path(file_path).name
    path = root / name
    if path.exists():
        path = root / f"{Path(name).stem}-{update_id}{Path(name).suffix}"
    return path


def download(root, update_id, xml_id):
    meta = get_json(f"{API}/api/updates/{update_id}")
    if meta.get("size", 0) > GITHUB_FILE_LIMIT:
        return None, f"too large for GitHub: {meta['size']} bytes"
    path = target_path(root, meta["file"], update_id)
    tmp = path.with_name(path.name + ".part")
    tmp.write_bytes(request(cdn_url(meta["file"])))
    if tmp.stat().st_size > GITHUB_FILE_LIMIT:
        tmp.unlink()
        return None, "too large for GitHub"
    raw = gen.read_plugin_xml(tmp)
    if raw is None:
        tmp.unlink()
        return None, "archive has no plugin.xml"
    tmp.rename(path)
    return path, None


def main():
    parser = argparse.ArgumentParser(description="Download new plugin versions from JetBrains Marketplace CDN")
    parser.add_argument("--dir", type=Path, default=TOOLS.parent)
    parser.add_argument("--build", action="append", help="IDE build with product code, e.g. PS-263.7307.215")
    parser.add_argument("--no-latest", action="store_true", help="skip the newest version regardless of IDE build")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    builds = args.build or installed_builds()
    if not builds:
        sys.exit("no IDE builds: pass --build PS-263.7307.215")

    local = gen.collect(args.dir)
    have = {(p["id"], p["version"]) for p in local}
    xml_ids = sorted({p["id"] for p in local})
    print("builds:", ", ".join(builds))

    candidates = {}
    for build in builds:
        candidates.update(compatible_updates(build, xml_ids))
    if not args.no_latest:
        for xml_id in xml_ids:
            try:
                for update_id, found in latest_update(xml_id).items():
                    candidates.setdefault(update_id, found)
            except urllib.error.HTTPError as e:
                print(f"{'skip':<10}{xml_id:<45}not on Marketplace ({e.code})")

    for update_id, (xml_id, version, source) in sorted(candidates.items(), key=lambda c: (c[1][0], c[1][1])):
        if (xml_id, version) in have:
            print(f"{'have':<10}{xml_id:<45}{version:<24}{source}")
            continue
        if args.dry_run:
            print(f"{'new':<10}{xml_id:<45}{version:<24}{source}")
            continue
        path, error = download(args.dir, update_id, xml_id)
        if error:
            print(f"{'FAIL':<10}{xml_id:<45}{version:<24}{error}")
            continue
        have.add((xml_id, version))
        print(f"{'added':<10}{xml_id:<45}{version:<24}{path.name}")


if __name__ == "__main__":
    main()
