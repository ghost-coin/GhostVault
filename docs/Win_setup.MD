# GhostVault setup for Windows

The follow guide is for the setup of GhostVault for running natively on Windows.

The procedure for running GhostVault on Windows using WSL can be found [here](https://github.com/bleach86/GhostVault/blob/main/docs/WSL_setup.MD)


**1. Installing Python and Git**

Start by downloading Python from [here](https://www.python.org/ftp/python/3.10.4/python-3.10.4-amd64.exe).

Once downloaded, run the installer. Make sure that the box next to `Add Python 3.10 to PATH`, then click on install now.


![alt text](https://github.com/bleach86/GhostVault/blob/main/assets/python_install_win.PNG?raw=true)


Now download Git for Windows from [here](https://github.com/git-for-windows/git/releases/download/v2.35.2.windows.1/Git-2.35.2-64-bit.exe)

Once downloaded, run the installer. Click on the `Next` button until it becomes the `Install` button. Then click the `Install` button.



**2. Download GhostVault and install Python modules**

Open a cmd window but clicking on the start menu. Once the menu is up, type `cmd`, then click on `Command Prompt` to open a cmd window.

Enter the following command to download GhostVasult and to change into the new directory.

```
git clone https://github.com/ghost-coin/GhostVault && cd GhostVault
```

Now now to install the needed Python modules enter the following command

```
pip install -r requirements.txt
```

Now you are ready to continue on to the Universal Quickstart guide found in the main [readme](https://github.com/ghost-coin/GhostVault)
