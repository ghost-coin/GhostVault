# GhostVault setup guide for Windows using WSL


This guide is for setting up GhostVault on Windows using WSL. 
WSL, or Windows Subsystem for Linux is a built-in tool that allows you to run a full Linux environment as an app from within windows.

Running GhostVault using WSL has a few advantages. One being, running GhostVault with WSL allows your cold staking node to be sand-boxed on your system. This allows you to run your cold staking node at the
same time as your regular Windows desktop wallet.

This means that GhostVault will effectively run in the background while you can continue to use your computer as normal, including your normal wallet.

**1. Installing WSL**
This part can take a long time and requires rebooting the system.

To install WSL, first go to the start menu. Type in 'powershell'. 
There should be an option for an app called Windows PowerShell. Right click this and select 'Run as administrator`
Click `Yes` when prompted.

Once powershell is open type in `wsl --install` and press Enter.

This will begin the installation process. This can take a long time. Once this finishes, you need to reboot your computer.
Upon reboot, the WSL installation process will continue.

At the end of the installation process it will prompt you for a user name. Put the name you want for the user here. 
Then enter the password you wish the use twice. 

That's it. You are now in a fully running WSL environment. 

**2. Enabling WSL and cron on boot**

cron is a task scheduler for Unix systems. With WSL the cron service is not started on boot by default. In order to set this up so that we can 
ensure that your cold staking node is up and running at all times, we must issue a few commands both in the WSL environment and in Windows.

*************************************************
The following is to be done in the WLS environment
*************************************************

If your WSL environment is not open, go to the start menu and select Ubuntu on Windows.

Now right click the top bar of the window and select `Properties`
In the window that comes up, select the check box next to `Use Ctrl+Shift+C/V as Copy/Paste` then click the OK button.

Use `ctrl+shift+c` to copy from the command line and `ctrl+shift+v` to paste into it.

In the prompt, we need to make a startup script with

```
echo "service cron start" | sudo tee /usr/local/bin/cronstart.sh
```

Now lets make it executable

```
sudo chmod +x /usr/local/bin/cronstart.sh
```

Next we need to create a file within `/etc/sudoers.d/` with purpose to allow your `$USER` to execute cronstart.sh by sudo without password.
Run the following command to generate the line that must be placed in the sudoers file

```
echo "$USER ALL=(ALL) NOPASSWD: /usr/local/bin/cronstart.sh"
```

Copy the output of the command and temporarily store it in a notepad file for use in just a moment.

Now enter `sudo visudo -f /etc/sudoers.d/cronstart` to open the sudoers file for editing.

Now copy the output of the last command from the notepad file and paste it into the the command line window using `ctrl+shift+V`
Next press `ctrl+x` then type `y` then press Enter to save.

This is the end of the process from within the WSL environment.


******************************************************
The following is to be done in the Windows environment
******************************************************


Now, back in Windows we will setup the scheduled task that will activate WSL and cron at boot.

In the start menu, search for Task Scheduler. And as before with powershell, right click and select 'Run as administrator`.

First, click on `Task Scheduler Library` on the left hand side. 

![alt text](https://github.com/bleach86/GhostVault/blob/main/assets/taskschedulerlib.PNG?raw=true)

Then click on `Create Task…` on the right hand side.

![alt text](https://github.com/bleach86/GhostVault/blob/main/assets/createtask.PNG?raw=true)


This will open a tabbed window for making a new task. 

****************************************************
General Tab
****************************************************

On the general tab, start by giving your task a name. Any will do, like `WSL service cron start`.
Then select the choice that says `Run whether user is logged or not`
Then select `Do not store password` and `Run with highest privileges`
And finally in the `Configure for` dropdown, select the `Windows 10` option.

![alt text](https://github.com/bleach86/GhostVault/blob/main/assets/generaltab.PNG?raw=true)

****************************************************
Triggers Tab
****************************************************

On the Triggers tab, start by selecting `New...` near the bottom left. 
In the `Begin the task` dropdown, select ` At startup`

Under advanced setting select `Delay task for` and then select `1 Minute` from the dropdown

Now select 'OK' to go back to the main task creation window.


![alt text](https://github.com/bleach86/GhostVault/blob/main/assets/newtrigger.PNG?raw=true)

****************************************************
Actions Tab
****************************************************

On the Actions tab, start by selecting `New...` near the bottom left.
Choose `Start a program` from the Action dropdown.
Then enter `C:\Windows\System32\wsl.exe` in the textbox for Program/script.
Now in the box for `Add arguments (optional)` put in `sudo cronstart.sh`.

![alt text](https://github.com/bleach86/GhostVault/blob/main/assets/newaction.PNG?raw=true)

Now click `OK` then click `OK` on the task creation window.

Your task is now scheduled. 

**3. Reboot and test**

Now that our task is scheduled, reboot your computer. Once the computer is on the desktop again, wait for a full 2 minutes.

After 2 minutes has elapsed go to the start menu and select Ubuntu on Windows.

In the prompt enter `sudo service cron status`. If everything wend well, it should so `* cron is running`

You are now ready for the installation of GhostVault. Please proceed to the main [readme](https://github.com/bleach86/GhostVault#readme) after the row of `#`


