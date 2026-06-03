#!/usr/bin/env python3
"""
gen_compile_time_request.py - PlatformIO build script (two-phase build)

Phase 1 (pre-build): Compile all sources WITHOUT LTO to extract
  .compile_time_request sections, then run buildcommands.py to generate
  compile_time_request.c.

Phase 2 (normal build): PlatformIO compiles everything WITH LTO,
  using the auto-generated compile_time_request.c.
"""
Import("env", "projenv")
import subprocess
import os
import sys
import re
import glob

PROJECT_DIR = env.subst("$PROJECT_DIR")
BUILD_DIR = env.subst("$BUILD_DIR")

KLIPPER_DIR = os.path.normpath(os.path.join(PROJECT_DIR, "..", ".."))
BUILDCMD_SCRIPT = os.path.join(KLIPPER_DIR, "scripts", "buildcommands.py")
OUT_DIR = os.path.join(BUILD_DIR, "klipper_gen")
CTR_TXT = os.path.join(OUT_DIR, "compile_time_request.txt")
CTR_C = os.path.join(OUT_DIR, "compile_time_request.c")
KLIPPER_DICT = os.path.join(OUT_DIR, "klipper.dict")
CTR_OBJ_DIR = os.path.join(OUT_DIR, "ctr_objects")

PYTHON = sys.executable

# Source directories to scan for .c files
SRC_DIRS = [
    os.path.join(PROJECT_DIR, "src"),
]


def find_c_files():
    """Find all .c source files that might contain DECL_CTR macros."""
    c_files = []
    for src_dir in SRC_DIRS:
        for root, dirs, files in os.walk(src_dir):
            for f in files:
                if f.endswith(".c") and f != "compile_time_request.c":
                    c_files.append(os.path.join(root, f))
    return c_files


