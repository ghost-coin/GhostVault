#!/usr/bin/env python3

import urllib.request
from urllib.request import urlopen
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import requests, os, sys, json, pprint, shutil, platform, subprocess, textwrap, time, os.path, git, psutil
import hashlib
from datetime import datetime, timedelta
from colorama import Fore, Back, Style
from colorama import init
from crontab import CronTab
init()

RPCUSER = 'user'
RPCPASSWORD = 'password'
RPCPORT = 51725

version = "v1.3.1"

system = platform.system()

def rpcproxy():
    rpcproxy = AuthServiceProxy('http://%s:%s@127.0.0.1:%d/' % (RPCUSER, RPCPASSWORD, RPCPORT), timeout=120)
    return rpcproxy

def checkConnect():
    try:
        rpcproxy().getblockchaininfo()
        return True
    except:
        return False

def checkWalletLoad():
    try:
        rpcproxy().getstakinginfo()
        return True
    except:
        return False

def daemonInfo():
    with open('daemon.json') as f:
        data = json.loads(f.read())
    return data
    
def getExplorerHeight():
    url = f"https://explorer.myghost.org/api/getblockcount"
    response = urlopen(url)
    data = json.loads(response.read())
    return data

def getExplorerBlockHash(index):
    url = f"https://explorer.myghost.org/api/getblockhash?index={index}"
    response = urlopen(url)
    data = json.loads(response.read())
    return data

def getPeerCount():
    peerCount = rpcproxy().getconnectioncount()
    return peerCount

def getBlockHeight():
    blocks = rpcproxy().getblockcount()
    return blocks

def getBlockChainInfo():
    blockChainInfo = rpcproxy().getblockchaininfo()
    return blockChainInfo

def importKey(words):
    print("Building wallet from mnemonic words.")
    try:
        rpcproxy().extkeyimportmaster(words, "", False, "", "", -1)
    except Exception as e:
        showError(e)
    print('Sucessfully imported mnemonic.')

def getNewExtAddr(label):
    extAddr = rpcproxy().getnewextaddress(label)
    return extAddr
    
def getNewStealthAddr():
    addr = rpcproxy().getnewstealthaddress()
    return addr

def validateAddress(address):
    addr = rpcproxy().validateaddress(address)
    
    if addr['isvalid'] == True:
        return True
    else:
        return False

def getColdStakingInfo():
    if checkWalletLoad() == False:
        showError(f"No wallet loaded!")
    
    csInfo = rpcproxy().getcoldstakinginfo()
    return csInfo

def getStakingInfo():
    if checkWalletLoad() == False:
        showError(f"No wallet loaded!")
    
    sInfo = rpcproxy().getstakinginfo()
    return sInfo

def getUptime():
    uptime = rpcproxy().uptime()
    return uptime

def getNetworkInfo():
    network = rpcproxy().getnetworkinfo()
    return network

def getBalances():
    return rpcproxy().getbalances()

def getKeysAvailable():
    keys = []
    
    allKeys = rpcproxy().extkey("account")
    
    for i in allKeys['chains']:
        keyDict = {"key": "", "label": ""}
        if 'function' in i or 'use_type' in i or i['receive_on'] == False or i['label'] == '': 
            continue
        
        keyDict['key'] = i['chain']
        keyDict['label'] = i['label']
        keys.append(keyDict)
    return keys

def setRewardAddress(rewardAddress, anon=False):
    if validateAddress(rewardAddress) == False:
        showError(f"Invalid Ghost address: {rewardAddress}")
    
    if anon == True:
        print(f"Setting reward address to: {Fore.CYAN}<Internal Stealth Address>{Style.RESET_ALL}...")
    
    else:
        print(f"Setting reward address to: {Fore.CYAN}{rewardAddress}{Style.RESET_ALL}...")
    
    try:
        rpcproxy().walletsettings("stakingoptions", {"rewardaddress": rewardAddress})
    except Exception as e:
        showError(e)
    dInfo = daemonInfo()
    dInfo['rewardAddress'] = rewardAddress
    updateDaemonInfo(dInfo)
    print(f"Reward address successfully updated.")

def setAnonAddress(rewardAddress):
    if validateAddress(rewardAddress) == False:
        showError(f"Invalid Ghost address: {rewardAddress}")
        
    print(f"Setting anon reward address to: {Fore.CYAN}{rewardAddress}{Style.RESET_ALL}...")

    dInfo = daemonInfo()
    dInfo['anonRewardAddress'] = rewardAddress
    updateDaemonInfo(dInfo)
    print(f"Anon reward address successfully updated.")

def getRewardAddressFromWallet():
    walletInfo = rpcproxy().walletsettings("stakingoptions")
    
    if walletInfo['stakingoptions'] == 'default':
        return None
    elif 'rewardaddress' in walletInfo['stakingoptions']:
        return walletInfo['stakingoptions']['rewardaddress']
    else:
        return None
        
def mnemonic():
    words = rpcproxy().mnemonic("new", "", "english")['mnemonic']
    return words

def getWallets():
    wallets = rpcproxy().listwallets()
    return wallets

def getWalletInfo():
    walletInfo = rpcproxy().getwalletinfo()
    return walletInfo

def createWallet(walletName):
    rpcproxy().createwallet(walletName)

def loadWallet(walletName):
    if checkWalletLoad() == True:
        wallet = rpcproxy().getwalletinfo()['walletname']
        if wallet == walletName:
            print(f"Wallet {walletName} already loaded.")
            return
        else:
            rpcproxy().loadwallet(walletName)
            return
    rpcproxy().loadwallet(walletName)

def isBadFork():
    bcInfo = getBlockChainInfo()
    block = bcInfo['blocks']
    bestBlockHash = bcInfo['bestblockhash']
    
    if bestBlockHash == getExplorerBlockHash(block):
        return False
    else:
        return True

def getSystem():
    arch = platform.uname()[-2]

    if arch == 'armv7l':
        arch = 'arm'
    elif arch == 'aarch64':
        arch = 'aarch64'
    elif arch == 'x86_64' or arch == 'AMD64':
        arch = 'x86_64'
    
    if system == 'Darwin':
        systemOS = 'MacOS'
        arch = 'x86_64'
        return f'{arch}-{systemOS}'
    
    return f'{arch}-{system}'

def syncProgress():
    while True:
        bcInfo = getBlockChainInfo()
        blocks = bcInfo['blocks']
        headers = bcInfo['headers']
        initialDl = bcInfo['initialblockdownload']
        
        if headers == 0 or getPeerCount() == 0:
            continue
        
        progress = blocks / headers * 100
        
        clear()
        print(f"Ghostd is currently syncing with the Ghost network.")
        print(f"Progress: {blocks:,}/{headers:,} {Fore.GREEN}{round(progress, 3)}%{Style.RESET_ALL}")
        
        if initialDl == False or progress == 100:
            time.sleep(1)
            break
        time.sleep(1)

