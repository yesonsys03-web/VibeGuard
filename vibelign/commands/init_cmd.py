import platform
import shutil
import subprocess
import sys
from pathlib import Path

_MIN_PYTHON = (3, 9)

_ERR = {
    "network": (
        "인터넷 연결이 필요해요.\n    와이파이가 연결됐는지 확인하고 다시 해보세요."
    ),
    "permission": (
        "이 컴퓨터에 설치할 권한이 없어요.\n"
        "    Mac/Linux: sudo vib init\n"
        "    Windows:   관리자 권한으로 터미널을 열고 다시 시도해보세요."
    ),
    "pip_broken": (
        "Python이 제대로 설치되지 않은 것 같아요.\n"
        "    python.org 에서 Python을 다시 설치해보세요."
    ),
    "uv_fail": (
        "uv 설치에 실패했어요.\n"
        "    직접 설치하려면: https://docs.astral.sh/uv/getting-started/installation/"
    ),
    "reinstall_fail": (
        "vibelign 재설치에 실패했어요.\n"
        "    직접 설치하려면:\n"
        "      uv:  uv tool install vibelign --no-cache\n"
        "      pip: pip install vibelign --upgrade --no-cache-dir"
    ),
}

_UV_INSTALL_CMD = {
    "Darwin": "curl -LsSf https://astral.sh/uv/install.sh | sh",
    "Linux": "curl -LsSf https://astral.sh/uv/install.sh | sh",
    "Windows": (
        "powershell -ExecutionPolicy ByPass -c "
        '"irm https://astral.sh/uv/install.ps1 | iex"'
    ),
}


def _ok(msg: str) -> None:
    print(f"  ✓ {msg}")


def _step(msg: str) -> None:
    print(f"  → {msg}")


def _warn(msg: str) -> None:
    print(f"  ⚠  {msg}")


def _fail(msg: str) -> None:
    print(f"  ✗ {msg}")


def _korean_error(result: subprocess.CompletedProcess[str]) -> str:
    combined = ((result.stdout or "") + (result.stderr or "")).lower()
    if any(
        k in combined
        for k in ["network", "connection", "timeout", "urlopen", "unreachable"]
    ):
        return _ERR["network"]
    if any(k in combined for k in ["permission", "access denied", "denied"]):
        return _ERR["permission"]
    return ""


def _check_python() -> bool:
    cur = sys.version_info[:2]
    if cur < _MIN_PYTHON:
        _fail(
            f"Python {cur[0]}.{cur[1]} 이에요. "
            f"{_MIN_PYTHON[0]}.{_MIN_PYTHON[1]} 이상이 필요해요."
        )
        print("    python.org 에서 최신 Python을 설치해보세요.")
        return False
    _ok(f"Python {cur[0]}.{cur[1]}")
    return True


def _check_pip() -> bool:
    if shutil.which("pip") or shutil.which("pip3"):
        _ok("pip")
        return True
    _warn("pip이 없어요. Python 내장 기능으로 복구를 시도할게요...")
    result = subprocess.run(
        [sys.executable, "-m", "ensurepip", "--upgrade"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        _ok("pip 복구 완료")
        return True
    _fail("pip 복구에 실패했어요.")
    print(f"    {_ERR['pip_broken']}")
    return False


def _check_uv() -> bool:
    """uv 감지. 없으면 설치 여부를 물어봄. 현재 세션에서 사용 가능하면 True."""
    if shutil.which("uv"):
        _ok("uv")
        return True

    _warn("uv가 없어요.")
    print("    uv를 설치하면 더 빠르고 안정적으로 패키지를 관리할 수 있어요.")
    try:
        answer = input("    uv를 설치할까요? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        _step("uv 설치를 건너뜁니다. pip으로 진행할게요.")
        return False

    if answer not in {"y", "yes", "ㅇ"}:
        _step("uv 설치를 건너뜁니다. pip으로 진행할게요.")
        return False

    system = platform.system()
    cmd = _UV_INSTALL_CMD.get(system)
    if not cmd:
        _fail(f"지원하지 않는 운영체제예요: {system}")
        return False

    _step("uv를 설치하는 중...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        _fail("uv 설치에 실패했어요.")
        hint = _korean_error(result)
        print(f"    {hint or _ERR['uv_fail']}")
        return False

    # 설치 후 현재 세션 PATH 반영 여부 확인
    if shutil.which("uv"):
        _ok("uv 설치 완료")
        return True

    # 설치는 됐지만 새 터미널에서만 PATH 적용
    _uv_candidates = [
        Path.home() / ".local" / "bin" / "uv",
        Path.home() / ".cargo" / "bin" / "uv",
    ]
    if any(p.exists() for p in _uv_candidates):
        _ok("uv 설치 완료 (새 터미널에서 PATH가 적용돼요)")
        _step("이번 재설치는 pip으로 진행할게요.")
        return False

    _fail("uv 설치 경로를 찾을 수 없어요. pip으로 진행할게요.")
    return False


def _reinstall(use_uv: bool, force: bool) -> bool:
    if use_uv:
        _step("uv 캐시를 정리하는 중...")
        subprocess.run(["uv", "cache", "clean"], capture_output=True)
        cmd = ["uv", "tool", "install", "vibelign", "--no-cache"]
        if force:
            cmd.append("--force")
        _step("vibelign 재설치 중 (uv)...")
    else:
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "vibelign",
            "--upgrade",
            "--no-cache-dir",
        ]
        if force:
            cmd.append("--force-reinstall")
        _step("vibelign 재설치 중 (pip)...")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        combined = (result.stdout or "") + (result.stderr or "")
        already = any(
            k in combined.lower()
            for k in ["already installed", "up-to-date", "up to date", "satisfied"]
        )
        if already and not force:
            _ok("이미 최신 버전이에요")
            print("    강제로 다시 설치하려면: vib init --force")
        else:
            _ok("vibelign 재설치 완료")
        return True

    _fail("vibelign 재설치에 실패했어요.")
    hint = _korean_error(result)
    print(f"    {hint or _ERR['reinstall_fail']}")
    return False


def run_init(args) -> None:
    force = getattr(args, "force", False)

    print("=" * 50)
    print("  VibeLign 업데이트 / 재설치")
    print("=" * 50)
    print()

    print("[1/4] Python 버전 확인")
    if not _check_python():
        return
    print()

    print("[2/4] pip 확인")
    if not _check_pip():
        return
    print()

    print("[3/4] uv 확인")
    uv_ready = _check_uv()
    print()

    print("[4/4] vibelign 재설치")
    success = _reinstall(use_uv=uv_ready, force=force)
    print()

    print("=" * 50)
    if success:
        print("✓ 완료!")
        print()
        print("  지금 터미널을 닫고 새로 열어야 새 버전이 적용돼요.")
        print("  그 다음: vib start")
    else:
        print("✗ 재설치 중 문제가 생겼어요.")
        print("  위의 안내를 따라 해결해보세요.")
    print("=" * 50)
