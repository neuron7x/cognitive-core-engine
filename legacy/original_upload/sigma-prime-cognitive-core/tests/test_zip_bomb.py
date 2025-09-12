import zipfile, io, json, sys, subprocess, os
from .util_zip import run_sanitize

def make_zip_with_big_ratio(tmp_path):
    zpath = tmp_path / "ratio.zip"
    data = b"A" * (2 * 1024 * 1024)  # 2MB of same byte => high ratio
    with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("big.txt", data)
    return zpath

def test_zip_bomb_ratio_flag(tmp_path):
    zpath = make_zip_with_big_ratio(tmp_path)
    code, out = run_sanitize(str(zpath))
    # Our sanitize CLI prints "ZIP safe" only when ok
    # Here we rely on library thresholds from zipci_lib; call it via CLI entry
    proc = subprocess.run([sys.executable, "-m", "tools.zipci.cli", str(zpath)],
                          capture_output=True, text=True)
    js = json.loads(proc.stdout.strip())
    assert js["ok"] in (True, False)
    # High ratio should normally flag as suspicious
    assert any("suspicious-ratio" in r for r in js["reasons"])
