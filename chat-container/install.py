import os
import subprocess

# Configuration
APP_NAME = "Chat Companion"
CONDA_ENV_NAME = "depressionappenv"
VENV_ARCHIVE = "dpsn.tar.gz"
ANACONDA_PATH = os.path.join(os.environ['USERPROFILE'], "anaconda3")
MINICONDA_PATH = os.path.join(os.environ['USERPROFILE'], "miniconda3")
INSTALL_DIR = os.path.dirname(os.path.abspath(__file__))  
APP_DIR = os.path.join(INSTALL_DIR, "llm-chat-app")
BATCH_FILE_PATH = os.path.join(INSTALL_DIR, "run_myapp.bat")
EXE_FILE_PATH = os.path.join(INSTALL_DIR, "run_myapp.exe")
ICON_PATH = os.path.join(INSTALL_DIR, "icon.ico")
VENV_ARCHIVE_PATH = os.path.join(INSTALL_DIR, VENV_ARCHIVE)
BATOEXE_TOOL = os.path.join(INSTALL_DIR, "BatToExeConverter.exe")

def run_command(command):
    """Run a shell command and print output."""
    process = subprocess.run(command, shell=True, text=True, capture_output=True)
    print(process.stdout)
    if process.stderr:
        print("ERROR:", process.stderr)

def is_conda_installed():
    """Check if Anaconda or Miniconda is installed."""
    return os.path.exists(ANACONDA_PATH) or os.path.exists(MINICONDA_PATH)

def get_conda_path():
    """Return the path to Anaconda or Miniconda, installing Miniconda if necessary."""
    if os.path.exists(ANACONDA_PATH):
        return ANACONDA_PATH
    elif os.path.exists(MINICONDA_PATH):
        return MINICONDA_PATH
    else:
        return install_miniconda()

def install_miniconda():
    """Download and install Miniconda."""
    installer_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
    installer_path = os.path.join(os.environ['TEMP'], "MinicondaInstaller.exe")

    if not os.path.exists(installer_path):
        print("Downloading Miniconda...")
        run_command(f"powershell -Command Invoke-WebRequest -Uri {installer_url} -OutFile {installer_path}")

    print("Installing Miniconda...")
    run_command(f'"{installer_path}" /InstallationType=JustMe /RegisterPython=0 /S')

    return MINICONDA_PATH

def extract_conda_env(conda_path):
    """Extract the prebuilt Conda environment from .tar.gz."""
    venvs_dir = os.path.join(conda_path, "envs")
    extracted_env_path = os.path.join(venvs_dir, CONDA_ENV_NAME)

    if not os.path.exists(extracted_env_path):
        os.makedirs(extracted_env_path)

    print(f"Extracting Conda environment to {extracted_env_path}...")
    run_command(f'tar -xzf "{VENV_ARCHIVE_PATH}" -C "{extracted_env_path}"')

    print(f"Conda environment '{CONDA_ENV_NAME}' is ready!")

def convert_bat_to_exe():
    """Convert the batch file to an executable using BatToExeConverter.exe"""
    if os.path.exists(BATOEXE_TOOL):
        print("Converting batch file to EXE...")
        run_command(f'"{BATOEXE_TOOL}" /bat "{BATCH_FILE_PATH}" /exe "{EXE_FILE_PATH}" /icon "{ICON_PATH}"')
    else:
        print("ERROR: BatToExeConverter.exe not found!")

def cleanup_files():
    """Delete unnecessary files after installation."""
    if os.path.exists(VENV_ARCHIVE_PATH):
        os.remove(VENV_ARCHIVE_PATH)
        print(f"Deleted {VENV_ARCHIVE_PATH}")

    install_script = os.path.join(INSTALL_DIR, "install.py")
    if os.path.exists(install_script):
        os.remove(install_script)
        print(f"Deleted {install_script}")

def main():
    print("Installation started...")

    conda_path = get_conda_path()
    extract_conda_env(conda_path)
    convert_bat_to_exe()
    cleanup_files()

    print("Installation completed successfully!")

if __name__ == "__main__":
    main()
