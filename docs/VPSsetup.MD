**VPS Setup**

This guide is for setting up and securing a vps. This guide assumes that you have ssh access to a vps on the root account.
This guide also is for Ubuntu based systems. Other Linux systems shopuld be similar.
You can follow the first part of the guide found [here](https://ghostveterans.com/vps/)

**1. Creating a User account with sudo access**

The first thing that needs to be done is to create a reagular user account.

In this example I will be making new account for the user 'tux'. You should replace tux with the username of your choice.

```
adduser tux
```

After this it will ask you to put a new password in twice. This is an important password.
The rest of the fields can be left blank.

Once you have your new user made, let's give it sudo access so that you can do root level tasks, form a more secure user account.

This can be done as follows

```
usermod -aG sudo tux
```

Remember to replace tux with the username that you chose in the previous step.

**2. Test user account and sudo access**

Now that you have a user account with sudo access, let's test them out and make sure they work.

To switch to the new account do

```
su - tux
```

Remember to use your own user name in place of tux
You should now be in the user account. Next to the cursor instead of saying `root@hostname` it should say `tux@hostname`.
It may be a different color also.

To make sure type `whoami` in. It should return the name of your user and not root.

Now lets test to make sure that our sudo password works. 

We can test sudo and update the packages at the same time.

```
sudo apt update && sudo apt upgrade -y
```

This will ask you to put your sudo password in. Enter the password that you made earlier. It all goes well, the system update will run.

If this does not work, you need to make sure that your spelling is correct and case matters.


**3. Log out and log back in with user account**

Now that you have a new account with sudo access, we need to log out of the ssh session and log back in using the user account.

To log out, type `exit` and press enter. This will drop you back to the root shell. Type `exit` and pres enter once more. This will exit the ssh session.

Now to log back in, replace root with the username you made. Once it asks you for the password, enter the password you made for that user. The same
one used in the sudo step.

You should now be logged in as the user you made.


**4. Secure ssh**

ssh is great secure tool for accessing a shell form across a network. However ssh is heavily targeted and attacked.
The root user is the most targeted name, as well as names such as admin. The attackers will try ot log in as these users, trying passwords from large
dictionaries of common passwords. We are going to mitigate these threats by disabling logging into the root account. This means that they will not have 
direct access to root and this will stop all attempts to login using the root user. The next is we will install a package called fail2ban.
What this does is if there are 6 failed login attempts in 10 minutes, then their IP is banned for 10 minutes. Second ban is permanent.

To disable root login type

```
sudo nano /etc/ssh/sshd_config
```
You will need to enter your password. Use the down arrow to find the line that says `PermitRootLogin`
There may be a # in front of it like `#PermitRootLogin`

Using the arrow keys, move the cursor over and change the word after `PermitRootLogin` to no.
If there is a # at the front, remove it.

It should be like this `PermitRootLogin no`

Now press ctrl + x then press y then enter.

To make the changes take affect, we will restart sshd with `sudo service sshd restart`
Put in your password if asked.

To install fail2ban just do 

```
sudo apt install fail2ban
```

Enter your password then press y if prompted.

That is it. fail2ban is ready to go and working already.

With those 2 simple things, your ssh configuration is much more resilient against attackers, most being stopped dead in their tracks.


**5. Secure ssh ADVANCED optional**

As stated in the last step attackers try to log into privileged accounts using various passwords. We already mitigate much of the user names they try 
by disabling the ability to login as the root user, and by not using names such as admin. The problem is, if they know your username, they can still
attempt to breech your account. Now, chances are that you used a strong password and fail2ban will ban them before they get in.
But there is still the chance. Or maybe they already know your password. So we will use the most secure password, and that is no password at all.

By disabling passwords and using cryptographically-secure public private key pair you eliminate most threats. If someone where to somehow gain access
to your keys, then they will be able to access your server. Pretty much needing physical access to your computer. For this you can add a password to
your keys. Meaning you would need the keys plus password. This password should not be the same as the one used for logging in.

This step is labeled as optional as there is a con that might be a problem for some.
That is you will only be able to access the server from a computer that you your server has the keys for. While you can have multiple keys at once,
there may be a situation where if you do not have access to a computer that the server has the keys for, leaving you without access until you can
back to a computer that the server has the keys for.

With that said, this step is highly recomended.

This guide will be going over the instructions for Linux and Mac users. Putty users should refer to the guide found 
[here](https://www.ssh.com/academy/ssh/putty/windows/puttygen)

To start with type `exit` to close the ssh session.
Now we need to generate our ssh keys. To do this do

```
ssh-keygen -t rsa -b 4096
```

This may take a bit depending on your hardware. The first thing it will ask is

```
Enter file in which to save the key (/home/user/.ssh/id_rsa): 
```

Press enter to continue with this default path.

Next will say

```
Enter passphrase (empty for no passphrase): 
```

If you want to use a password with your key, this where to put it.

After confirming your password it will finish the key generation and end with something like this

```
The key's randomart image is:
+---[RSA 4096]----+
|      +oo. .     |
|     o = .. .    |
|    . = +  o     |
|   . o + o  + .  |
|   o+   S =  *   |
| Eo.o. . o *o = .|
|.. o. o   .o=+ * |
| .. ...   .o.+= .|
|o.  .o      +. . |
+----[SHA256]-----+
```

Your will look differently. This means it worked. 

Now that you have generated your key pair, we need to copy the public key over to the server. this can be done as follows.

```
ssh-copy-id <your user>@<the vps ip>
```

This will ask for the password for your user. This is the login password that you made for the user, not the password for the key if you set one.

Once the key is copied over, it is time to test it.

**note** This is where putty users should come back in. 

In order to test our keys, we simply need to log in to the server over ssh.

If it is working and you did not set a password, then it should log you right in with no password prompt.
If you set a password for your key, then you will see something like `Enter passphrase for key '/home/user/.ssh/id_rsa':`
This is where you put in the password for your key in, not your login password.

Once You confirm that your key works, we can disable logging in with a password.

To start

```
sudo nano /etc/ssh/sshd_config
```

Use the arrow keys to scroll down and find the line that says `PubkeyAuthentication`
change the word after it to yes and remove the 3 present as before.

Then find the line that says `PasswordAuthentication`
Change the word after to no and remove the # if present.

Now press ctrl + x then y then enter.

Finally do `sudo service sshd restart` to make the changes take place.

Your ssh session is now ironclad.

**6. Firewall**

Now for the firewall. For a GhostVault node, only 2 ports need to be accessible. Port 22 for ssh, and port 51728 for ghostd.

To start, lets get the status of ufw.

```
sudo ufw status
```
Enter your password if prompted. 

It will probably say `Status: inactive`
that is expected.

Next lets set the rules that allow our two ports. It is very critical that you enable port 22. If you fail to enable port 22 you will lose access to
the server. 

```
sudo ufw allow 22
```

and for ghostd

```
sudo ufw allow 51728
```

Again it is very critical that you enable port 22 before the next step. If you fail to enable port 22 you will lose access to
the server. 

After you are sure that port 22 is allowed, do

```
sudo ufw enable
```

This will enable the firewall. You can do `sudo ufw status` once more, and it should show active as well as the ports that are allowed.

That is it for the firewall

**7. System updates**

The last step for securing your server is the setup automatic updates. This is to ensure that all security patches are downloaded and installed.

For this we will use the cron service to schedule the task. To do this

```
sudo crontab -e
```

Enter your password, then it will ask you what editor you want to use, choose #1 for nano.

Now use the arrow keys to scroll to the bottom of the file.

at the bottom enter the following

```
0 0 * * 0 /usr/bin/apt update && /usr/bin/apt upgrade -y
```

Now press ctrl + x then y then enter.

This schedules an update once a week.

Your server is now secured.
