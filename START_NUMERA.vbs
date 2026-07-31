Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)
shell.Run "cmd /c cd /d """ & root & "\backend"" && python -m uvicorn numera.main:app --app-dir src --host 127.0.0.1 --port 8000", 0, False
WScript.Sleep 2500
shell.Run "cmd /c cd /d """ & root & "\frontend"" && npm run dev", 0, False
WScript.Sleep 5000
shell.Run "http://localhost:3000", 1, False
