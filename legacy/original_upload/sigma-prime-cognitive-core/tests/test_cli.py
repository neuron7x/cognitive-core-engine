import json, sys, subprocess, pathlib

def test_cli_json_output(tmp_path):
    p = tmp_path / "ok.zip"
    (tmp_path / "d").mkdir()
    (tmp_path / "d/file.txt").write_text("hello")
    import zipfile
    with zipfile.ZipFile(p, "w") as z:
        z.write(tmp_path / "d/file.txt", "file.txt")
    proc = subprocess.run([sys.executable, "-m", "tools.zipci.cli", str(p)],
                          capture_output=True, text=True)
    assert proc.returncode == 0
    js = json.loads(proc.stdout.strip())
    assert js["ok"] is True
    assert js["zip"].endswith(".zip")
