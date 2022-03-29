# GhostVault
Ghost coin cold staking node managment interface

Setup walkthrough:

This guide is for Ubuntu/Deabian based systems. Other systems to come.

To start with, any currenty running instances of ghostd will need to be stopped before continuing with this guide.

Now that there is no instance of ghostd running we can continue.
Now let's make sure your system is up to date by running:
```
sudo apt update && sudo apt upgrade -y
```
Next we need to make sure a few dependencies are satisfied:

```
sudo apt install python3-pip git
```

Clone the repository:

```
cd && git clone https://github.com/bleach86/GhostVault && cd GhostVault/
```

Install the python modules:

```
pip3 install -r requirements.txt
```

That concludes the system setup, and you are ready to run GhostVault for the first time and do the initial setup.

**NOTE** run `cd ~/GhostVault` if you get file not found in following steps. 

To start the GhostVault quickstat simply run:

```
python3 ghostVault.py quickstart
```

This will start the quickstart guide. It will start by downloading ghostd and syncing with the ghost network.
There will also be a check in this stage to make sure your node is on the correct chain. If it says bad chain detected,
do the resync to get back on the correct chain.

