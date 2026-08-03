#!/usr/bin/env python3
# Script to organize docs folder for mkdocs build
# Ensures Chinese translation files are in i18n/simple-chinese/,
# fixes common formatting issues in translated markdown files,
# and generates a complete sitemap.xml.

import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

SITE_URL = "https://docs.kalico.gg"
I18N_DIR = "i18n/simple-chinese"
NAV_FILES = {
    "index.md", "Overview.md", "Features.md", "FAQ.md", "Config_Changes.md",
    "Config_Reference.md", "Kalico_Additions.md", "Bleeding_Edge.md",
    "Config_Reference_Bleeding_Edge.md", "Nonlinear_Pressure_Advance.md",
    "PID.md", "MPC.md", "Dockable_Probe.md", "INDX.md",
    "G-Codes.md", "Command_Templates.md", "G-Code_Shell_Command.md", "Status_Reference.md",
    "Migrating_from_Klipper.md", "Installation.md", "OctoPrint.md", "TMC_Drivers.md",
    "Config_checks.md", "Rotation_Distance.md", "Multi_MCU_Homing.md",
    "Z_Calibration.md", "Bed_Level.md", "Delta_Calibrate.md", "Probe_Calibrate.md",
    "BLTouch.md", "Manual_Level.md", "Bed_Mesh.md", "Endstop_Phase.md",
    "Axis_Twist_Compensation.md", "Skew_Correction.md",
    "Measuring_Resonances.md", "Resonance_Compensation.md", "Pressure_Advance.md",
    "Slicers.md", "Exclude_Object.md", "Using_PWM_Tools.md",
    "Code_Overview.md", "Kinematics.md", "Protocol.md", "API_Server.md",
    "MCU_Commands.md", "CANBUS_protocol.md", "Debugging.md", "Benchmarks.md",
    "CONTRIBUTING.md", "Packaging.md",
    "Example_Configs.md", "SDCard_Updates.md", "RPi_microcontroller.md",
    "Beaglebone.md", "Bootloaders.md", "Bootloader_Entry.md",
    "CANBUS.md", "CANBUS_Troubleshooting.md",
    "TSL1401CL_Filament_Width_Sensor.md", "Hall_Filament_Width_Sensor.md", "Load_Cell.md",
    "Telemetry.md", "Contact.md", "Sponsors.md",
}


def find_docs_root():
    script_dir = Path(__file__).resolve().parent
    docs_root = script_dir.parent / "docs"
    if not docs_root.is_dir():
        print(f"Error: docs directory not found at {docs_root}", file=sys.stderr)
        sys.exit(1)
    return docs_root


def move_cn_files(docs_root):
    i18n_dir = docs_root / "i18n" / "simple-chinese"
    i18n_dir.mkdir(parents=True, exist_ok=True)

    moved = []
    for md_file in docs_root.glob("*_CN.md"):
        dest = i18n_dir / md_file.name
        if dest.exists():
            if md_file.read_text(encoding="utf-8") == dest.read_text(encoding="utf-8"):
                md_file.unlink()
                moved.append(f"removed duplicate: {md_file.name}")
            else:
                print(
                    f"Warning: {md_file.name} differs from {dest}, skipping",
                    file=sys.stderr,
                )
        else:
            shutil.move(str(md_file), str(dest))
            moved.append(f"moved: {md_file.name}")

    return moved


def fix_code_fences(md_path):
    content = md_path.read_text(encoding="utf-8")
    original = content
    content = re.sub(r"^\\\s*$", "```", content, flags=re.MULTILINE)
    if content != original:
        md_path.write_text(content, encoding="utf-8")
        return True
    return False


def fix_escaped_brackets(md_path):
    content = md_path.read_text(encoding="utf-8")
    original = content
    content = re.sub(r"\\\[(\w+)\\\]", r"`[\1]`", content)
    if content != original:
        md_path.write_text(content, encoding="utf-8")
        return True
    return False


def process_translations(docs_root):
    i18n_dir = docs_root / "i18n" / "simple-chinese"
    if not i18n_dir.exists():
        return []

    results = []
    for md_file in i18n_dir.glob("*.md"):
        changed = False
        if fix_code_fences(md_file):
            results.append(f"fixed fences: {md_file.name}")
            changed = True
        if fix_escaped_brackets(md_file):
            results.append(f"fixed brackets: {md_file.name}")
            changed = True
        if not changed:
            pass
    return results


def generate_sitemap(docs_root):
    today = datetime.now().strftime("%Y-%m-%d")
    urls = []

    # Root-level English docs
    for md_file in sorted(docs_root.glob("*.md")):
        if md_file.name.startswith("_") or md_file.name.startswith("~"):
            continue
        priority = "1.0" if md_file.name == "index.md" else \
                   "0.9" if md_file.name in NAV_FILES else "0.5"
        freq = "weekly" if md_file.name in {
            "index.md", "Config_Reference.md", "G-Codes.md",
            "Config_Reference_Bleeding_Edge.md", "Config_Changes.md",
        } else "monthly"
        urls.append(f"""  <url>
    <loc>{SITE_URL}/{md_file.name}</loc>
    <lastmod>{today}</lastmod>
    <priority>{priority}</priority>
    <changefreq>{freq}</changefreq>
  </url>""")

    # Subdirectory docs (ai/, fly_features/)
    for subdir in ["ai", "fly_features"]:
        sub_path = docs_root / subdir
        if not sub_path.exists():
            continue
        for md_file in sorted(sub_path.glob("*.md")):
            urls.append(f"""  <url>
    <loc>{SITE_URL}/{subdir}/{md_file.name}</loc>
    <lastmod>{today}</lastmod>
    <priority>0.5</priority>
    <changefreq>monthly</changefreq>
  </url>""")

    # Chinese translations
    i18n_dir = docs_root / I18N_DIR
    if i18n_dir.exists():
        for md_file in sorted(i18n_dir.glob("*.md")):
            urls.append(f"""  <url>
    <loc>{SITE_URL}/{I18N_DIR}/{md_file.name}</loc>
    <lastmod>{today}</lastmod>
    <priority>0.7</priority>
    <changefreq>monthly</changefreq>
  </url>""")

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>
"""
    sitemap_path = docs_root / "sitemap.xml"
    sitemap_path.write_text(sitemap, encoding="utf-8")
    return len(urls)


def main():
    docs_root = find_docs_root()
    print(f"Docs root: {docs_root}")

    results = []
    results.extend(move_cn_files(docs_root))
    results.extend(process_translations(docs_root))

    if results:
        print("Changes made:")
        for r in results:
            print(f"  - {r}")
    else:
        print("No changes needed.")

    count = generate_sitemap(docs_root)
    print(f"Sitemap generated: {count} URLs")
    print("Done.")


if __name__ == "__main__":
    main()