def isSyncing():
    bcInfo = getBlockChainInfo()
    blocks = bcInfo['blocks']
    headers = bcInfo['headers']
    initialDl = bcInfo['initialblockdownload']
    
    if initialDl == True or blocks != headers:
        return True
    else:
        return False

def convertFromSat(value):
    sat_readable = value / 10**8
    return sat_readable
    
def convertToSat(value):
    sat_readable = value * 10**8
    return sat_readable

def clear():
    if system == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def showError(err):
    print(f"GhostVualt has encountered an error.\nERROR:{Fore.RED}{err}{Style.RESET_ALL}")
    sys.exit()

def getLink():
    with open("links.json") as f:
        links = json.loads(f.read())
    
    return links[getSystem()]['link']

def downloadFromUrl(url, path):
    clear()
    with open(path, "wb") as f:
        print("Downloading %s" % path)
        response = requests.get(url, stream=True)
        total_length = response.headers.get('content-length')
    
        if total_length is None: # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write(f"{Fore.GREEN}\r[%s%s]{Style.RESET_ALL}" % ('=' * done, ' ' * (50-done)) )    
                sys.stdout.flush()
    clear()

def downloadDaemon():
    url = getLink()
    archive = getLink().split("/")[-1]
    
    if os.path.isfile(archive) == True:
        if isValidArchiveHash(archive) == False:
            os.remove(archive)
            downloadFromUrl(url, archive)
        else:
            print(f'Valid archive file found, skipping download.')
            return
    else:
        downloadFromUrl(url, archive)

def extractDaemon():
    removeDaemon()
    archive = getLink().split("/")[-1]

    if os.path.isfile(archive) == False:
        showError(f"File {archive} not found.")
    
    elif isValidArchiveHash(archive) == False:
        showError("SHA256 hash of archive invalid. Download may be corrupted. Please retry download.")
    
    if os.path.isfile(daemonInfo()['ghostdPath']):
        print("Removing existing ghostd in favor of new one.")
        removeDaemon()
    
    if archive.endswith(".tar.gz"):
        archiveFormat = 'gztar'
    elif archive.endswith(".tar.xz"):
        archiveFormat = 'xztar'
    elif archive.endswith(".zip"):
        archiveFormat = 'zip'
    
    print("Extracting Ghostd from archive...")
    
    try:
        shutil.unpack_archive(archive, os.getcwd(), archiveFormat)
    except Exception as e:
        showError(e)
        #time.sleep(5)
        #shutil.unpack_archive(archive, os.getcwd(), archiveFormat)
    for dirpath, dirnames, filenames in os.walk("."):
        if system == "Windows":
            for filename in [f for f in filenames if f == "ghostd.exe"]:
                daemonPath = os.path.join(dirpath, filename)
        else:
            for filename in [f for f in filenames if f == "ghostd"]:
                daemonPath = os.path.join(dirpath, filename)
    dInfo = daemonInfo()
    dInfo['ghostdPath'] = daemonPath
    dInfo['ghostdHash'] = getDaemonHash(daemonPath)
    dInfo['archive'] = archive
    updateDaemonInfo(dInfo)
    print("Daemon Extraction success!")

def getDaemonHash(daemonPath):
    return getHash(daemonPath)

def isValidArchiveHash(archive):
    readable_hash = getHash(archive)
    with open("links.json") as f:
        links = json.loads(f.read())
    
    if links[getSystem()]['hash'] == readable_hash:
        return True
    else:
        return False

def isValidDaemonHash():
    storeHash = daemonInfo()['ghostdHash']
    
    readable_hash = getHash(daemonInfo()['ghostdPath'])
    
    if storeHash == readable_hash:
        return True
    else:
        return False

def isStealthAddr(addr):
    if validateAddress(addr) == True and addr.startswith("SP") == True:
        return True
    else:
        return False

def getHash(path):
    with open(path,"rb") as f:
        bytes = f.read()
        readable_hash = hashlib.sha256(bytes).hexdigest();
    return readable_hash

def prepareDataDir():
    if system == 'Linux':
        datadir = os.path.expanduser('~/.ghost/')
    elif system == 'Darwin':
        datadir = os.path.expanduser('~/Library/Application Support/Ghost/')
    elif system == 'Windows':
        datadir = os.path.expanduser('~/AppData/Roaming/Ghost/')
    
    if os.path.isdir(datadir):
        print('Data directory found...')
        print('Copying configuration file to data directory...')
        shutil.copy('templates/ghost.conf', datadir)
    else:
        print("Data directory not found, creating...")
        os.mkdir(datadir)
        print('Copying configuration file to data directory...')
        shutil.copy('templates/ghost.conf', datadir)

def clearBlocks():
    if system == 'Linux':
        datadir = os.path.expanduser('~/.ghost')
    elif system == 'Darwin':
        datadir = os.path.expanduser('~/Library/Application Support/Ghost')
    elif system == 'Windows':
        datadir = os.path.expanduser('~/AppData/Roaming/Ghost')
    
    rmdir = ['blocks', 'chainstate']
    print("Clearing blocks...")
    for i in rmdir:
        shutil.rmtree(f'{datadir}/{i}/')
    os.remove(f'{datadir}/peers.dat')
    os.remove(f'{datadir}/banlist.dat')
    print('Blocks successfully cleared.')

def createBatchFiles():
    print('Preparing batch files...')
        
    batchFiles = [('vaultStart.bat', 'start'), ('vaultUpdate.bat', 'update'), ('vaultPay.bat', 'cronpay')]
    
    for i in batchFiles:
        if os.path.isfile(f'{i[0]}'):
            print(f"Batch file '{i[0]}' found. Skipping")
        else:
            print(f"Creating batch file '{i[0]}'...")
            
            with open(f"{i[0]}", "w") as f:
                f.write(f'@echo off\npowershell -window hidden -command "cd {os.path.expanduser("~")}\\GhostVault\\ ; {shutil.which("python")} ghostVault.py {i[1]}\nexit"')
            print("Success!")

def updateDaemonInfo(dInfo):
    with open('daemon.json', 'r+') as f:
        f.seek(0)
        json.dump(dInfo, f, indent = 4)
        f.truncate()

def startDaemon():
    if os.path.isfile(daemonInfo()['ghostdPath']) == False:
        showError(f"ghostd not found! run GhostVault with 'forceupdate' or 'quickstart' argument to install daemon.")
    
    elif getDaemonHash(daemonInfo()['ghostdPath']) != daemonInfo()['ghostdHash']:
        showError(f"Daemon hash not as expected! Daemon may be courupted.\nPlease run 'ghostVault.py forceupdate' to rectify.")
    
    elif checkConnect() == True:
        print("Daemon already running...")
    else:
        if system == "Windows":
            print("Ghost Core starting")
            subprocess.Popen(f"start cmd /C {daemonInfo()['ghostdPath']}", shell=True)
        else:
            subprocess.call([f"{daemonInfo()['ghostdPath']}", "-daemon"])
        waitForDaemon()
        try:
            loadWallet(daemonInfo()['walletName'])
        except:
            pass
    
def stopDaemon():
    if checkConnect() == False:
        print("Daemon not running...")
    else:
        print(rpcproxy().stop())

