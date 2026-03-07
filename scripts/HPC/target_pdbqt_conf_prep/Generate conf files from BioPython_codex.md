

Generate conf files from BioPython
1 task in progress


## Me:
OK but but can I create a Python environment in the cell in the command cell whatever is that it's in the terminal in the VS Code Can I create a Python environment so as not to start mixing things around?

GPT:
Yes. That is the best approach.

In your FDA folder terminal (PowerShell), run:

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install biopython
Then run your script with the venv Python:

python "H:\My Drive\VSCode_Github\scripts\Version_B\box_Proteins_03.py" `
  --csv ".\fused\compounds_with_pdb_flat_selected_PPT_column.csv" `
  --pdb-dir ".\fused\PDB_bioassembly" `
  --out-dir ".\fused\PDB_bioassembly\conf" `
  --has-header
Optional (VS Code): Ctrl+Shift+P -> Python: Select Interpreter -> choose .\.venv\Scripts\python.exe.


## Me:
PS C:\Users\geras\Partners HealthCare Dropbox\Evangelos Papadopoulos\MMSEGs Discussion\GeneDeepDives\Evangelos\PDB_Evangelos\FDA> .\.venv\Scripts\Activate.ps1
.\.venv\Scripts\Activate.ps1 : File C:\Users\geras\Partners HealthCare Dropbox\Evangelos Papadopoulos\MMSEGs Discussion\GeneDeepDives\Evangelos\PDB_Evangelos\FDA\.venv\Scripts\Activate.ps1 
cannot be loaded because running scripts is disabled on this system. For more information, see about_Execution_Policies at https:/go.microsoft.com/fwlink/?LinkID=135170.
At line:1 char:1
+ .\.venv\Scripts\Activate.ps1
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : SecurityError: (:) [], PSSecurityException
    + FullyQualifiedErrorId : UnauthorizedAccess
PS C:\Users\geras\Partners HealthCare Dropbox\Evangelos Papadopoulos\MMSEGs Discussion\GeneDeepDives\Evangelos\PDB_Evangelos\FDA> python -m pip install --upgrade pip
Defaulting to user installation because normal site-packages is not writeable
Requirement already satisfied: pip in c:\program files\windowsapps\pythonsoftwarefoundation.python.3.13_3.13.3312.0_x64__qbz5n2kfra8p0\lib\site-packages (25.3)
Collecting pip
  Downloading pip-26.0.1-py3-none-any.whl.metadata (4.7 kB)
