# GhostVault
Ghost coin cold staking node managment interface

Setup walkthrough:

For running GhostVault on Windows, you should start [here](https://github.com/bleach86/GhostVault/blob/main/docs/Win_setup.MD)

For running GhostVault on MacOS, you should start [here](https://github.com/bleach86/GhostVault/blob/main/docs/Mac_setup.MD)

The following is for Ubuntu/Debian based systems.

Sart with with this VPS setup guide [here](https://ghostveterans.com/vps/)

The first section 'VPS Provider & Setup' is for setting up a vps with the provider 'Vultr.com'
you can use this one, or any you like. Make sure the system is Ubuntu 20.04 and 2gb of ram.

The next part in that guide 'Connecting to your VPS' is for getting a ssh connection.

After that part secure your server using the guide found [here](https://github.com/bleach86/GhostVault/blob/main/docs/VPSsetup.MD)

Once your server is secured, return back here and continue with this guide.

#############################################################################################
To start with, any currently running instances of ghostd will need to be stopped before continuing with this guide.

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
cd && git clone https://github.com/ghost-coin/GhostVault && cd GhostVault/
```

Install the python modules:

```
pip3 install -r requirements.txt
```

That concludes the system setup, and you are ready to run GhostVault for the first time and do the initial setup.

**NOTE** In case of file not found error when running GhostVault commands

**NOTE** On Linux/MacOS/WSL, type the following `cd ~/GhostVault`

**NOTE** On Windows, close the current cmd window and open a new one, then type `cd GhostVault`

************************************************
GhostVault Universal Quickstart Guide
************************************************


To start the GhostVault quickstat simply run

For Linux/MacOS/WSL:

```
python3 ghostVault.py quickstart
```

For Windows:

```
python ghostVault.py quickstart
```


This will start the quickstart guide. It will start by downloading ghostd and syncing with the ghost network.
There will also be a check in this stage to make sure your node is on the correct chain. If it says bad chain detected,
do the resync to get back on the correct chain.

Once ghostd is running and synced with the network it will try to detect existing wallets. If none are found, it will give you the 
oportunity to type in the name of a wallet. 
To make a new wallet, leave this blank and in the next step you put in the name of the new wallet in.
If a wallet is detected, you will have the chance to make a new one anyway.

The next step is getting the Extended public Key for your wallet. This key is how you connect your wallet to the coldstaking node.

If making a new wallet, it will ask you to name the key, and a new one is generated for you. You need to copy this key as you will need it for
setting up coldstaking on your wallet.
If using an existing wallet, it will list all available keys from the wallet, letting you choose the one you want to use.
You can also choose to make a new one.

After you have your key chosen and recorded, the next step is setting up the reward address.

The reward address is where staking rewards are sent. You should have control over this wallet.
You can use either a standard or a stealth address for this.

For normal privacy mode use a standard address. In this mode, all staking rewards are paid directly to public address
In a public transaction. This will pay to the same address every time.

For Enhanced Privacy mode use a stealth address. In this mode all staking rewards are paid directly to your wallet on a public transaction,
just like in normal mode. But, the payments will be paid to freshly generated address derived from your stealth address. This will make it
extremely difficult for any prying eyes to associate any payments to you.

And the same as before, existing reward address is detected if using existing wallet, and there is the chance to change it. 

And that's it for the quickstart. Now you can start staking.

Full Anon mode.

Once the quickstart is finished, you can activate full Anon mode if you wish.

This can be done as followes:

For Linux/MacOS/WSL:

```
python3 ghostVault.py private
```

For Windows:

```
python ghostVault.py private
```


So first it will want you to type `private` to confirm that you want to activate anon mode.
The only thing you should have to do is put the address where you want your anonymized funds to go.

Like with the regular reward address, you can use either a standard or a stealth address.

If you use a stealth address, the stake rewards are paid to the internal wallet on the coldstaking node on a random address. Once the coins mature,
they will be sent to the stealth address via a public to anon transaction.

If you use a standard address, the stake rewards are paid to the internal wallet on the coldstaking node on a random address like before.
But, once they mature they will be sent from the internal public balance, to the internal anon balance. Then once they are mature again,
the anonymized coins are sent to the address of your choice in a anon to public transaction.

After that, you will be in full Anon mode! Congrats!

The addresses can be changed at any time, and the proper modes are automatically detected and activated.

Next step would be to use the extended public key to setup cold staking on your wallet.
You can follow the steps under `Connecting Ghost Wallet to your Cold staking VPS` found here https://ghostveterans.com/vps/


*********************************************
**COMMANDS**
*********************************************

**NOTE** In case of file not found error when running GhostVault commands

**NOTE** On Linux/MacOS/WSL, type the following `cd ~/GhostVault`

**NOTE** On Windows, close the current cmd window and open a new one, then type `cd GhostVault`

All commands are run as follows

For Linux/MacOS/WSL:

```
python3 ghostVault.py <command>
```

For Windows:

```
python ghostVault.py <command>
```



`quickstart` : This runs the quickstart guide. It should be run first.

`status`           : This returns the status and general health of the staking node.

`stats`            : This returns basic staking stats. 

`start`            : Starts ghostd

`stop`             : Stops ghostd

`restart`          : restarts ghostd

`rewardaddress`    : Show the reward address for normal and enhanced privacy modes.

`anonaddress`      : Shows the address where rewards are sent to in Anon mode.

`setrewardaddress` : Sets a new reward address. This will also disable Anon mode if Anon mode is active.

`setanonaddress`   : Sets a new address to receive anonymized stake rewards at.

`showextkey`       : Shows the extended public key used to connect cold staking.

`newextkey`        : Sets new extended public key.

`private`          : Checks Anon mode and is used to activate anon mode.

`update`           : Runs the self updater to update GhostVault and ghostd

`forceupdate`      : Downloads new ghostd even if update is not needed

`checkchian`       : Checks to ensure you are on a good chain.

`forceresync`      : Forces ghostd to resync with the network in case of a bad chain.

`balance`          : Shows the internal wallet balances

`cronpay`          : Used by cron to process payments for Anon mode.
