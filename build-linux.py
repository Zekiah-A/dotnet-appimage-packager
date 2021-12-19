#!/usr/bin/env python
#####################################################################################################
# <Build-linux - Automatically converts .net 5/6 avalonia projects to linux executable AppImages.>
# Copyright (C) 2021 zekiahepic
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#####################################################################################################

import os;
import io;
import time;
import urllib.request;
from shutil import copyfile as copy;
from shutil import copytree as copy_recursive;
from shutil import move;


class colours:
    NOCOLOUR='\033[0m'
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    ORANGE='\033[0;33m'
    BLUE='\033[0;34m'
    PURPLE='\033[0;35m'
    CYAN='\033[0;36m'
    LIGHTGRAY='\033[0;37m'
    DARKGRAY='\033[1;30m'
    LIGHTRED='\033[1;31m'
    LIGHTGREEN='\033[1;32m'
    YELLOW='\033[1;33m'
    LIGHTBLUE='\033[1;34m'
    LIGHTPURPLE='\033[1;35m'
    LIGHTCYAN='\033[1;36m'
    WHITE='\033[1;37m'

#General app configuration, will be set manually until TODO: automatic csproj detection is implemented.
appname = ""
appcategory = ""
appiconpath = ""

#IO paths.
path = ""
appdir_path = ""
appicon_name = ""
appicon_name_sanitised = ""

# ---------------------
# Configuration
# ---------------------
def query_appname():
    global appname
    appname = input(f"{colours.YELLOW}Enter project name (must be{colours.NOCOLOUR} {colours.RED}exact{colours.NOCOLOUR} {colours.YELLOW}casing):{colours.NOCOLOUR}\n=> ")

def category_help():
    print("Category Types: GNOME, GNOME-Classic, GNOME-Flashback, KDE, LXDE, LXQt, MATE, Razor, ROX, TDE, Unity, XFCE, EDE, Cinnamon, Pantheon, Old")
    query_category()

def query_category():
    temp_category = input(f"{colours.YELLOW}Enter application category, type{colours.NOCOLOUR} {colours.RED}'help'{colours.NOCOLOUR} {colours.YELLOW}to see all available categories:{colours.NOCOLOUR}\n=> ")
    if (temp_category == "help"):
        category_help()
    else:
        global appcategory
        appcategory = temp_category

def query_appiconpath():
    global appiconpath
    global appicon_name
    global appicon_name_sanitised
    appiconpath = input(f"{colours.YELLOW}Enter path to app icon (from the project head direcory):{colours.NOCOLOUR}\n=> ")
    appicon_path_array = appiconpath.split('/')
    appicon_name = appicon_path_array[len(appicon_path_array) - 1]
    appicon_name_sanitised = appicon_name.split('.')[0]

query_appname()
query_category()
query_appiconpath()

# ---------------------
# Build
# ---------------------
time.sleep(0.5) #Give the user time to read the logs
print(f"=> {colours.GREEN}Building the dotnet self contained executable.{colours.NOCOLOUR}")

#Build the dotnet package as a self contained pacckage (with unused library cleanup to reduce filesize), so that no dotnet runtime is needed.
os.system("dotnet publish -c Release -r linux-x64 -p:PublishTrimmed=true")

print(f"=> Build sucess! {colours.GREEN}Creating AppImage app dir.{colours.NOCOLOUR}")

#Make AppImage directory structure.
if (os.path.exists(os.path.join(os.getcwd(), 'bin', 'Release', 'net6.0', 'linux-x64'))):
    path = os.path.join(os.getcwd(), 'bin', 'Release', 'net6.0')
elif (os.path.exists(os.path.join(os.getcwd(), 'bin', 'Release', 'net5.0', 'linux-x64'))):
    path = os.path.join(os.getcwd(), 'bin', 'Release', 'net6.0')
print(f"{colours.NOCOLOUR}{path},")

try:
    appdir_path = f"{path}/{appname}-x86_64.AppDir" #TODO: Make this project name (instead of MyApp)
    os.makedirs(os.path.join(f"{appdir_path}/usr/bin"), exist_ok=True)#TODO: Fix where i am using os.path.join wrongly
    os.makedirs(os.path.join(f"{appdir_path}/usr/lib"), exist_ok=True)
    print(f"{colours.NOCOLOUR}{appdir_path},\n{appdir_path}/usr/bin,\n{appdir_path}/usr/lib\n=>{colours.GREEN} Sucessfully made directories.{colours.NOCOLOUR}")