Downloading pip-26.0.1-py3-none-any.whl (1.8 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.8/1.8 MB 1.9 MB/s  0:00:02
Installing collected packages: pip
  WARNING: The scripts pip.exe, pip3.13.exe and pip3.exe are installed in 'C:\Users\geras\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts' which is not on PATH.
  Consider adding this directory to PATH or, if you prefer to suppress this warning, use --no-warn-script-location.
Successfully installed pip-26.0.1

[notice] A new release of pip is available: 25.3 -> 26.0.1
[notice] To update, run: C:\Users\geras\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe -m pip install --upgrade pip
PS C:\Users\geras\Partners HealthCare Dropbox\Evangelos Papadopoulos\MMSEGs Discussion\GeneDeepDives\Evangelos\PDB_Evangelos\FDA> python -m pip install biopython
Defaulting to user installation because normal site-packages is not writeable
Collecting biopython
  Downloading biopython-1.86-cp313-cp313-win_amd64.whl.metadata (13 kB)
Collecting numpy (from biopython)
  Downloading numpy-2.4.2-cp313-cp313-win_amd64.whl.metadata (6.6 kB)
Downloading biopython-1.86-cp313-cp313-win_amd64.whl (2.7 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.7/2.7 MB 4.4 MB/s  0:00:00
Downloading numpy-2.4.2-cp313-cp313-win_amd64.whl (12.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 12.3/12.3 MB 4.4 MB/s  0:00:02
Installing collected packages: numpy, biopython
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 0/2 [numpy]  WARNING: The scripts f2py.exe and numpy-config.exe are installed in 'C:\Users\geras\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts' which is not on PATH.
  Consider adding this directory to PATH or, if you prefer to suppress this warning, use --no-warn-script-location.
Successfully installed biopython-1.86 numpy-2.4.2                                                                                                                                               
PS C:\Users\geras\Partners HealthCare Dropbox\Evangelos Papadopoulos\MMSEGs Discussion\GeneDeepDives\Evangelos\PDB_Evangelos\FDA> 
PS C:\Users\geras\Partners HealthCare Dropbox\Evangelos Papadopoulos\MMSEGs Discussion\GeneDeepDives\Evangelos\PDB_Evangelos\FDA>

GPT:
You’re in good shape now: BioPython installed successfully.

To avoid activation-policy issues, use the venv Python directly (no activation needed):

.\.venv\Scripts\python.exe -m pip install --upgrade pip biopython
.\.venv\Scripts\python.exe "H:\My Drive\VSCode_Github\scripts\Version_B\box_Proteins_03.py" `
  --csv ".\fused\compounds_with_pdb_flat_selected_PPT_column.csv" `
  --pdb-dir ".\fused\PDB_bioassembly" `
  --out-dir ".\fused\PDB_bioassembly\conf" `
  --has-header
If you still want activation in PowerShell, use one of these:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
or permanent for your user:

Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
Also verify which Python is running:

python -c "import sys; print(sys.executable)"
.\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"

## Me:

I do not understand why I don't need activation of the environment can I also somehow activate it to see it?

GPT:
You don’t need activation because this already works:

.\.venv\Scripts\python.exe your_script.py
That directly uses the venv’s Python, so packages come from that environment.

Activation is just a convenience:

It changes PATH so python points to .venv.
It usually changes the prompt to show (.venv).
You can activate and see it like this (temporary, current terminal only):

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
Then check:

python -c "import sys; print(sys.executable)"
It should print a path ending in \.venv\Scripts\python.exe, and your prompt should show (.venv).

To leave the environment:

deactivate

## Me:

For some reason as you can see it never created any confirmation files it could not find the PDB and maybe because the PDBS are of particular naming as you can see:

geras@Papa:/mnt/c/Users/geras/Partners HealthCare Dropbox/Evangelos Papadopoulos/MMSEGs Discussion/GeneDeepDives/Evangelos/PDB_Evangelos/FDA$ ls ./fused/PDB_bioassembly/ | head
110D.assembly1.pdb
146D.assembly1.pdb
151D.assembly1.pdb
152D.assembly1.pdb
198D.assembly1.pdb
1A4L.assembly1.pdb
1AO8.assembly1.pdb
1AXW.assembly1.pdb
1C3S.assembly1.pdb
1C9H.assembly1.pdb
geras@Papa:/mnt/c/Users/geras/Partners HealthCare Dropbox/Evangelos Papadopoulos/MMSEGs Discussion/GeneDeepDives/Evangelos/PDB_Evangelos/FDA$ 

geras@Papa:/mnt/c/Users/geras/Partners HealthCare Dropbox/Evangelos Papadopoulos/MMSEGs Discussion/GeneDeepDives/Evangelos/PDB_Evangelos/FDA$ ls ./fused/PDB_bioassembly/ | head
110D.assembly1.pdb
146D.assembly1.pdb
151D.assembly1.pdb
152D.assembly1.pdb
198D.assembly1.pdb
1A4L.assembly1.pdb
1AO8.assembly1.pdb
1AXW.assembly1.pdb
1C3S.assembly1.pdb
1C9H.assembly1.pdb
geras@Papa:/mnt/c/Users/geras/Partners HealthCare Dropbox/Evangelos Papadopoulos/MMSEGs Discussion/GeneDeepDives/Evangelos/PDB_Evangelos/FDA$


2 previous messages
GPT:
Exactly, that was the issue. I patched the resolver to support names like 1A4L.assembly1.pdb (and other PDBCODE*.pdb matches) in box_Proteins_03.py.

Run again:

python "H:\My Drive\VSCode_Github\scripts\Version_B\box_Proteins_03.py" `
  --csv ".\fused\compounds_with_pdb_flat_selected_PPT_column.csv" `
  --pdb-dir ".\fused\PDB_bioassembly" `
  --out-dir ".\fused\PDB_bioassembly\conf" `
  --has-header
If you’re running a different copy (PyMol/box_Proteins_03.py), use this updated one or copy the same changes there too.


## Me:
-a---l         2/21/2026   2:59 AM        1968219 8UTY.assembly1.pdb
-a---l         2/21/2026   2:59 AM        1826955 8V8U.assembly1.pdb
-a---l         2/21/2026   2:59 AM        1582659 8V8V.assembly1.pdb
-a---l         2/21/2026   2:59 AM        6362226 8V9R.assembly1.pdb
-a---l         2/21/2026   2:59 AM         388638 8VAC.assembly1.pdb
-a---l         2/22/2026   2:10 AM         612243 8VB5-assembly1.cif
-a---l         2/22/2026   2:24 AM         218321 8VB5.assembly1.pdb
-a---l         2/21/2026   2:59 AM         416421 8W38.assembly1.pdb
-a---l         2/21/2026   2:59 AM         387585 8W3B.assembly1.pdb
-a---l         2/21/2026   2:59 AM         419661 8W3D.assembly1.pdb
-a---l         2/21/2026   2:59 AM         283419 8XI9.assembly1.pdb
-a---l         2/21/2026   2:59 AM         838836 8XOM.assembly1.pdb
-a---l         2/21/2026   2:59 AM         262521 8XV9.assembly1.pdb
-a---l         2/21/2026   2:59 AM        3857139 8YCX.assembly1.pdb
-a---l         2/21/2026   2:59 AM        2996838 8YD0.assembly1.pdb
-a---l         2/21/2026   2:59 AM        3608469 8YD1.assembly1.pdb
-a---l         2/21/2026   2:59 AM        1624941 8YD2.assembly1.pdb
-a---l         2/21/2026   2:59 AM        1120716 8YGE.assembly1.pdb
-a---l         2/21/2026   2:59 AM         275157 8YGQ.assembly1.pdb
-a---l         2/21/2026   2:59 AM         948915 8YO7.assembly1.pdb
-a---l         2/21/2026   2:59 AM         156006 8YYA.assembly1.pdb
-a---l         2/21/2026   2:59 AM         260820 8Z7U.assembly1.pdb
-a---l         2/21/2026   2:59 AM         256527 8Z7Y.assembly1.pdb
-a---l         2/21/2026   2:59 AM         815913 8ZBS.assembly1.pdb
-a---l         2/21/2026   2:59 AM         812106 8ZBT.assembly1.pdb
-a---l         2/21/2026   2:59 AM         814617 8ZBU.assembly1.pdb
-a---l         2/21/2026   2:59 AM        6327639 9C87.assembly1.pdb
-a---l         2/21/2026   3:00 AM        3858435 9CE8.assembly1.pdb
-a---l         2/21/2026   3:00 AM         471015 9CJ1.assembly1.pdb
-a---l         2/21/2026   3:00 AM         777438 9CTF.assembly1.pdb
-a---l         2/21/2026   3:00 AM         302211 9D5E.assembly1.pdb
-a---l         2/21/2026   3:00 AM         297432 9D5F.assembly1.pdb
-a---l         2/21/2026   3:00 AM         295407 9D5H.assembly1.pdb
-a---l         2/21/2026   3:00 AM         301077 9D5P.assembly1.pdb
-a---l         2/21/2026   3:00 AM         857466 9D6X.assembly1.pdb
-a---l         2/21/2026   3:00 AM         892215 9D6Z.assembly1.pdb
-a---l         2/21/2026   3:00 AM         447849 9D71.assembly1.pdb
-a---l         2/21/2026   3:00 AM        1752273 9DA8.assembly1.pdb
-a---l         2/21/2026   3:00 AM        1173609 9DHZ.assembly1.pdb
-a---l         2/21/2026   3:00 AM         777924 9DI0.assembly1.pdb
-a---l         2/21/2026   3:00 AM        1692090 9DKW.assembly1.pdb
-a---l         2/21/2026   3:00 AM        3270780 9DQL.assembly1.pdb
-a---l         2/21/2026   3:00 AM        1658799 9DW3.assembly1.pdb
-a---l         2/22/2026   2:10 AM       16266539 9EOK-assembly1.cif
-a---l         2/21/2026   3:00 AM         573642 9FOS.assembly1.pdb
-a---l         2/21/2026   3:00 AM        3355506 9G6I.assembly1.pdb
-a---l         2/21/2026   3:00 AM         831060 9GKV.assembly1.pdb
-a---l         2/21/2026   3:00 AM        1082889 9GKX.assembly1.pdb
-a---l         2/21/2026   3:00 AM        3701214 9GN6.assembly1.pdb
-a---l         2/21/2026   3:00 AM         774360 9GNQ.assembly1.pdb
-a---l         2/21/2026   3:00 AM         248103 9GOI.assembly1.pdb
-a---l         2/21/2026   3:00 AM        3387744 9H1O.assembly1.pdb
-a---l         2/21/2026   3:00 AM        1480275 9HQ4.assembly1.pdb
-a---l         2/21/2026   3:00 AM          82863 9JL7.assembly1.pdb
-a---l         2/21/2026   3:00 AM         262278 9JRK.assembly1.pdb
-a---l         2/21/2026   3:00 AM        3894642 9JVP.assembly1.pdb
-a---l         2/21/2026   3:00 AM        1624374 9JVZ.assembly1.pdb
-a---l         2/21/2026   3:00 AM         632934 9KRM.assembly1.pdb
-a---l         2/21/2026   3:00 AM         886302 9LGC.assembly1.pdb
-a---l         2/22/2026   2:10 AM        1110948 9LPD-assembly1.cif
-a---l         2/22/2026   2:24 AM         420479 9LPD.assembly1.pdb
-a---l         2/21/2026   3:00 AM        1438965 9NTG.assembly1.pdb
-a---l         2/21/2026   3:00 AM         688662 9NTJ.assembly1.pdb
-a---l         2/22/2026   2:10 AM       33533713 9NTM-assembly1.cif
-a---l         2/22/2026   1:59 AM            441 9O0R.pdb1.gz
-a---l         2/21/2026   3:00 AM         213030 9O8X.assembly1.pdb
-a---l         2/21/2026   3:00 AM         202419 9OAF.assembly1.pdb
-a---l         2/21/2026   3:00 AM         197802 9OAM.assembly1.pdb
-a---l         2/21/2026   3:00 AM         203067 9OBJ.assembly1.pdb
-a---l         2/21/2026   3:00 AM         130896 9ONI.assembly1.pdb
-a---l         2/21/2026   3:00 AM        1103382 9OT2.assembly1.pdb
-a---l         2/21/2026   3:00 AM         176904 9P6A.assembly1.pdb
-a---l         2/21/2026   3:00 AM         720171 9RSJ.assembly1.pdb


(.venv) PS C:\Users\geras\Partners HealthCare Dropbox\Evangelos Papadopoulos\MMSEGs Discussion\GeneDeepDives\Evangelos\PDB_Evangelos\FDA> python "H:\My Drive\VSCode_Github\scripts\Version_B\box_Proteins_03.py" 
>>   --csv ".\fused\compounds_with_pdb_flat_selected_PPT_column.csv" 
>>   --pdb-dir ".\fused\PDB_bioassembly" 
>>   --out-dir ".\fused\PDB_bioassembly\conf" 
>>   --has-header
SKIP row 2: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 3: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 4: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 5: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 6: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 7: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 8: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 9: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 10: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 11: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 12: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 13: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 14: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 15: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 16: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 17: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 18: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 19: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 20: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 21: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 22: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 23: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 24: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 25: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 26: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 27: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 28: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 29: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 30: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 31: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 32: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 33: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 34: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 35: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 36: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 37: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 38: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 39: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 40: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 41: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 42: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 43: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 44: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 45: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 46: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 47: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 48: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 49: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 50: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 51: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 52: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 53: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 54: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 55: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 56: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 57: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 58: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 59: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 60: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 61: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 62: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 63: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 64: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 65: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 66: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 67: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 68: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 69: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 70: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 71: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 72: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 73: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 74: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 75: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 76: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 77: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 78: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 79: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 80: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 81: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 82: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 83: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 84: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 85: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 86: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 87: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 88: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 89: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 90: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 91: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 92: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 93: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 94: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 95: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 96: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 97: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 98: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 99: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 100: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 101: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 102: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 103: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 104: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 105: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 106: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 107: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 108: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 109: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 110: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 111: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 112: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 113: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 114: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 115: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 116: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 117: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 118: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 119: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 120: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 121: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 122: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 123: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 124: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 125: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 126: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 127: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 128: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 129: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 130: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 131: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 132: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 133: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 134: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 135: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 136: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 137: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 138: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 139: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 140: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 141: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 142: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 143: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 144: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 145: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 146: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 147: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 148: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 149: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 150: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 151: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 152: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 153: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 154: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 155: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 156: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 157: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 158: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 159: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 160: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 161: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 162: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 163: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 164: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 165: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 166: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 167: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 168: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 169: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 170: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 171: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 172: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 173: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 174: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 175: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 176: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 177: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 178: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 179: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 180: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 181: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 182: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 183: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 184: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 185: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 186: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 187: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 188: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 189: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 190: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 191: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 192: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 193: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 194: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 195: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 196: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 197: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 198: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 199: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 200: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 201: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 202: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 203: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 204: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 205: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 206: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 207: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 208: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 209: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 210: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 211: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 212: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 213: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 214: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 215: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 216: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 217: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 218: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 219: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 220: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 221: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 222: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 223: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 224: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 225: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 226: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 227: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 228: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 229: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 230: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 231: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 232: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 233: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 234: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 235: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 236: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 237: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 238: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 239: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 240: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 241: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 242: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 243: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 244: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 245: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 246: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 247: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 248: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 249: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 250: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 251: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 252: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 253: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 254: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 255: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 256: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 257: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 258: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 259: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 260: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 261: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 262: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 263: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 264: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 265: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 266: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 267: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 268: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 269: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 270: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 271: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 272: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 273: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 274: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 275: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 276: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 277: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 278: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 279: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 280: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 281: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 282: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 283: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 284: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 285: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 286: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 287: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 288: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 289: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 290: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 291: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 292: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 293: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 294: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 295: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 296: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 297: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 298: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 299: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 300: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 301: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 302: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 303: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 304: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 305: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 306: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 307: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 308: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 309: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 310: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 311: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 312: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 313: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 314: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 315: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 316: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 317: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 318: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 319: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 320: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 321: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 322: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 323: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 324: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 325: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 326: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 327: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 328: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 329: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 330: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 331: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 332: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 333: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 334: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 335: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 336: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 337: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 338: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 339: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 340: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 341: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 342: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 343: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 344: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 345: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 346: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 347: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 348: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 349: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 350: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 351: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 352: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 353: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 354: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 355: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 356: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 357: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 358: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 359: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 360: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 361: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 362: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 363: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 364: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 365: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 366: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 367: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 368: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 369: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 370: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 371: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 372: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 373: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 374: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 375: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 376: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 377: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 378: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 379: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 380: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 381: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 382: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 383: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 384: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 385: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 386: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 387: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 388: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 389: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 390: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 391: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 392: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 393: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 394: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 395: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 396: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 397: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 398: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 399: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 400: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 401: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 402: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 403: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 404: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 405: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 406: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 407: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 408: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 409: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 410: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 411: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 412: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 413: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 414: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 415: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 416: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 417: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 418: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 419: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 420: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 421: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 422: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 423: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 424: invalid pdb/ligand values (pdb='', ligand='')
SKIP row 425: invalid pdb/ligand values (pdb='', ligand='')
DONE: wrote 0 conf file(s), skipped 424 row(s).
(.venv) PS C:\Users\geras\Partners HealthCare Dropbox\Evangelos Papadopoulos\MMSEGs Discussion\GeneDeepDives\Evangelos\PDB_Evangelos\FDA> 
(.venv) PS C:\Users\geras\Partners HealthCare Dropbox\Evangelos Papadopoulos\MMSEGs Discussion\GeneDeepDives\Evangelos\PDB_Evangelos\FDA>

GPT:
You fixed the PDB filename issue; now the new failure is CSV parsing.

invalid pdb/ligand values (pdb='', ligand='') for every row means your file is being split wrong (most likely ; delimiter instead of ,), so columns 3/4 are empty.

Try this first:

python "H:\My Drive\VSCode_Github\scripts\Version_B\box_Proteins_03.py" `
  --csv ".\fused\compounds_with_pdb_flat_selected_PPT_column.csv" `
  --pdb-dir ".\fused\PDB_bioassembly" `
  --out-dir ".\fused\PDB_bioassembly\conf" `
  --has-header `
  --delimiter ";"
If still empty, test column indices:

python "H:\My Drive\VSCode_Github\scripts\Version_B\box_Proteins_03.py" `
  --csv ".\fused\compounds_with_pdb_flat_selected_PPT_column.csv" `
  --pdb-dir ".\fused\PDB_bioassembly" `
  --out-dir ".\fused\PDB_bioassembly\conf" `
  --has-header `
  --delimiter ";" `
  --pdb-col 4 `
  --ligand-col 5
Quick check of your CSV header/delimiter:

Get-Content ".\fused\compounds_with_pdb_flat_selected_PPT_column.csv" -TotalCount 3
If you paste the first 2-3 lines here, I’ll give you the exact final command (correct delimiter + exact column numbers).


## Me:

The other up the limiter but if you insist in using the comma I have a file with, delivered wisdoma delimiter as it's this one command Also you have mixed up against the Col the ligand with the PDB columns you have mixed up so look at 4th column 3rd column Lincoln is in the 3rd column PDB is in the 4th column.
(.venv) PS C:\Users\geras\Partners HealthCare Dropbox\Evangelos Papadopoulos\MMSEGs Discussion\GeneDeepDives\Evangelos\PDB_Evangelos\FDA> python "H:\My Drive\VSCode_Github\scripts\Version_B\box_Proteins_03.py" 
>>   --csv ".\fused\compounds_with_pdb_flat_selected_PPT.csv" 
>>   --pdb-dir ".\fused\PDB_bioassembly" 
>>   --out-dir ".\fused\PDB_bioassembly\conf" 
>>   --has-header 
>>   --delimiter ","

GPT:
Correct, thanks for the correction:

ligand code = column 3
PDB code = column 4
Use this command with your comma-delimited file:

python "H:\My Drive\VSCode_Github\scripts\Version_B\box_Proteins_03.py" `
  --csv ".\fused\compounds_with_pdb_flat_selected_PPT.csv" `
  --pdb-dir ".\fused\PDB_bioassembly" `
  --out-dir ".\fused\PDB_bioassembly\conf" `
  --has-header `
  --delimiter "," `
  --ligand-col 3 `
  --pdb-col 4
If you want, I can also update the script defaults so it permanently uses ligand-col=3 and pdb-col=4.


## Me:
OK the generation of the conf files worked very well only I would like the receptor file to be of the format: 
'receptor = ./Target_PDBQT/1A4L.assembly1.delig.pdbqt'

GPT:
Perfect. Use the receptor template option so each .conf writes exactly that format:

python "H:\My Drive\VSCode_Github\scripts\Version_B\box_Proteins_03.py" `
  --csv ".\fused\compounds_with_pdb_flat_selected_PPT.csv" `
  --pdb-dir ".\fused\PDB_bioassembly" `
  --out-dir ".\fused\PDB_bioassembly\conf" `
  --has-header `
  --delimiter "," `
  --ligand-col 3 `
  --pdb-col 4 `
  --receptor-template "./Target_PDBQT/{pdb}.assembly1.delig.pdbqt"
That will produce lines like:

receptor = ./Target_PDBQT/1A4L.assembly1.delig.pdbqt

## Me:
I moved the protein 0 to A Please also edit so as to include author version you Date example you usad usage and MIT license and short and long help

I understand: you want box_Proteins_03.py cleaned up with proper metadata and documentation sections (author, version, date, usage examples, MIT license notice, and clearer short/long CLI help). I’ll open that file and apply those edits directly.

I hit a sandbox refresh error while reading the file; I’m retrying immediately and then I’ll patch the script once it loads.

I’m now adding a proper script header and CLI documentation: author/version/date/license metadata, --version, richer --help text with examples, and clearer option help strings.










