import os
import pathlib
import platform
import shutil
import subprocess


def get_pea_exec() -> pathlib.Path | [str]:

    # PEA available on PATH
    if shutil.which("pea"):
        executable = ["pea"]

    # Attempts executing AppImage natively
    elif platform.system().lower() == "linux":
        executable = pathlib.Path(f"{os.getcwd()}/../resources/ginan.AppImage")

    # Automated docker install and setup linking /data to CWD.
    elif platform.system().lower() == "darwin":
        pass

    # Uses/Installs WSL and Ubuntu before executing PEA
    ## TODO - Test and complete on windows system
    elif platform.system().lower() == "windows":
        # Check if WSL is installed
        if not shutil.which("wsl"):
            result = subprocess.run(['powershell.exe', '-Command',
                                     'Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart'],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                print("WSL enabled successfully. Please restart your computer.")
            else:
                raise RuntimeError(f"Error enabling WSL: {result.stderr}")

        # Check if Ubuntu is installed
        try:
            subprocess.call(['wsl', '--install', '-d', 'Ubuntu'], text=True)
            return pathlib.Path(f"{os.getcwd()}/../resources/ginan.AppImage")
        except subprocess.CalledProcessError as e:
            print(f"Error installing Ubuntu: {e.stderr}")
            raise RuntimeError("Error installing Ubuntu")

        # Execute PEA AppImage
        pass

    # Unknown system
    else:
        raise RuntimeError("Unsupported platform: " + platform.system())

    # Test and return executable
    if not executable:
        raise RuntimeError("No executable found yet running on supported system: " + platform.system())
    else:
        _test_executable(executable)
        return executable

def _test_executable(pea_exec):
    try:
        subprocess.call(pea_exec, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Error running PEA executable: {e.stderr}")
        raise RuntimeError("Error running PEA executable")

if __name__ == "__main__":
    print(get_pea_exec().resolve())