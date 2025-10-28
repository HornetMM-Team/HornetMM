# A Cross Platform Mod Manager For Hollow Knight/Silksong Made in Py
<b> You dont need any sort of python in order to run this if your using releases tab/actions. Recommended to run with source </b>


<h2>Demo:</h2>
- <img width="702" height="858" alt="image" src="https://github.com/user-attachments/assets/d8d18a46-366d-4152-8705-5a1545bdecb4" />

(I used windows for this demo)


>[!TIP]
>Btw. since this uses customtkinter, if you find a cool theme, in the source place a theme .json inside of the themes folder, then add this to somewhere in the base.py, or other menus that you want to look like that ```customtkinter.set_default_color_theme("themes/<my_custom_theme>.json")``` replace "my_custom_theme" with the attual name of your json




Goals In Project:
- [x] Add BepinEx/Hollow Knight Modding Api Support For Hollow knight
- [ ] Add Thunderstore support for Silksong
- [x] Add 1-click support
- [ ] Add To flatpak for Steam Deck
- [ ] Add Proper MonoMod detection
- [x] Make settings.json work
- [ ] Add A optional cheat menu


Features:
- GameBanana 1-Click
- Installing BepInEx
- Mod Management
- Settings
- System Theme Support

<h3>Installation (Source; Windows, Difficulty: Easy):</h3>
- To install make sure you have <b>GIT</b> installed as it will be required in order to install all the source code, by default it installs "cloned" code inside of %userprofile% or your user folder.
- for linux ppl it might be in home,
- to install git (for windows) you will need to A: run ```setx %WINGET% C:\<yourusername>\AppData\Local\Microsoft\WindowsApps\winget.exe``` (do this if typing winget gives error) restart your terminal and run ```winget install git.git```,
- or B: go to (git's website)[git-scm.com] and download git. if your downloading GIT from the website.
- you will need to restart your computer to apply the PATH variables.
- Both Methods Do <font color="red">NOT</font> require admin.
- Make sure to run git --version to make sure its installed correctly.
- if you havent restarted yet and the command isnt reconized then restart,
- for the new value in PATH to take effect, now run ```git clone https://https://github.com/Sonic3Modder/HornetMM.git```
- this will copy all of the source code into a folder called "HornetMM".
- now we have to install python.
- I devoloped this with python 3.13.7 so I do recommend installing that version, or the latest,
- to install run ```winget install python```(if you did the instructions, or if it just works) or install python from the (website)[https://github.com/Sonic3Modder/HornetMM/edit/main/README.md].
- Now you want to go inside of the folder you cloned, inside of the root (base folder) of your user directory/folder in cmd/powershell, now type ```pip install -r requirements.txt``` this will install the requirements,
- after thats done run ```python base.py``` this will run the base. Now you have it working yay :D

<h3>Installation (Source; Linux, Difficulty: Medium):</h3>

> [!WARNING]  
> SteamOS is ment for system stability making it hard to install AUR packages, Highly reccomended that you install the flatpak, And even if you do, SteamOS wipes everything in rootfs on system update. YOU HAVE BEEN WARNED‼️‼️

To install you will need <b>Git</b> to do this you can run:

- Ubuntu/Debain/ZorinOS: ```sudo apt install git```
- Fedora/Nobara: ```sudo dnf install git```
- Arch/SteamOS/Manjaro: ```sudo pacman -S git``` (Make sure you run ```sudo pacman -Syu``` Before)
- Gentoo: ```emerge --ask --verbose dev-vcs/git```

Make sure that git is installed correctly by running ```git --version```. Now that git is working, we need **Python**, you can install python by running:

- Ubuntu/Debain/ZorinOS: ```sudo apt install python```
- Fedora/Nobara: ```sudo dnf install python```
- Arch/SteamOS/Manjaro: ```sudo pacman -S python``` (Make sure you run ```sudo pacman -Syu``` Before)
- Gentoo: ```emerge --ask dev-lang/python:3.13```

Now that we have **Python**, And **Git**, Now we can Start the installation Process, firstly run ```git clone https://github.com/Sonic3Modder/HornetMM.git``` this will copy all of the source files into a folder inside of your user directory (/home/<yourusername>)
now type ```cd HornetMM``` and run ```pip install -r install requirements.txt``` wait for the requirements to download. then run ```python base.py```. Now you have HornetMM working on linux.

<h3>Building(Linux; Difficulty: Medium):</h3>
🚧 W.I.P 🚧

>[!NOTE]
> I dont know when Ill make it work

<h3>Building(Windows; Difficulty: Easy)</h3>
🚧 W.I.P 🚧

>[!NOTE]
> I dont know when Ill make it work
‎ 
‎ 
‎ 









