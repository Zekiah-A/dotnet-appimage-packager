# dotnet-appimage-packager
Tool to automatically build and package a .net 5/6 project to the portable .AppImage format, for distribution on Linux.


**Caution: In very early stages of development, expect many bugs and issues.**

### Running the tool.
Simply put the *build-linux.py* script in the root (main) folder of your dotnet project, and then run the script from the command line, by doing:
- `python build-linux.py` in Command Prompt, or Powershell on Windows.
- `python3 build-linux.py` in the Terminal on Ubuntu based distrobutions.
- `python build-linux.py` in the Terminal on macos and other distrobutions.

### How it works:
The tool first runs the necessary commands to create an AppDir from your dotnet project, from the [official documentation](https://docs.appimage.org/packaging-guide/manual.html), and then makes use of [AppImageTool](https://appimage.github.io/appimagetool/), to convert the AppDir into a .AppImage package.

### Important note:
While generating the AppDir directories and project files is possible on windows or macos with this tool, the AppDir to .AppImage packager is only supported on **WSL/Linux** systems for the time being.