def restartDaemon():
    print('Restarting daemon...')
    stopDaemon()
    waitForDaemonShutdown()
    startDaemon()

def removeDaemon():
    if daemonInfo()['ghostdPath'] == "":
        return
    elif os.path.isfile(daemonInfo()['ghostdPath']) == False:
        return
    if system == 'Windows':
        daemonDir = daemonInfo()['ghostdPath'].split('\\')[1]
    else:
        daemonDir = f"{daemonInfo()['ghostdPath'].split('/')[1]}/"
    
    stopDaemon()
    print('Removing deamon directory.')
    shutil.rmtree(daemonDir)
    dInfo = daemonInfo()
    dInfo['ghostdPath'] = ""
    dInfo['ghostdHash'] = ""
    updateDaemonInfo(dInfo)

def removeArchive():
    archive = getLink().split("/")[-1]
    
    if os.path.isfile(archive):
        print(f'Removing archive file {archive}...')
        os.remove(archive)
    else:
        print('Archive file not found.')
    dInfo = daemonInfo()
    dInfo['archive'] = ""
    updateDaemonInfo(dInfo)

def getStats(duration="all", days=None):
    tnow = time.time()
    day = 86400
    
    if checkWalletLoad() == False:
        try:
            loadWallet(daemonInfo()['walletName'])
        except:
            showError(f"Now wallet loaded!")
    
    if duration == 'all' and days == None:
        last24 = tnow - day
        last7d = tnow - day *7
        last30d = tnow - day *30
        last180d = tnow - day *180
        last365d = tnow - day *365
        durations = [("24h", last24), ("7 Days", last7d), ("30 Days", last30d), ("180 Days", last180d), ("Year", last365d)]
        clear()
        
        print(f"GhostVault {version} Staking Stats Page\n")
        
        print(f"{Fore.BLUE}DURATION        STAKES FOUND        AMOUNT EARNED{Style.RESET_ALL}")
        
        for i in durations:
            filter = rpcproxy().filtertransactions({"from":int(i[1]), "to":int(tnow),"count":100000,"category":"stake","collate":True,"include_watchonly":True,"with_reward":True})

            print(f"Last {i[0]:<9}        {Fore.GREEN}{filter['collated']['records']}                 {filter['collated']['total_reward']}{Style.RESET_ALL}")
            
        oneStake = rpcproxy().filtertransactions({"count":1,"category":"stake","include_watchonly":True})
        
        timeToFind = getStakingInfo()['expectedtime']
        
        if timeToFind == 0:
            timeToFind = 1
        
        if len(oneStake) != 0:
            etime = tnow - int(oneStake[0]['time'])
            nextReward = timeToFind - etime
        else:
            etime = 1
            nextReward = 0
            
        percentToReward = etime / timeToFind * 100
        ghostPerDay = day / timeToFind
        
        print("\n")
        print(f"Network stake weight   : {convertFromSat(int(getStakingInfo()['netstakeweight'])):,}")
        print(f"Current stake weight   : {getColdStakingInfo()['currently_staking']:,} | {round(float(getColdStakingInfo()['currently_staking']) / convertFromSat(int(getStakingInfo()['netstakeweight']))*100, 2)}%")
        
        if timeToFind == 1:
            pass
        else:
            print(f"EST Time to find       : {str(timedelta(seconds=timeToFind)).split('.')[0]}")
        
        if nextReward == 0:
            pass
        else:
            if nextReward < 0:
                print(f"EST Time to next reward: -{str(timedelta(seconds=nextReward*-1)).split('.')[0]} | {round(percentToReward, 2)}%")
            else:
                print(f"EST Time to next reward: {str(timedelta(seconds=nextReward)).split('.')[0]} | {round(percentToReward, 2)}%")
        print(f"EST Stakes per day     : {round(ghostPerDay, 2)}")
        print(f"EST Ghost per day      : {round(ghostPerDay*3.876, 8):,}")

