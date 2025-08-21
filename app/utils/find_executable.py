import platform
import shutil
from importlib.resources import files


def get_pea_exec():
    # AppImage works natively
    if platform.system().lower() == "linux":
        executable = files('app.resources').joinpath('ginan.AppImage')

    # PEA available on PATH
    elif shutil.which("pea"):
        executable = "pea"

    elif platform.system().lower() == "darwin":
        executable = files('app.resources.osx_arm64.bin').joinpath('pea')

    elif platform.system().lower() == "windows":
        raise RuntimeError("MichaelSoft WiNdLoWs cAn'T PEa")

    # Unknown system
    else:
        raise RuntimeError("Unsupported platform: " + platform.system())

    return executable

if __name__ == "__main__":
    print(get_pea_exec())