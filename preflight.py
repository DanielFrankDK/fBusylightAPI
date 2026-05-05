"""Checks and installs dependencies before the server starts."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def _run_sudo(*args) -> bool:
    result = subprocess.run(["sudo", *args])
    return result.returncode == 0


def ensure_udev():
    dst = Path("/etc/udev/rules.d/99-luxafor.rules")
    if dst.exists():
        return
    print(">>> Installing udev rules for non-root USB access (sudo required)...")
    src = ROOT / "99-luxafor.rules"
    ok = (
        _run_sudo("cp", str(src), str(dst))
        and _run_sudo("udevadm", "control", "--reload")
        and _run_sudo("udevadm", "trigger")
    )
    if not ok:
        print("    WARNING: udev rules not installed — device access may require root.")
        print(f"    Run manually: sudo cp {src} {dst} && sudo udevadm control --reload && sudo udevadm trigger")
        return
    user = os.environ.get("USER") or os.environ.get("LOGNAME", "")
    if user:
        _run_sudo("usermod", "-aG", "plugdev", user)
    print(">>> udev rules installed. Log out and back in for group changes to take effect.")


def ensure_pip_packages():
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
        import usb.core  # noqa: F401
    except ImportError:
        print(">>> Installing Python dependencies...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")],
            check=True,
        )
        os.execv(sys.executable, [sys.executable] + sys.argv)


def run():
    ensure_udev()
    ensure_pip_packages()
