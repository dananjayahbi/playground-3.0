import os
import subprocess
import shutil

# Configuration
APP_NAME = "MyApp"
CONDA_ENV_NAME = "myapp_env"
ANACONDA_INSTALLER_URL = "https://repo.anaconda.com/archive/Anaconda3-2023.07-Windows-x86_64.exe"
ANACONDA_PATH = os.path.join(os.environ['USERPROFILE'], "anaconda3")
INSTALL_DIR = os.path.dirname(os.path.abspath(__file__))  # Get correct install path
WHEELHOUSE_DIR = os.path.join(INSTALL_DIR, "wheelhouse")  # ✅ Now correctly set
APP_DIR = os.path.join(INSTALL_DIR, "simple-app")
BATCH_FILE_PATH = os.path.join(INSTALL_DIR, "run_myapp.bat")
DESKTOP_SHORTCUT = os.path.join(os.environ["USERPROFILE"], "Desktop", "Run MyApp.lnk")
ICON_PATH = os.path.join(INSTALL_DIR, "app.ico")

def run_command(command):
    """Run a shell command and print output."""
    process = subprocess.run(command, shell=True, text=True, capture_output=True)
    print(process.stdout)
    if process.stderr:
        print("ERROR:", process.stderr)

def is_anaconda_installed():
    """Check if Anaconda is installed."""
    return os.path.exists(ANACONDA_PATH)

def install_anaconda():
    """Download and install Anaconda."""
    installer_path = os.path.join(os.environ['TEMP'], "AnacondaInstaller.exe")
    if not os.path.exists(installer_path):
        print("Downloading Anaconda...")
        run_command(f"powershell -Command Invoke-WebRequest -Uri {ANACONDA_INSTALLER_URL} -OutFile {installer_path}")

    print("Installing Anaconda...")
    run_command(f'"{installer_path}" /InstallationType=JustMe /RegisterPython=0 /S')

    # Add Anaconda to system PATH
    os.environ["PATH"] += f";{ANACONDA_PATH}\\Scripts;{ANACONDA_PATH}\\Library\\bin"

def create_conda_env():
    """Create a Conda virtual environment."""
    print(f"Creating Conda environment: {CONDA_ENV_NAME}...")
    run_command(f"{ANACONDA_PATH}\\Scripts\\conda create -y -n {CONDA_ENV_NAME} python=3.11")

def install_dependencies():
    """Ensure the Conda environment is activated before installing wheels."""
    print("Activating Conda environment and installing dependencies from wheelhouse...")

    if not os.path.exists(WHEELHOUSE_DIR):
        print(f"ERROR: Wheelhouse directory not found: {WHEELHOUSE_DIR}")
        return

    for file in os.listdir(WHEELHOUSE_DIR):
        if file.endswith(".whl"):
            wheel_path = os.path.join(WHEELHOUSE_DIR, file)
            run_command(f'call "{ANACONDA_PATH}\\Scripts\\activate.bat" {CONDA_ENV_NAME} && pip install "{wheel_path}"')

    print("All dependencies installed.")

def cleanup_wheelhouse():
    """Remove only the wheelhouse directory after installation."""
    if os.path.exists(WHEELHOUSE_DIR):
        shutil.rmtree(WHEELHOUSE_DIR)
        print("Wheelhouse directory deleted.")

def create_run_script():
    """Create a script to run the app inside the Conda environment."""
    with open(BATCH_FILE_PATH, "w") as f:
        f.write(f'@echo off\n')
        f.write(f'cd /d "{INSTALL_DIR}"\n')  # Ensure it runs in the correct directory
        f.write(f'call "{ANACONDA_PATH}\\Scripts\\activate.bat" {CONDA_ENV_NAME}\n')
        f.write(f'python "{os.path.join(APP_DIR, "app.py")}"\n')

    print(f"Run script created: {BATCH_FILE_PATH}")

def create_desktop_shortcut():
    """Create a shortcut to the batch file on the desktop."""
    shortcut_script = f'''
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("{DESKTOP_SHORTCUT}")
    $Shortcut.TargetPath = "{BATCH_FILE_PATH}"
    $Shortcut.IconLocation = "{ICON_PATH}"
    $Shortcut.Save()
    '''
    shortcut_path = os.path.join(os.environ['TEMP'], "create_shortcut.ps1")
    with open(shortcut_path, "w") as f:
        f.write(shortcut_script)
    run_command(f"powershell -ExecutionPolicy Bypass -File {shortcut_path}")

def main():
    print("Installation started...")

    if not is_anaconda_installed():
        install_anaconda()
    
    create_conda_env()
    install_dependencies()
    cleanup_wheelhouse()
    create_run_script()
    create_desktop_shortcut()

    print("Installation completed successfully!")

if __name__ == "__main__":
    main()
