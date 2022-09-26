#! /bin/bash
sudo apt update && sudo apt upgrade -y && sudo apt install python3-uvloop

cd ~/GhostVault && python3 ghostVault.py enableelectrumx

wget https://raw.githubusercontent.com/bleach86/electrumx-installer/master/bootstrap.sh -O - | bash

sudo ufw allow 50002