def compile_for_ctr(c_files):
    """Compile .c files to .o WITHOUT LTO for CTR extraction."""
    os.makedirs(CTR_OBJ_DIR, exist_ok=True)

    cc = "avr-gcc"
    include_dirs = []
    for d in [os.path.join(PROJECT_DIR, "src"),
              os.path.join(PROJECT_DIR, "src", "board"),
              os.path.join(PROJECT_DIR, "src", "arduino"),
              os.path.join(PROJECT_DIR, "src", "generic")]:
        if os.path.isdir(d):
            include_dirs.extend(["-I", d])

    cppdefines = []
    for d in env.get("CPPDEFINES", []):
        if isinstance(d, tuple):
            cppdefines.append(f"-D{d[0]}={d[1]}")
        else:
            cppdefines.append(f"-D{d}")

    base_flags = ["-mmcu=atmega328p", "-Os", "-std=gnu11",
                  "-Wall", "-fno-lto"] + cppdefines + include_dirs

    compiled = []
    for c_file in c_files:
        basename = os.path.basename(c_file).replace(".c", ".o")
        o_path = os.path.join(CTR_OBJ_DIR, basename)

        # Only recompile if source is newer
        if os.path.exists(o_path) and \
           os.path.getmtime(o_path) > os.path.getmtime(c_file):
            compiled.append(o_path)
            continue

        result = subprocess.run(
            [cc] + base_flags + ["-c", c_file, "-o", o_path],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            # Some files may fail due to missing headers — that's OK
            # as long as we get the CTR data
            pass
        if os.path.exists(o_path):
            compiled.append(o_path)

    return compiled


def extract_ctr(obj_files):
    """Extract .compile_time_request sections from .o files."""
    ctr_data = bytearray()

    for o_path in obj_files:
        tmp_ctr = o_path + ".ctr"
        result = subprocess.run(
            ["avr-objcopy", "-j", ".compile_time_request",
             "-O", "binary", o_path, tmp_ctr],
            capture_output=True
        )
        if result.returncode == 0 and os.path.exists(tmp_ctr):
            with open(tmp_ctr, "rb") as f:
                data = f.read()
            if data:
                ctr_data.extend(data)
            os.remove(tmp_ctr)
        elif os.path.exists(tmp_ctr):
            os.remove(tmp_ctr)

    return ctr_data


def ctr_to_text(ctr_data):
    """Convert binary CTR data to text format for buildcommands.py."""
    raw_text = ctr_data.decode("latin-1")
    fragments = raw_text.split("\x00")

    lines = []
    for frag in fragments:
        frag_stripped = frag.strip()
        if not frag_stripped:
            continue
        # Join CTR_INT value fragments with previous line
        if re.match(r'^[+-]0x[0-9a-fA-F]+', frag_stripped) and lines:
            lines[-1] = lines[-1] + " " + frag_stripped
        else:
            lines.append(frag_stripped)

    return "\n".join(lines) + "\n"


def run_buildcommands(ctr_text):
    """Run buildcommands.py to generate compile_time_request.c."""
    tools = ";".join([env.subst("$CC"), env.subst("$AS"), env.subst("$LD"),
                      env.subst("$OBJCOPY"), env.subst("$OBJDUMP")])

    # Write CTR text to file (buildcommands.py reads from file, not stdin)
    ctr_txt_path = os.path.join(OUT_DIR, "compile_time_request.txt")
    with open(ctr_txt_path, "w") as f:
        f.write(ctr_text)

    result = subprocess.run(
        [PYTHON, BUILDCMD_SCRIPT,
         "-d", KLIPPER_DICT,
         "-t", tools,
         "-e", "generic_arduino",
         ctr_txt_path, CTR_C],
        input=ctr_text,
        capture_output=True, text=True,
        cwd=KLIPPER_DIR
    )
    return result


def pre_build_action():
    """Run the full pre-build CTR extraction pipeline."""
    # Check if we need to regenerate
    c_files = find_c_files()
    if not c_files:
        print("No source files found!")
        return

    # Check if any source file is newer than the generated C file
    need_regen = not os.path.exists(CTR_C)
    if not need_regen:
        ctr_mtime = os.path.getmtime(CTR_C)
        for cf in c_files:
            if os.path.getmtime(cf) > ctr_mtime:
                need_regen = True
                break

    if not need_regen:
        print(f"CTR file up to date: {CTR_C}")
        return

    os.makedirs(OUT_DIR, exist_ok=True)

    # Phase 1: Compile for CTR extraction
    print("Phase 1: Compiling for CTR extraction...")
    obj_files = compile_for_ctr(c_files)
    print(f"  Compiled {len(obj_files)} objects")

    # Extract CTR data
    ctr_data = extract_ctr(obj_files)
    if not ctr_data:
        print("WARNING: No CTR data extracted!")
        return

    # Convert to text
    ctr_text = ctr_to_text(ctr_data)
    with open(os.path.join(OUT_DIR, "compile_time_request_raw.txt"), "w") as f:
        f.write(ctr_text)

    lines = [l for l in ctr_text.split("\n") if l.strip()]
    print(f"  Extracted {len(ctr_data)} bytes, {len(lines)} entries")

    # Run buildcommands.py
    print("Running buildcommands.py...")
    result = run_buildcommands(ctr_text)
    if result.returncode != 0:
        print(f"buildcommands.py FAILED:\n{result.stderr}")
        return

    print(f"Generated {CTR_C}")
    if result.stdout.strip():
        for line in result.stdout.strip().split("\n"):
            print(f"  {line}")
    if result.stderr.strip():
        for line in result.stderr.strip().split("\n"):
            print(f"  {line}")

    # Post-process: remove __always_inline (causes issues with LTO on AVR)
    # and remove ctr_run_* functions (provided by ctr_run.c + registrations.c)
    with open(CTR_C, "r") as f:
        code = f.read()
    code = code.replace("const __always_inline struct command_encoder *",
                        "const struct command_encoder *")
    code = code.replace("uint8_t __always_inline",
                        "uint8_t")
    # Remove ctr_run_initfuncs, ctr_run_taskfuncs, ctr_run_shutdownfuncs
    # These are provided by ctr_run.c using registrations.c lists
    import re
    code = re.sub(r'\nvoid\nctr_run_initfuncs\(void\)\n\{[^}]*\}\n', '\n', code)
    code = re.sub(r'\nvoid\nctr_run_taskfuncs\(void\)\n\{[^}]*\}\n', '\n', code)
    code = re.sub(r'\nvoid\nctr_run_shutdownfuncs\(void\)\n\{[^}]*\}\n', '\n', code)
    # Remove initial_pins (provided by initial_pins.h stub)
    code = re.sub(r'\nconst struct initial_pin_s initial_pins\[\].*?;\n', '\n', code)
    code = re.sub(r'\nconst int initial_pins_size.*?;\n', '\n', code)
    with open(CTR_C, "w") as f:
        f.write(code)
    print("  Post-processed: removed __always_inline + ctr_run_* + initial_pins")


def compile_generated_ctr():
    """Compile the generated compile_time_request.c with LTO flags."""
    cc = env.subst("$CC")
    include_dirs = []
    for d in [os.path.join(PROJECT_DIR, "src"),
              os.path.join(PROJECT_DIR, "src", "board"),
              os.path.join(PROJECT_DIR, "src", "arduino"),
              os.path.join(PROJECT_DIR, "src", "generic")]:
        if os.path.isdir(d):
            include_dirs.extend(["-I", d])

    cppdefines = []
    for d in env.get("CPPDEFINES", []):
        if isinstance(d, tuple):
            cppdefines.append(f"-D{d[0]}={d[1]}")
        else:
            cppdefines.append(f"-D{d}")

    # Compile with same flags as PlatformIO (including LTO)
    o_path = os.path.join(OUT_DIR, "compile_time_request.o")
    compile_cmd = [cc, "-mmcu=atmega328p", "-Os", "-flto",
                   "-fno-merge-constants", "-std=gnu11",
                   "-fno-use-linker-plugin"] + cppdefines + include_dirs + \
                  ["-c", CTR_C, "-o", o_path]

    result = subprocess.run(compile_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"CTR compilation FAILED:\n{result.stderr}")
        return False

    # Replace the PlatformIO-compiled .o with our generated one
    orig_o = os.path.join(BUILD_DIR, "src", "compile_time_request.c.o")
    if os.path.exists(orig_o):
        os.remove(orig_o)
    import shutil
    shutil.copy2(o_path, orig_o)
    print(f"Replaced {orig_o}")
    return True


def pre_link_action(source, target, env):
    """Pre-link action: compile and replace compile_time_request.o."""
    if os.path.exists(CTR_C):
        compile_generated_ctr()


# Run pre-build action immediately (before any PlatformIO compilation)
pre_build_action()

# Register pre-link action to replace the .o after PlatformIO compiles
env.AddPreAction("$BUILD_DIR/firmware.elf", pre_link_action)
