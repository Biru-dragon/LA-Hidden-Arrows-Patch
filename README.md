### Tools used
[![MultiExtractor](https://img.shields.io/badge/MultiExtractor-Extraction-orange?style=flat-square&logo=appveyor&logoColor=white)](https://www.multi-extractor.com/)
[![HxD](https://img.shields.io/badge/HxD-Hex%20Editor-blue?style=flat-square&logo=codeforces&logoColor=white)](https://mh-nexus.de/en/hxd/)
[![Sysinternals Strings](https://img.shields.io/badge/Sysinternals-Strings-0078D7?style=flat-square&logo=microsoft&logoColor=white)](https://learn.microsoft.com/en-us/sysinternals/downloads/strings)
[![Notepad++](https://img.shields.io/badge/Notepad++-Text%20Editor-90E528?style=flat-square&logo=notepad%2B%2B&logoColor=black)](https://notepad-plus-plus.org/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-AI%20Assistant-D97706?style=flat-square&logo=anthropic&logoColor=white)](https://claude.ai/)

### Requirement
- [Python 3](https://www.python.org/downloads/)


## How to use it
To find the game executable, from Steam :
`LIBRARY > Logic Arrows Demo > Manage > Browse local files`

Place the `patch.py` file next to the game executable `Logic Arrows.exe`. 

Copy the path to the folder containing the executable and open the command prompt. (`cmd.exe`)

Close the game if it is open.

In the command prompt, enter the following commands : `cd <your copied path here>` and `python patch.py`

Open the game, go to `Settings` and then click on `Open Saves Folder`. Once done, replace the `player.json` file with the one located in the repository (remember to make a backup of your `player.json` file if you want to keep it).

## How to remove the patch
Go to the folder containing the game's executable, delete the files `Logic Arrows.exe` and `patch.py` then rename `Logic Arrows.original.exe` to `Logic Arrows.exe` and the patch will then be removed.

If you have kept a copy of your `player.json` file, you can place it into your save folder, replacing the existing one to recover your original progress.
