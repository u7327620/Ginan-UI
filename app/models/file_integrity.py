import os
import pathlib
import platform
import shutil
import subprocess


def get_pea_exec() -> pathlib.Path:
    if platform.system().lower() == "linux":
        try:
            path = pathlib.Path(f"{os.getcwd()}/../resources/ginan.AppImage")
            subprocess.run(path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return path
        except FileNotFoundError:
            raise RuntimeError("Ginan executable for linux not found, check resources folder has ginan.AppImage")
    elif platform.system().lower() == "windows":
        # Check if wsl is available
        if not shutil.which("wsl"):
            result = subprocess.run(['powershell.exe', '-Command',
                                     'Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart'],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                print("WSL enabled successfully. Please restart your computer.")
            else:
                raise RuntimeError(f"Error enabling WSL: {result.stderr}")
        # Ubuntu and run commands
        try:
            subprocess.call(['wsl', '--install', '-d', 'Ubuntu'], text=True)
            ## TODO - See how to call appImage after this step...
            return pathlib.Path(f"{os.getcwd()}/../resources/ginan.AppImage")
        except subprocess.CalledProcessError as e:
            print(f"Error installing Ubuntu: {e.stderr}")
            raise RuntimeError("Error installing Ubuntu")
    else:
        raise RuntimeError("Unsupported platform: " + platform.system())

if __name__ == "__main__":
    print(get_pea_exec().resolve())
