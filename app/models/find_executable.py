import platform
import shutil
from importlib.resources import files


def get_pea_exec():
    executable = None

    # AppImage works natively
    if platform.system().lower() == "linux":
        executable = files('app.resources').joinpath('ginan.AppImage')

    # PEA available on PATH
    elif shutil.which("pea"):
        executable = ["pea"]

    elif platform.system().lower() == "darwin":
        raise RuntimeError("macOS requires a manual installation of pea on PATH. Please install it from github.com/GeoscienceAustralia/ginan")

    elif platform.system().lower() == "windows":
        # TODO: Check if Ubuntu is installed then try calling it with "pea" command.
        pass

    # Unknown system
    else:
        raise RuntimeError("Unsupported platform: " + platform.system())

    # Test and return executable
    #if not executable:
        #raise RuntimeError("No executable found on *supported* system: " + platform.system())
    #else:
        #return executable

if __name__ == "__main__":
    print(get_pea_exec())