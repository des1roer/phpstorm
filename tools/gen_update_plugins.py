#!/usr/bin/env python3
import argparse
import io
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

PLUGIN_XML = "META-INF/plugin.xml"


def read_plugin_xml(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if PLUGIN_XML in names:
            return archive.read(PLUGIN_XML)
        for name in names:
            parts = name.split("/")
            if len(parts) == 3 and parts[1] == "lib" and name.endswith(".jar"):
                with zipfile.ZipFile(io.BytesIO(archive.read(name))) as jar:
                    if PLUGIN_XML in jar.namelist():
                        return jar.read(PLUGIN_XML)
    return None


def build_tuple(build):
    return tuple(int(p) if p.isdigit() else sys.maxsize for p in re.split(r"[.]", build))


def is_compatible(build, since, until):
    target = build_tuple(build)
    if since and target < build_tuple(since)[: len(target)]:
        return False
    if until:
        limit = build_tuple(until.replace("*", str(sys.maxsize)))
        if target[: len(limit)] > limit:
            return False
    return True


def collect(folder):
    plugins = []
    for path in sorted(p for p in folder.iterdir() if p.suffix in (".zip", ".jar")):
        raw = read_plugin_xml(path)
        if raw is None:
            print(f"skip {path.name}: {PLUGIN_XML} not found", file=sys.stderr)
            continue
        meta = ET.fromstring(raw)
        idea_version = meta.find("idea-version")
        attrs = idea_version.attrib if idea_version is not None else {}
        plugins.append({
            "file": path.name,
            "id": (meta.findtext("id") or meta.findtext("name") or path.stem).strip(),
            "name": (meta.findtext("name") or path.stem).strip(),
            "version": (meta.findtext("version") or "0").strip(),
            "description": meta.findtext("description") or "",
            "since": attrs.get("since-build"),
            "until": attrs.get("until-build"),
        })
    return plugins


def write_xml(plugins, base_url, target):
    root = ET.Element("plugins")
    for p in plugins:
        node = ET.SubElement(root, "plugin", id=p["id"], url=f"{base_url}/{p['file']}", version=p["version"])
        bounds = {k: v for k, v in (("since-build", p["since"]), ("until-build", p["until"])) if v}
        ET.SubElement(node, "idea-version", bounds)
        ET.SubElement(node, "name").text = p["name"]
        ET.SubElement(node, "description").text = p["description"]
    ET.indent(root)
    ET.ElementTree(root).write(target, encoding="utf-8", xml_declaration=True)


def main():
    parser = argparse.ArgumentParser(description="Generate updatePlugins.xml for a custom JetBrains plugin repository")
    parser.add_argument("--dir", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--base-url", default="https://raw.githubusercontent.com/des1roer/phpstorm/main")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--build", help="IDE build to check compatibility against, e.g. 263.7307.215")
    args = parser.parse_args()

    plugins = collect(args.dir)
    out = args.out or args.dir / "updatePlugins.xml"
    write_xml(plugins, args.base_url.rstrip("/"), out)

    for p in plugins:
        status = ""
        if args.build:
            status = "ok" if is_compatible(args.build, p["since"], p["until"]) else "INCOMPATIBLE"
        print(f"{status:<13}{p['id']:<45}{p['version']:<20}{p['since'] or '-'} .. {p['until'] or '-'}")
    print(f"{len(plugins)} plugins -> {out}")


if __name__ == "__main__":
    main()
