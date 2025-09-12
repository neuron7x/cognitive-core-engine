import zipfile

from .util_zip import run_sanitize


def test_sanitize_all_good(tmp_path):
    zpath = tmp_path / "good.zip"
    with zipfile.ZipFile(zpath, "w") as z:
        z.writestr("proj/readme.txt", "ok")
    code, out = run_sanitize(str(zpath))
    assert code == 0
    assert "ZIP safe" in out


def test_sanitize_path_traversal(tmp_path):
    zpath = tmp_path / "bad.zip"
    with zipfile.ZipFile(zpath, "w") as z:
        z.writestr("../evil.txt", "x")
        z.writestr("/abs/file.txt", "y")
        z.writestr(".git/config", "secret")
    code, out = run_sanitize(str(zpath))
    assert code != 0
    assert "Forbidden entries:" in out


def test_sanitize_symlink_detection(tmp_path):
    zpath = tmp_path / "sym.zip"
    with zipfile.ZipFile(zpath, "w") as z:
        info = zipfile.ZipInfo("link")
        info.create_system = 3
        # Set mode to symlink
        info.external_attr = 0o120777 << 16
        z.writestr(info, "")
    code, out = run_sanitize(str(zpath))
    assert code != 0
    assert "symlink" in out