def quickstart():
    newWallet = True
    clear()
    print(f"Welcome to GhostVault quickstart guide.")
    print(f"This is an automated guide that will assist you in setting up your coldstakig node.")
    print(f"This guide will also try to detect existing wallets and settings.")
    print(f"To start with, we will download the daemon and get synced with the Ghost network.")
    input("Press Enter to continue...")
    
    stopDaemon()
    waitForDaemonShutdown()
    downloadDaemon()
    extractDaemon()
    prepareDataDir()
    startDaemon()
    try:
        loadWallet(daemonInfo()['walletName'])
    except:
        pass
    
    if isSyncing() == True:
        syncProgress()
    
    if isBadFork() == True:
        print(f"ERROR: {Fore.RED}Bad Fork detected!{Style.RESET_ALL}")
        
        while True:
            ans = input(f"Would you like to resync to the correct chain? {Fore.GREEN}Y/{Fore.RED}n{Style.RESET_ALL} ")
            
            if ans.lower() == 'y' or ans.lower() == '':
                print("Forcing resync...")
                stopDaemon()
                waitForDaemonShutdown()
                clearBlocks()
                startDaemon()
                if isSyncing() == True:
                    syncProgress()
                    
                if isBadFork() == True:
                    showError(f"Bad fork still detected. Re-run GhostVault with 'forcerescan'")
                break
                
            elif ans.lower() == 'n':
                print(f"{Fore.RED}Exiting!{Style.RESET_ALL}")
                sys.exit()
            else:
                print("Invalid answer! Please enter either 'y' or 'n'")
                input("Press Enter to continue...")
                
    clear()
    
    if len(getWallets()) == 0:
        print(f"No existing wallets detected.")
        print(f"Sometimes GhostVault will not find a wallet that is existing.\nYou can enter the wallet name and GhostVault will try to load it.\n")
        
        walletName = input(f"Please enter a wallet name or leave blank to make new: ")
        
        if walletName != "":
            print(f"Attempting to load wallet: {walletName}")
            
            try:
                rpcproxy().loadwallet(walletName)
            except:
                showError(f"Failed to load wallet '{walletName}'. Please ensure the wallet exists and is spelled correctly.")
                
            print(f"Successfully loaded wallet {walletName}")
            
            dInfo = daemonInfo()
            dInfo['walletName'] = walletName
            updateDaemonInfo(dInfo)
            
            newWallet = False
            
        else:
            print("Making new wallet...")
            makeWallet()
        
    else:
        clear()
        print("Existing wallets detected!")
        
        while True:
            ans = input(f"Would you like to use one of these? No to make new: {Fore.GREEN}Y/{Fore.RED}n{Style.RESET_ALL} ")
            
            if ans.lower() == 'y' or ans.lower() == '':
                
                count = 1
                clear()
                
                for i in getWallets():
                    if i == "":
                        i = '[default wallet]'
                    print(f"{count}. {i}")
                    count += 1
                
                while True:
                    walletIndex = input(f"Please enter the number of the wallet you want to use: ")
                    
                    if walletIndex.isdigit() == False:
                        print(f"{Fore.RED}Invalid answer. Answer must be a number matching a wallet.{Style.RESET_ALL}")
                        
                    elif int(walletIndex) > len(getWallets()):
                        print(f"{Fore.RED}Invalid answer. Answer must be a number matching a wallet.{Style.RESET_ALL}")
                    else:
                        walletName = getWallets()[int(walletIndex)-1]
                        break
                
                dInfo = daemonInfo()
                dInfo['walletName'] = walletName
                updateDaemonInfo(dInfo)
                try:
                    loadWallet(walletName)
                except Exception as e:
                    pass
                newWallet = False
                break
                    
            elif ans.lower() == 'n':
                makeWallet()
                break
            else:
                print("Invalid answer! Please enter either 'y' or 'n'")
            
    if newWallet == False and len(getKeysAvailable()) > 0:
        keys = getKeysAvailable()
        
        print(f"Extended public keys detected.")
        
        while True:
            ans = input(f"Would you like to use an existing key? No to make new: {Fore.GREEN}Y/{Fore.RED}n{Style.RESET_ALL} ")
            
            if ans.lower() == 'y' or ans.lower() == '':
                count = 1
                clear()
                
                for i in keys:
                    print(f"{count}. ExtPubKey: {i['key'][0:24]} Label: {i['label']}")
                    count += 1
                    
                while True:
                    
                    keyIndex = input(f"Please enter the number of the ExtPubKey you want to use: ")
                    
                    if keyIndex.isdigit() == False:
                        print(f"{Fore.RED}Invalid answer. Answer must be a number matching a key.{Style.RESET_ALL}")
                        
                    elif int(keyIndex) > len(getWallets()):
                        print(f"{Fore.RED}Invalid answer. Answer must be a number matching a key.{Style.RESET_ALL}")
                    else:
                        extKey = keys[int(keyIndex)-1]['key']
                        extLabel = keys[int(keyIndex)-1]['label']
                        break
                        
                dInfo = daemonInfo()
                dInfo['extPubKey'] = extKey
                dInfo['extPubKeyLabel'] = extLabel
                updateDaemonInfo(dInfo)
                input(f"Your ExtPublicKey is:\n{Fore.GREEN}{extKey}{Style.RESET_ALL}\nPress Enter to continue...")
                break
                    
            elif ans.lower() == 'n':
                print(f"Generating new extended public key...")
                
                makeExtKey()
                break
                
            else:
                print("Invalid answer! Please enter either 'y' or 'n'")
                input("Press Enter to continue...")
                
    else:
        print(f"Generating new extended public key...")
                
        makeExtKey()
        
    print(f"Checking for existing reward address...")
    
    if getRewardAddressFromWallet() == None:
        print(f"Reward address not found.")
        print(f"The reward address is where block rewards will be sent. Must be a valid public Ghost address")
        
        makeRewardAddress()
                
    else:
        print(f"Reward address found.")
        
        while True:
            ans = input(f"Would you like to continue using {getRewardAddressFromWallet()} as your reward address? {Fore.GREEN}Y/{Fore.RED}n{Style.RESET_ALL} ")
            
            if ans.lower() == 'y' or ans.lower() == '':
                dInfo = daemonInfo()
                dInfo['rewardAddress'] = getRewardAddressFromWallet()
                updateDaemonInfo(dInfo)
                print(f"Reward address successfully updated.")
                break
                
            elif ans.lower() == 'n':
                makeRewardAddress()
                break
            else:
                print("Invalid answer! Please enter either 'y' or 'n'")
                input("Press Enter to continue...")
    if system != 'Windows':
        cronFound = False
        cronBoot = False
        cmd = f"cd {os.path.expanduser('~/GhostVault/')} && {shutil.which('python3')} ghostVault.py update"
        cmdBoot = f"cd {os.path.expanduser('~/GhostVault/')} && {shutil.which('python3')} ghostVault.py start"
        print("Setting up cron job...")
        cron = CronTab(user=True)
        for job in cron:
            if cmd in str(job):
                print(f"Update cron found, skipping")
                cronFound = True
                
            elif cmdBoot in str(job):
                print(f"Start on boot cron found, skipping")
                cronBoot = True
                
        if cronFound == False:
            try:
                job3 = cron.new(command=cmd)
                job3.minute.on(0)
                job3.hour.every(2)
                cron.write()
                print("Update cron successfully set.\n")
                
            except Exception as e:
                showError(e)
        
        if cronBoot == False:
            try:
                job4 = cron.new(command=cmdBoot)
                job4.every_reboot()
                cron.write()
                print("Start on boot cron successfully set.\n")
                
            except Exception as e:
                showError(e)
    elif system == 'Windows':
        createBatchFiles()
        print(f"Setting up Windows Tasks...")
        
        try:
            subprocess.call(f'{shutil.which("schtasks")} /create /sc hourly /mo 2 /tn "GhostVault Updater" /tr "{os.path.expanduser("~")}\\GhostVault\\vaultUpdate.bat"')
            print(f"Update task successfully set.\n")
        except Exception as e:
            showError(e)
        
        shutil.copy('vaultStart.bat', f"{os.path.expanduser('~')}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\")
        print(f"Startup task successfully set.\n")
            
    print(f"Quick start success!")
    dInfo = daemonInfo()
    dInfo['firstRun'] = False
    updateDaemonInfo(dInfo)

def makeExtKey():
    while True:
        keyLabel = input(f"Please enter a label for your new extended public key: ")
        
        if len(keyLabel) == 0:
            pass
        else:
            break
    
    extKey = getNewExtAddr(keyLabel)
    print(f"Deriving keys...")
    rpcproxy().deriverangekeys(0, 999, extKey, False, True, True)
    dInfo = daemonInfo()
    dInfo['extPubKey'] = extKey
    dInfo['extPubKeyLabel'] = keyLabel
    updateDaemonInfo(dInfo)
    input(f"Your extPublicKey is:\n{Fore.GREEN}{extKey}{Style.RESET_ALL}\nPress Enter to continue...")    

def makeWallet():
    while True:
        walletName = input(f"Please enter a name for your wallet: ")
        
        if len(walletName) == 0:
            pass
        else:
            break
    
    dInfo = daemonInfo()
    dInfo['walletName'] = walletName
    createWallet(walletName)
    try:
        loadWallet(walletName)
    except:
        pass
    updateDaemonInfo(dInfo)
    words = mnemonic()
    clear()
    print(f"Your mnemonic recovery words are:\n")
    print(textwrap.fill(f"{Fore.GREEN}{words}{Style.RESET_ALL}", 80))
    
    input(f"\nPlease write down or copy these words, in order, and store them in a safe place.\nThese are your recovery words, needed to recover a corrupted wallet.\nPress Enter to continue.")
    
    importKey(words)   

def getLoad():
    if system == "Windows":
        load1, load5, load15 = psutil.getloadavg()
    else:
        load1, load5, load15 = os.getloadavg()
    return [load1, load5, load15]

def uptime():
    return time.time() - psutil.boot_time()

def isUpToDate():
    with open("links.json") as f:
        dvers = json.loads(f.read())
    
    if dvers['version'] != getNetworkInfo()['subversion'].split(':')[1].replace('/', ''):
        return False
    else:
        return True

def private():
    if daemonInfo()['firstRun'] == True:
        showError(f"You must run 'ghostVault.py quickstart' fisrt.")
    
    if daemonInfo()['anonMode'] == True:
        print(f"ANON mode is {Fore.GREEN}Active!{Style.RESET_ALL}\n\n")
        print(f"You can run '{Fore.CYAN}ghostVault.py setrewardaddress{Style.RESET_ALL}' to disable this mode.")
    
    else:
        print(f"ANON mode is {Fore.RED}NOT Active!{Style.RESET_ALL}\n\n")
        
        while True:
            
            print(f"Press Enter to quit or type '{Fore.CYAN}private{Style.RESET_ALL}' to continue with")
            ans = input(f"ANON mode setup. ")
            
            if ans == "private":
                privateSetup()
                break
            elif ans == "":
                break
            else:
                print(f"Invalid answer")
                input("Press Enter to continue...")
            
def privateSetup():
    cronPayFound = False
    clear()
    print(f"Welcome the the ANON Mode setup wizard.\n")
    print(f"Reward Address:\n{Fore.CYAN}{daemonInfo()['rewardAddress']}{Style.RESET_ALL}\n")
    
    if isStealthAddr(daemonInfo()['rewardAddress']) == True:
        atype = "Stealth"
    else:
        atype = "Public"
    
    print(f"Address Type: {atype}\n")
    
    print(f"If you use a stealth address funds will be sent directly to it.")
    print(f"If you use a public address, funds will pass through your\ncoldstaking node's internal anon wallet before being sent to your public address\n")
    while True:
        ans = input(f"Would you like to use this address? {Fore.GREEN}Y/{Fore.RED}n{Style.RESET_ALL} ")
        
        if ans.lower() == 'y' or ans.lower() == '':
            setAnonAddress(daemonInfo()['rewardAddress'])
            break
        elif ans.lower() == 'n':
            makeAnonAddress()
            break
        else:
            print("Invalid answer! Please enter either 'y' or 'n'")
            input("Press Enter to continue...")

    addr = getNewStealthAddr()
    setRewardAddress(addr, anon=True)
    if system != 'Windows':
        cmdPay = f"cd {os.path.expanduser('~/GhostVault/')} && {shutil.which('python3')} ghostVault.py cronpay"
        print("Setting up cron job")
        cron = CronTab(user=True)
        for job in cron:
            if cmdPay in str(job):
                print(f"cron job found, skipping")
                cronPayFound = True
                
        if cronPayFound == False:
            try:
                job3 = cron.new(command=cmdPay)
                job3.minute.every(15)
                cron.write()
                print("Cron successfully set.\n")
                
            except Exception as e:
                showError(e)
    elif system == 'Windows':
        createBatchFiles()
        print(f"Creating Windows task...")
        
        try:
            subprocess.call(f'{shutil.which("schtasks")} /create /sc minute /mo 15 /tn "GhostVault Payment Processor" /tr "{os.path.expanduser("~")}\\GhostVault\\vaultPay.bat"')
            print(f"Task successfully set.\n")
        except Exception as e:
            showError(e)
    
    dInfo = daemonInfo()
    dInfo['anonMode'] = True
    dInfo['internalAnon'] = addr
    updateDaemonInfo(dInfo)
    
    print(f"ANON mode successfully activated!")

def cronPayment():
    if daemonInfo()['anonRewardAddress'] == "" or validateAddress(daemonInfo()['anonRewardAddress']) == False:
        return
    balance = getBalances()['mine']['trusted']
    
    if isStealthAddr(daemonInfo()['anonRewardAddress']) == True:
        payee = daemonInfo()['anonRewardAddress']
        ptype = "ext anon"
    else:
        payee = daemonInfo()['internalAnon']
        ptype = "int anon"
    
    if balance >= 0.1:
        try:
            txid = rpcproxy().sendtypeto("ghost", "anon", [{"address": payee, "amount": balance, "subfee": True}])
        except Exception as e:
            showError(e)
        
        with open("payment.log", "a") as f:
            f.write(f"{datetime.utcnow()} TYPE: {ptype} TXID: {txid} AMOUNT: {balance}\n")
            
    anonBalance = getBalances()['mine']['anon_trusted']
    
    if anonBalance >= 0.1:
        try:
            txid = rpcproxy().sendtypeto("anon", "ghost", [{"address": f"{daemonInfo()['anonRewardAddress']}", "amount": anonBalance, "subfee": True}])
        except Exception as e:
            showError(e)
        
        with open("payment.log", "a") as f:
            f.write(f"{datetime.utcnow()} TYPE: ext pub TXID: {txid} AMOUNT: {anonBalance}\n")

def status():
    clear()
    tnow = time.time()
    day = 86400
    day = tnow - day
    filter = rpcproxy().filtertransactions({"from":int(day), "to":int(tnow),"count":100000,"category":"stake","collate":True,"include_watchonly":True,"with_reward":True})
    
    print(f"{Fore.BLUE}#{Style.RESET_ALL}"*80)

    print(f"GhostVault {version}")
    print(f"Hostname                        : {Fore.GREEN}{platform.node()}{Style.RESET_ALL}")
    print(f"Uptime/Load Average             : {Fore.GREEN}{str(timedelta(seconds=uptime())).split('.')[0]}, {getLoad()[0]} {getLoad()[1]} {getLoad()[2]}{Style.RESET_ALL}")
    
    if daemonInfo()['anonMode'] == True:
        print(f"privacy mode                    : {Fore.GREEN}ANON{Style.RESET_ALL}")
    elif isStealthAddr(daemonInfo()['rewardAddress']) == True:
        print(f"privacy mode                    : {Fore.YELLOW}ENHANCED{Style.RESET_ALL}")
    else:
        print(f"privacy mode                    : {Fore.RED}NORMAL{Style.RESET_ALL}")
    
    if checkConnect() == False:
        print(f"ghostd version                  : {Fore.RED}DAEMON NOT CONNECTED{Style.RESET_ALL}")
        print(f"ghostd up-to-date               : {Fore.RED}DAEMON NOT CONNECTED{Style.RESET_ALL}")
        print(f"ghostd running                  : {Fore.RED}DAEMON NOT CONNECTED{Style.RESET_ALL}")
        print(f"ghostd uptime                   : {Fore.RED}DAEMON NOT CONNECTED{Style.RESET_ALL}")
        print(f"ghostd responding (RPC)         : {Fore.RED}DAEMON NOT CONNECTED{Style.RESET_ALL}")
        print(f"ghostd connecting (peers)       : {Fore.RED}DAEMON NOT CONNECTED{Style.RESET_ALL}")
        print(f"ghostd blocks synced            : {Fore.RED}DAEMON NOT CONNECTED{Style.RESET_ALL}")
        print(f"last block (local ghostd)       : {Fore.RED}DAEMON NOT CONNECTED{Style.RESET_ALL}")
        print(f"   (explorer.myghost.org)       : {Fore.GREEN}{getExplorerHeight()}{Style.RESET_ALL}")
        print(f"ghostd is good chain            : {Fore.RED}DAEMON NOT CONNECTED{Style.RESET_ALL}")
        print(f"ghostd staking enabled          : {Fore.RED}DAEMON NOT CONNECTED{Style.RESET_ALL}")
        print(f"ghostd staking currently?       : {Fore.RED}DAEMON NOT CONNECTED{Style.RESET_ALL}")
        print(f"ghostd staking difficulty       : {Fore.RED}DAEMON NOT CONNECTED{Style.RESET_ALL}")
        print(f"ghostd network stakeweight      : {Fore.RED}DAEMON NOT CONNECTED{Style.RESET_ALL}")
        print(f"currently staking               : {Fore.RED}DAEMON NOT CONNECTED{Style.RESET_ALL}")
        print(f"total in coldstaking            : {Fore.RED}DAEMON NOT CONNECTED{Style.RESET_ALL}")
        print(f"stakes/earned last 24h          : {Fore.RED}DAEMON NOT CONNECTED{Style.RESET_ALL}")
    
    elif isUpToDate() == False:
        print(f"ghostd version                  : {Fore.RED}{getNetworkInfo()['subversion'].split(':')[1].replace('/', '')}{Style.RESET_ALL}")
        print(f"ghostd up-to-date               : {Fore.RED}NO{Style.RESET_ALL}")
        print(f"ghostd running                  : {Fore.GREEN}YES{Style.RESET_ALL}")
        print(f"ghostd uptime                   : {Fore.GREEN}{str(timedelta(seconds=getUptime())).split('.')[0]}{Style.RESET_ALL}")
        print(f"ghostd responding (RPC)         : {Fore.GREEN}YES{Style.RESET_ALL}")
        
        if getPeerCount() == 0:
            print(f"ghostd connecting (peers)       : {Fore.RED}{getPeerCount()}{Style.RESET_ALL}")
        else:
            print(f"ghostd connecting (peers)       : {Fore.GREEN}{getPeerCount()}{Style.RESET_ALL}")
        
        if isSyncing() == True:
            print(f"ghostd blocks synced            : {Fore.RED}NO{Style.RESET_ALL}")
            print(f"last block (local ghostd)       : {Fore.RED}{getBlockHeight()}{Style.RESET_ALL}")
        else:
            print(f"ghostd blocks synced            : {Fore.GREEN}YES{Style.RESET_ALL}")
            print(f"last block (local ghostd)       : {Fore.GREEN}{getBlockHeight()}{Style.RESET_ALL}")
            
        print(f"   (explorer.myghost.org)       : {Fore.GREEN}{getExplorerHeight()}{Style.RESET_ALL}")
        
        if isBadFork() == True:
            print(f"ghostd is good chain            : {Fore.RED}NO{Style.RESET_ALL}")
        else:
            print(f"ghostd is good chain            : {Fore.GREEN}YES{Style.RESET_ALL}")
        
        if getStakingInfo()['enabled'] == False:
            print(f"ghostd staking enabled          : {Fore.RED}NO{Style.RESET_ALL}")
        else:
            print(f"ghostd staking enabled          : {Fore.GREEN}YES - {getStakingInfo()['percentyearreward']}%{Style.RESET_ALL}")
            
        if getStakingInfo()['staking'] == False and getStakingInfo()['enabled'] == False:
            print(f"ghostd staking currently?       : {Fore.RED}NO{Style.RESET_ALL}")
        
        elif getStakingInfo()['staking'] == False and getStakingInfo()['enabled'] == True:
            if 'cause' in getStakingInfo():
                print(f"ghostd staking currently?       : {Fore.RED}NO - {getStakingInfo()['cause']}{Style.RESET_ALL}")
            else:
                print(f"ghostd staking currently?       : {Fore.RED}NO{Style.RESET_ALL}")
        
        else:
            print(f"ghostd staking currently?       : {Fore.GREEN}YES{Style.RESET_ALL}")
            
        print(f"ghostd staking difficulty       : {Fore.GREEN}{getStakingInfo()['difficulty']}{Style.RESET_ALL}")
        print(f"ghostd network stakeweight      : {Fore.GREEN}{convertFromSat(getStakingInfo()['netstakeweight']):,}{Style.RESET_ALL}")
        
        if getColdStakingInfo()['currently_staking'] == 0:
            print(f"currently staking               : {Fore.RED}0{Style.RESET_ALL}")
        else:
            print(f"currently staking               : {Fore.GREEN}{getColdStakingInfo()['currently_staking']}{Style.RESET_ALL}")
            
        if getColdStakingInfo()['coin_in_coldstakeable_script'] == 0:
            print(f"total in coldstaking            : {Fore.RED}0{Style.RESET_ALL}")
        else:
            print(f"total in coldstaking            : {Fore.GREEN}{getColdStakingInfo()['coin_in_coldstakeable_script']}{Style.RESET_ALL}")
            
        if filter['collated']['records'] == 0:
            print(f"stakes/earned last 24h          : {Fore.RED}0{Style.RESET_ALL}/{Fore.RED}0{Style.RESET_ALL}")
        else:
            print(f"stakes/earned last 24h          : {Fore.GREEN}{filter['collated']['records']}{Style.RESET_ALL}/{Fore.GREEN}{filter['collated']['total_reward']}{Style.RESET_ALL}")
            
            
    
    else:
        print(f"ghostd version                  : {Fore.GREEN}{getNetworkInfo()['subversion'].split(':')[1].replace('/', '')}{Style.RESET_ALL}")
        print(f"ghostd up-to-date               : {Fore.GREEN}YES{Style.RESET_ALL}")
        print(f"ghostd running                  : {Fore.GREEN}YES{Style.RESET_ALL}")
        print(f"ghostd uptime                   : {Fore.GREEN}{str(timedelta(seconds=getUptime())).split('.')[0]}{Style.RESET_ALL}")
        print(f"ghostd responding (RPC)         : {Fore.GREEN}YES{Style.RESET_ALL}")
        
        if getPeerCount() == 0:
            print(f"ghostd connecting (peers)       : {Fore.RED}{getPeerCount()}{Style.RESET_ALL}")
        else:
            print(f"ghostd connecting (peers)       : {Fore.GREEN}{getPeerCount()}{Style.RESET_ALL}")
            
        if isSyncing() == True:
            print(f"ghostd blocks synced            : {Fore.RED}NO{Style.RESET_ALL}")
            print(f"last block (local ghostd)       : {Fore.RED}{getBlockHeight()}{Style.RESET_ALL}")
        else:
            print(f"ghostd blocks synced            : {Fore.GREEN}YES{Style.RESET_ALL}")
            print(f"last block (local ghostd)       : {Fore.GREEN}{getBlockHeight()}{Style.RESET_ALL}")
        
        print(f"   (explorer.myghost.org)       : {Fore.GREEN}{getExplorerHeight()}{Style.RESET_ALL}")
        
        if isBadFork() == True:
            print(f"ghostd is good chain            : {Fore.RED}NO{Style.RESET_ALL}")
        else:
            print(f"ghostd is good chain            : {Fore.GREEN}YES{Style.RESET_ALL}")
        
        if getStakingInfo()['enabled'] == False:
            print(f"ghostd staking enabled          : {Fore.RED}NO{Style.RESET_ALL}")
        else:
            print(f"ghostd staking enabled          : {Fore.GREEN}YES - {getStakingInfo()['percentyearreward']}%{Style.RESET_ALL}")
        
        if getStakingInfo()['staking'] == False and getStakingInfo()['enabled'] == False:
            print(f"ghostd staking currently?       : {Fore.RED}NO{Style.RESET_ALL}")
        
        elif getStakingInfo()['staking'] == False and getStakingInfo()['enabled'] == True:
            if 'cause' in getStakingInfo():
                print(f"ghostd staking currently?       : {Fore.RED}NO - {getStakingInfo()['cause']}{Style.RESET_ALL}")
            else:
                print(f"ghostd staking currently?       : {Fore.RED}NO{Style.RESET_ALL}")
        
        else:
            print(f"ghostd staking currently?       : {Fore.GREEN}YES{Style.RESET_ALL}")
            
        print(f"ghostd staking difficulty       : {Fore.GREEN}{getStakingInfo()['difficulty']}{Style.RESET_ALL}")
        print(f"ghostd network stakeweight      : {Fore.GREEN}{convertFromSat(getStakingInfo()['netstakeweight']):,}{Style.RESET_ALL}")
        
        if getColdStakingInfo()['currently_staking'] == 0:
            print(f"currently staking               : {Fore.RED}0{Style.RESET_ALL}")
        else:
            print(f"currently staking               : {Fore.GREEN}{getColdStakingInfo()['currently_staking']}{Style.RESET_ALL}")
            
        if getColdStakingInfo()['coin_in_coldstakeable_script'] == 0:
            print(f"total in coldstaking            : {Fore.RED}0{Style.RESET_ALL}")
        else:
            print(f"total in coldstaking            : {Fore.GREEN}{getColdStakingInfo()['coin_in_coldstakeable_script']}{Style.RESET_ALL}")
            
        if filter['collated']['records'] == 0:
            print(f"stakes/earned last 24h          : {Fore.RED}0{Style.RESET_ALL}/{Fore.RED}0{Style.RESET_ALL}")
        else:
            print(f"stakes/earned last 24h          : {Fore.GREEN}{filter['collated']['records']}{Style.RESET_ALL}/{Fore.GREEN}{filter['collated']['total_reward']}{Style.RESET_ALL}")
            
    print(f"{Fore.BLUE}#{Style.RESET_ALL}"*80)
    
def makeAnonAddress():
    while True:
        clear()
        print(f"If you use a stealth address funds will be sent directly to it.")
        print(f"If you use a public address, funds will pass through your\ncoldstaking node's internal anon wallet before being sent to your public address\n")
        ans = input(f"Please enter the address that you wish to recieve block rewards at: ")
        
        if validateAddress(ans) == True:
            print(f"You have selected to recieve rewards at:\n{Fore.CYAN}{ans}{Style.RESET_ALL}\n")
            confirm = input(f"Press Enter to confirm or enter anyting to try again.")
            
            if confirm == "":
                setAnonAddress(ans)
                break
            else:
                pass
        else:
            print(f"Not a valid Ghost address. Please try again.")
            input("Press Enter to continue...")

def makeRewardAddress():
    if daemonInfo()['anonMode'] == True:
        clear()
        print(f"ANON mode is {Fore.GREEN}Active!{Style.RESET_ALL}\n\n")
        print(f"Continuing will disable ANON mode.")
        while True:
            ans = input(f"Type {Fore.CYAN}public{Style.RESET_ALL} to continue or Enter to exit: ")
            
            if ans == 'public':
                print(f"Continuing...")
                break
            elif ans == '':
                print(f"Exiting...")
                sys.exit()
            else:
                print(f"Unknown answer, please try again.")
                input("Press Enter to continue...")
    
    while True:
        clear()
        print(f"Using a stealth address will enable Enhanced Privacy.")
        ans = input(f"Please enter the address that you wish to recieve block rewards at: ")
        
        if validateAddress(ans) == True:
            print(f"You have selected to recieve rewards at: {Fore.CYAN}{ans}{Style.RESET_ALL}\n")
            confirm = input(f"Press Enter to confirm or enter anything to try again.")
            
            if confirm == "":
                setRewardAddress(ans)
                if daemonInfo()['anonMode'] == True:
                    dInfo = daemonInfo()
                    dInfo['anonMode'] = False
                    updateDaemonInfo(dInfo)
                break
            else:
                pass
        else:
            print(f"Not a valid Ghost address. Please try again.")
            input("Press Enter to continue...")

def waitForDaemon():
    count = 0
    while True:
        time.sleep(3)
        online = checkConnect()
        
        if online == True:
            break
        
        if count == 40:
            showError("Daemon Failed to start")
        count += 1

def waitForDaemonShutdown():
    print("Waiting for full daemon shutdown...")
    count = 0
    if system == 'Linux':
        pidFile = os.path.expanduser('~/.ghost/ghost.pid')
    elif system == 'Darwin':
        pidFile = os.path.expanduser('~/Library/Application Support/Ghost/ghost.pid')
    elif system == 'Windows':
        pidFile = os.path.expanduser('~/AppData/Roaming/Ghost/ghost.pid')
    while True:
        
        if os.path.isfile(pidFile):
            with open(pidFile) as f:
                pid = f.read()
            
            if psutil.pid_exists(int(pid)):
                pass
            else:
                print(f"Unclean shutdown detected. Removing PID file.")
                os.remove(pidFile)
                break
        else:
            break
            
        if count == 40:
            showError("Shutdown error. Please try again.")
        count += 1
        time.sleep(3)

def help():
    print(f"GhostVault {version} Help text.")
    print(f"Usage: GhostVault.py [OPTION]\n\n")
    print(f"Options:\n")
    print(f"{Fore.BLUE}status{Style.RESET_ALL}            :  Returns staking node status.")
    print(f"{Fore.BLUE}quickstart{Style.RESET_ALL}        :  Runs the quickstart guide.")
    print(f"{Fore.BLUE}start{Style.RESET_ALL}             :  Starts the ghost daemon.")
    print(f"{Fore.BLUE}stop{Style.RESET_ALL}              :  Stops the ghost daemon.")
    print(f"{Fore.BLUE}restart{Style.RESET_ALL}           :  Restarts the ghost daemon.")
    print(f"{Fore.BLUE}rewardaddress{Style.RESET_ALL}     :  Returns current reward address.")
    print(f"{Fore.BLUE}setrewardaddress{Style.RESET_ALL}  :  Sets new reward address.")
    print(f"{Fore.BLUE}showextkey{Style.RESET_ALL}        :  Shows your extended public key.")
    print(f"{Fore.BLUE}newextkey{Style.RESET_ALL}         :  Creates a new extended public key.")
    print(f"{Fore.BLUE}checkchain{Style.RESET_ALL}        :  Checks that ghostd is on the correct chain.")
    print(f"{Fore.BLUE}forceresync{Style.RESET_ALL}       :  Forces ghostd to resync. Use in case of bad chain.")
    print(f"{Fore.BLUE}update{Style.RESET_ALL}            :  Self updater for GhostVault and ghostd.")
    print(f"{Fore.BLUE}forceupdate{Style.RESET_ALL}       :  Downloads Ghostd even if update is not needed.")
    print(f"{Fore.BLUE}private{Style.RESET_ALL}           :  Checks privacy mode and initiates anon mode activation.")
    print(f"{Fore.BLUE}stats{Style.RESET_ALL}             :  Basic staking stats.")
    print(f"{Fore.BLUE}anonaddress{Style.RESET_ALL}       :  Shows the current payment address when in anon mode.")
    print(f"{Fore.BLUE}setanonaddress{Style.RESET_ALL}    :  Sets new payment address when in anon mode.")
    print(f"{Fore.BLUE}balance{Style.RESET_ALL}           :  Shows internal wallet balances.")
    print(f"{Fore.BLUE}enableelectrumx{Style.RESET_ALL}   :  Enables txindex=1 in config for use with electrumx server.")
    print(f"{Fore.BLUE}cronpay{Style.RESET_ALL}           :  Activates the payment processor. Used in a cron job.")

def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "help":
            help()
        
        elif arg  == "quickstart":
            quickstart()
        
        elif arg == "restart":
            restartDaemon()
            if isSyncing() == True:
                syncProgress()
        
        elif arg == "start":
            startDaemon()
            if isSyncing() == True:
                syncProgress()
        
        elif arg == "stop":
            stopDaemon()
        
        elif arg == "rewardaddress":
            if getRewardAddressFromWallet() == None:
                print(f"Reward address not set!\nPlease run '{Fore.CYAN}ghostVault.py setrewardaddress{Style.RESET_ALL}' to set a reward address.")
            else:
                print(f"Your reward address is currently set to:\n\n{Fore.CYAN}{getRewardAddressFromWallet()}{Style.RESET_ALL}")
        
        elif arg == "setrewardaddress":
            makeRewardAddress()
        
        elif arg == "showextkey":
            
            key = daemonInfo()['extPubKey']
            
            if key == '':
                print(f"Extended public key not set.\nPlease run '{Fore.CYAN}ghostVault.py quickstart{Style.RESET_ALL}' to set up your staking node.")
            
            else:
                print(f"Your extended public key is:\n\n{Fore.CYAN}{key}{Style.RESET_ALL}")
        
        elif arg == "update":
            if system == "Windows":
                repo = git.Repo(f"{os.path.expanduser('~')}\\GhostVault")
            else:
                repo = git.Repo(os.path.expanduser("~/GhostVault"))
            repo.remotes.origin.pull()
            
            print(f"Checking if ghostd is up to date...")
            if checkConnect() == False:
                showError(f"Daemon not connected! Please start the daemon with 'ghostVault.py start'.")
            
            if isUpToDate() == True:
                print(f"ghostd is up to date!")
            else:
                print(f"ghostd is out of date! Updating...")
                stopDaemon()
                waitForDaemonShutdown()
                removeArchive()
                removeDaemon()
                downloadDaemon()
                extractDaemon()
                prepareDataDir()
                startDaemon()
                
        elif arg == "checkchain":
            if isBadFork() == False:
                print(f"You are on the correct chain!")
            else:
                showError(f"Bad chain detected! Please run 'ghostVault.py forceresync' to force a resync.")
                
        elif arg == "forceresync":
            print("Forcing resync...")
            stopDaemon()
            waitForDaemonShutdown()
            clearBlocks()
            time.sleep(5)
            startDaemon()
            if isSyncing() == True:
                syncProgress()
                
            if isBadFork() == True:
                showError(f"Bad fork detected. Please run 'ghostVault.py forceresync' to force a resync.")
            print(f"Daemon is now synced with the Ghost network")

        elif arg == "enableelectrumx":
            print(f'Checking for txindex...')
            if system == 'Linux':
                datadir = os.path.expanduser('~/.ghost/')
            elif system == 'Darwin':
                datadir = os.path.expanduser('~/Library/Application Support/Ghost/')
            elif system == 'Windows':
                datadir = os.path.expanduser('~/AppData/Roaming/Ghost/')

            with open(os.path.join(datadir, "ghost.conf")) as f:
                lines = f.readlines()

            if "txindex=1\n" in lines:
                print(f'txindex found, electrumx mode enabled.')
            else:
                print(f'txindex  not found, activating electrumx mode..')
                with open(os.path.join(datadir, "ghost.conf"), 'a') as f:
                    f.write(f"txindex=1\n")
                print("Resyncing with the Ghost network...")
                stopDaemon()
                clearBlocks()
                time.sleep(5)
                startDaemon()
                if isSyncing() == True:
                    syncProgress()

                if isBadFork() == True:
                    showError(f"Bad fork detected. Please run 'ghostVault.py forceresync' to force a resync.")
                print(f"Daemon is now synced with the Ghost network")
        
        elif arg == "status":
            status()
        
        elif arg == "private":
            private()
            
        elif arg == 'stats':
            getStats()
        
        elif arg == 'cronpay':
            cronPayment()
            
        elif arg == 'anonaddress':
            if daemonInfo()['anonMode'] == False:
                print(f"ANON Mode not active!\nPlease run '{Fore.CYAN}ghostVault.py private{Style.RESET_ALL}' to activate ANON Mode.")
            else:
                print(f"Your anon reward address is currently set to:\n\n{Fore.CYAN}{daemonInfo()['anonRewardAddress']}{Style.RESET_ALL}")
                
        elif arg == 'setanonaddress':
            if daemonInfo()['anonMode'] == False:
                print(f"ANON Mode not active!\nPlease run '{Fore.CYAN}ghostVault.py private{Style.RESET_ALL}' to activate ANON Mode.")
            else:
                makeAnonAddress()
                
        elif arg == 'balance':
            print(f"GhostVault {version} balances.\n")
            
            for i in getBalances()['mine']:
                print(f"{i}: {getBalances()['mine'][i]}")
                
        elif arg == 'forceupdate':
            print(f"Force updating Ghostd...")
            stopDaemon()
            waitForDaemonShutdown()
            removeArchive()
            removeDaemon()
            downloadDaemon()
            extractDaemon()
            startDaemon()
        
        elif arg == 'newextkey':
            print(f"Getting new Extended Public Key...")
            makeExtKey()
                
        else:
            print(f"Unknown argument '{arg}'.\nPlease run '{Fore.CYAN}ghostVault.py help{Style.RESET_ALL}' for full list of commands.")
                
    else:
        help()

if __name__ == "__main__":
    main()