except OSError as error:
    print(f"=>{colours().RED} Could not make AppImage app directories.\n{error}{colours.NOCOLOUR}")

print(f"=> Populating AppDir files.{colours.NOCOLOUR}")

try:
    #Generate .desktop file.
    file = open(f"{appdir_path}/myapp.desktop","w+")
    file.write(f"[Desktop Entry]\nName={appname}-x86_64\nExec=myapp\nIcon={appicon_name_sanitised}\nType=Application\nCategories={appcategory};") #TODO: ADD back categories
    file.close
    print(f"{colours.NOCOLOUR}{appdir_path}/myapp.desktop")

    #Generate AppRun start script.
    file = open(f"{appdir_path}/AppRun","w+")
    file.write(f"#!/bin/bash\nchmod +x usr/bin/{appname}\nusr/bin/{appname}") #TODO: Use precompiled one instead?
    file.close
    print(f"{colours.NOCOLOUR}{appdir_path}/AppRun")

    #Move app icon (if exists) into the AppDir.
    copy(appiconpath, f"{appdir_path}/{appicon_name}")
    print(f"{colours.NOCOLOUR}{appdir_path}/{appicon_name}")
except OSError as error:
    print(f"=>{colours().RED} Could not populate AppDir directories.\n{error}{colours.NOCOLOUR}")

print(f"=>{colours.GREEN} Sucessfully populated AppDir files.{colours.NOCOLOUR} Copying executables & libraries to AppDir{colours.NOCOLOUR}.")

#Copy libraries and executables to the AppDir.
try: #TODO: implement status bar
    copy_recursive(os.path.join(path, "linux-x64"), os.path.join(appdir_path, 'usr', 'bin'), symlinks=False, ignore=None, copy_function=copy, ignore_dangling_symlinks=False, dirs_exist_ok=True)
    for r, d, f in os.walk(os.path.join(path, "linux-x64")):
        for file in f:
            print(os.path.join(r, file))
            time.sleep(0.005) #Just makes it look cooler lol
        for directory in f:
            print(os.path.join(r, directory))
            time.sleep(0.005) #Just makes it look cooler lol
except OSError as error:
    print(f"=>{colours().RED} Could not copy libraries and executables to the AppDir.\n{error}{colours.NOCOLOUR}")

#Use AppImageTool to build the AppImageDir into an AppImage
try:
    skip = input(f"=>{colours.YELLOW} This part is experimental, and will only run on linux/wsl systems. Enter {colours.NOCOLOUR}{colours.RED}[Y/n]{colours.YELLOW} to skip or continue the AppDir to AppImage build process.{colours.NOCOLOUR}\n=> ")
    if (str.lower(skip) == "n"):
        exit()
    else:
        #To fix execv error. Done now as this is the mo-cross platform section
        os.system(f"chmod +x {appdir_path}/AppRun")
        url = 'https://github.com/AppImage/AppImageKit/releases/download/13/appimagetool-x86_64.AppImage'
        urllib.request.urlretrieve(url, os.path.join(path, 'appimagetool-x86_64.AppImage'))
        os.system(f"chmod +x {path}/appimagetool-x86_64.AppImage")
        os.system(f"ARCH=x86_64 {path}/appimagetool-x86_64.AppImage {appdir_path}")
        print(f"=> {colours.GREEN}Sucessfully built AppImage,{colours.NOCOLOUR} can be found in root project directory, with name {appname}-x86_64.AppImage.{colours.NOCOLOUR}")
except Exception() as error:
    print(f"=>{colours().RED} Could not use AppImageTool to build the AppDir into an AppImage.\n{error}{colours.NOCOLOUR}")

# Potential future more customisable copy system:
# r=root, d=directories, f = files
#for r, d, f in os.walk(os.path.join(path, "linux-x64")):
#    for file in f:
#        print(os.path.join(r, file))
#        copy(os.path.join(r, file), os.path.join(appdir_path, 'usr', 'bin', file))
#    for directory in d:
#        print(os.path.join(r, directory))
#        copy(os.path.join(r, directory), os.path.join(appdir_path, 'usr', 'bin', directory)) #TODO: This is a hacky mess, use recursion!

#TODO: Strip ALL file extensions from icon name, from the icons, becaus it makes the appimagetool go WAH WAH
