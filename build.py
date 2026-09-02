"""build.py - bikin PVZ.exe pakai PyInstaller.

Cara pakai:
    python build.py                 # bikin dist/PVZ.exe (tanpa jendela hitam)
    python build.py --console       # sama, tapi console kelihatan (buat lihat error)
    python build.py --folder        # hasilnya 1 folder, bukan 1 file (boot lebih cepat)

Semua file .png di folder ini otomatis ikut dibundel, jadi kalau nambah sprite
baru ga perlu ngedit file ini.
"""

import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "PVZ"
ENTRY = "main.py"

STUB = '''import builtins, os, sys

# PyInstaller ga nyertain modul `site`, padahal dari situ builtin exit() dan
# quit() datang. Tanpa ini, begitu user klik tombol X di jendela, main.py
# manggil exit() dan exe-nya mati dengan NameError. Kita balikin manual.
builtins.exit = sys.exit
builtins.quit = sys.exit

# main.py manggil image.load("Background.png") -> path relatif.
# Di exe --onefile, asset diekstrak ke folder temp (sys._MEIPASS), sementara
# cwd-nya tetap di tempat user klik exe-nya. Jadi pindah cwd dulu.
if hasattr(sys, "_MEIPASS"):
    os.chdir(sys._MEIPASS)

import main
'''


def main():
    args = sys.argv[1:]
    onefile = "--folder" not in args
    console = "--console" in args

    os.chdir(HERE)

    if not os.path.exists(ENTRY):
        sys.exit("ERROR: %s ga ketemu di %s" % (ENTRY, HERE))

    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        sys.exit("PyInstaller belum keinstal. Jalanin dulu:\n"
                 "    %s -m pip install pyinstaller" % sys.executable)

    assets = sorted(f for f in os.listdir(HERE) if f.lower().endswith(".png"))
    if not assets:
        sys.exit("ERROR: ga ada file .png di folder ini, gambarnya mana?")

    # spec/stub/cache ditaruh di temp biar folder project cuma nambah dist/
    work = tempfile.mkdtemp(prefix="pvz-build-")
    stub_path = os.path.join(work, "_entry.py")
    with open(stub_path, "w", encoding="utf-8") as fh:
        fh.write(STUB)

    cmd = [sys.executable, "-m", "PyInstaller", stub_path,
           "--name", NAME,
           "--noconfirm", "--clean",
           "--onefile" if onefile else "--onedir",
           "--console" if console else "--windowed",
           "--paths", HERE,              # biar `import main` ketemu
           "--distpath", os.path.join(HERE, "dist"),
           "--workpath", os.path.join(work, "work"),
           "--specpath", work]

    for a in assets:
        # sumbernya harus path absolut: PyInstaller nyari path relatif dari
        # lokasi file .spec (yang kita taruh di temp), bukan dari folder ini
        cmd += ["--add-data", os.path.join(HERE, a) + os.pathsep + "."]
    if os.path.exists("icon.ico"):
        cmd += ["--icon", os.path.join(HERE, "icon.ico")]

    print("Bundel %d gambar: %s" % (len(assets), ", ".join(assets)))
    print("Build... (pertama kali biasanya 30-60 detik)\n")
    code = subprocess.call(cmd)
    shutil.rmtree(work, ignore_errors=True)

    if code != 0:
        sys.exit("\nBuild GAGAL (exit %d). Baca error PyInstaller di atas." % code)

    out = os.path.join(HERE, "dist", NAME + (".exe" if onefile else ""))
    if onefile and not os.path.exists(out):
        sys.exit("\nBuild bilang sukses tapi %s ga ada." % out)

    if onefile:
        print("\nBERES -> %s  (%.1f MB)" % (out, os.path.getsize(out) / 1048576))
    else:
        print("\nBERES -> %s\\  (kirim SEISI foldernya, jangan cuma exe-nya)"
              % os.path.join(HERE, "dist", NAME))


if __name__ == "__main__":
    main()
