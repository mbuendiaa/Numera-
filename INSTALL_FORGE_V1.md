# Install Numera Forge v1

1. Delete old folder: `tools/forge`
2. Copy the new `tools/forge` folder into your Numera repository.
3. Install:

```powershell
cd C:\Users\marta\OneDrive\Documentos\GitHub\Numera-\tools\forge
py -m pip install -e .
```

4. Go back to root:

```powershell
cd ..\..
```

5. Test:

```powershell
forge --help
forge docs --help
forge docs new ai 04_Context_Engine --title "Context Engine" --id AI-04
forge docs index
forge docs validate
```
