[Setup]
AppName=MyApp
AppVersion=1.0
DefaultDirName={pf}\MyApp
OutputBaseFilename=MyAppInstaller
OutputDir=Output
SetupIconFile=app.ico
PrivilegesRequired=admin
UninstallDisplayIcon={app}\app.ico
Compression=lzma
SolidCompression=yes

[Files]
Source: "simple-app\app.py"; DestDir: "{app}\simple-app"
Source: "wheelhouse\*.*"; DestDir: "{app}\wheelhouse"
Source: "install.py"; DestDir: "{app}"
Source: "run_myapp.bat"; DestDir: "{app}"
Source: "app.ico"; DestDir: "{app}"
Source: "BatToExeConverter.exe"; DestDir: "{tmp}"

[Icons]
; ✅ Use `run_myapp.exe` for the app launcher
Name: "{commondesktop}\Run MyApp"; Filename: "{app}\run_myapp.exe"; IconFilename: "{app}\app.ico"

[Code]
procedure UpdateSetupStatus(Text: string);
begin
  WizardForm.StatusLabel.Caption := Text;
  WizardForm.StatusLabel.Update;
end;

procedure RunInstallScript;
var
  PythonCmd, InstallScript: string;
  ResultCode: Integer;
begin
  PythonCmd := ExpandConstant('{cmd}');
  InstallScript := ExpandConstant('{app}\install.py');

  if FileExists(InstallScript) then
  begin
    // ✅ Step 1: Indicate environment setup
    UpdateSetupStatus('Setting up the environment...');

    // ✅ Step 2: Install dependencies
    UpdateSetupStatus('Installing dependencies... This may take a few minutes.');
    Exec(PythonCmd, '/C python "' + InstallScript + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;

procedure GenerateEXE;
var
  BatPath, ExePath, ConverterPath: string;
  ResultCode: Integer;
begin
  BatPath := ExpandConstant('{app}\run_myapp.bat');
  ExePath := ExpandConstant('{app}\run_myapp.exe');
  ConverterPath := ExpandConstant('{tmp}\BatToExeConverter.exe');

  if FileExists(ConverterPath) and FileExists(BatPath) then
  begin
    // ✅ Compile the .bat file into an invisible Windows application
    Exec(ConverterPath, '/bat "' + BatPath + '" /exe "' + ExePath + '" /icon "{app}\app.ico" /silent /invisible', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;

procedure CleanupAfterInstall;
var
  InstallScript, WheelhouseDir: string;
begin
  InstallScript := ExpandConstant('{app}\install.py');
  WheelhouseDir := ExpandConstant('{app}\wheelhouse');

  if FileExists(InstallScript) then
    DeleteFile(InstallScript);  // ✅ Delete install.py AFTER installation

  if DirExists(WheelhouseDir) then
    DelTree(WheelhouseDir, True, True, True);  // ✅ Delete wheelhouse folder AFTER dependencies are installed
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    RunInstallScript;  // ✅ Install dependencies first
    GenerateEXE;       // ✅ Convert BAT to EXE

    // ✅ Step 3: Indicate finalizing setup
    UpdateSetupStatus('Finalizing installation...');
  end;

  if CurStep = ssDone then
  begin
    CleanupAfterInstall;  // ✅ Cleanup after everything is completed
  end;
end;
