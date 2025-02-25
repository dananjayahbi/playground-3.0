[Setup]
AppName=ChatCompanion
AppVersion=1.0
DefaultDirName={pf}\ChatCompanion
DefaultGroupName=ChatCompanion
OutputDir=Output
OutputBaseFilename=ChatCompanionInstaller
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\icon.ico
Compression=lzma2
SolidCompression=yes
UseSetupLdr=no
DiskSpanning=yes

[Files]
Source: "models\*"; DestDir: "{app}\models"; Flags: recursesubdirs createallsubdirs
Source: "assets\*"; DestDir: "{app}\assets"; Flags: recursesubdirs createallsubdirs
Source: "venvs\dpsn.tar.gz"; DestDir: "{app}"; Flags: deleteafterinstall
Source: "backend.py"; DestDir: "{app}"
Source: "frontend.py"; DestDir: "{app}"
Source: "install.py"; DestDir: "{app}"
Source: "run_myapp.bat"; DestDir: "{app}"
Source: "icon.ico"; DestDir: "{app}"
Source: "BatToExeConverter.exe"; DestDir: "{app}"

[Icons]
Name: "{commondesktop}\Run ChatCompanion"; Filename: "{app}\run_myapp.exe"; IconFilename: "{app}\icon.ico"

[Run]
Filename: "{cmd}"; Parameters: "/C python ""{app}\install.py"""; WorkingDir: "{app}"; Flags: runhidden waituntilterminated

[UninstallRun]
Filename: "{cmd}"; Parameters: "/C conda remove --name dpsn --all -y"; Flags: runhidden waituntilterminated

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
procedure GenerateEXE;
var
  BatPath, ExePath, ConverterPath, LogFile: string;
  ResultCode: Integer;
begin
  BatPath := ExpandConstant('{app}\run_myapp.bat');
  ExePath := ExpandConstant('{app}\run_myapp.exe');
  ConverterPath := ExpandConstant('{app}\BatToExeConverter.exe');
  LogFile := ExpandConstant('{app}\converter_log.txt');

  if FileExists(ConverterPath) and FileExists(BatPath) then
  begin
    WizardForm.StatusLabel.Caption := 'Converting batch file to EXE...';
    WizardForm.StatusLabel.Update;

    Exec(ConverterPath, '/bat "' + BatPath + '" /exe "' + ExePath + '" /icon "{app}\icon.ico" /invisible > "' + LogFile + '" 2>&1', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

    if FileExists(ExePath) then
    begin
      WizardForm.StatusLabel.Caption := 'EXE Created Successfully!';
      WizardForm.StatusLabel.Update;
      DeleteFile(ConverterPath); 
    end
    else
    begin
      WizardForm.StatusLabel.Caption := 'Failed to create EXE! Check log.';
      WizardForm.StatusLabel.Update;
    end;
  end
  else
  begin
    WizardForm.StatusLabel.Caption := 'Error: BatToExeConverter.exe not found!';
    WizardForm.StatusLabel.Update;
  end;
end;

procedure UpdateSetupStatus(Text: string);
begin
  WizardForm.StatusLabel.Caption := Text;
  WizardForm.StatusLabel.Update;
end;

procedure CleanupAfterInstall;
var
  InstallScript, VenvArchive: string;
begin
  InstallScript := ExpandConstant('{app}\install.py');
  VenvArchive := ExpandConstant('{app}\dpsn.tar.gz');

  if FileExists(InstallScript) then
  begin
    DeleteFile(InstallScript);  
  end;

  if FileExists(VenvArchive) then
  begin
    DeleteFile(VenvArchive);  
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    UpdateSetupStatus('Setting up the environment...');
    GenerateEXE;
    CleanupAfterInstall;
    UpdateSetupStatus('Installation completed successfully!');
  end;
end;
