# Shidbot

This is a fork of the original discord pizzabot.

## This version contains the following changes:

-Removed two id checks that were for a specific use-case, now it can be used anywhere

-Messages prefixed with two dashes '--' will be ignored by the bot. This is useful to have small conversations in the bot room without being interrupted.

-Added the ability to whitelist channel ID's for sending reply messages, meaning the bot can be configured to only write responses in your discord guild's bot room when prompted.

-Added date and time for events that are printed to the console.

-Added the missing .env file for the bot id.

-Works properly instead of being a simple message logger.

# Installation instructions:


## Installing needed packages

## AlmaLinux 8 / Rocky Linux 8 / Oracle Linux 8 / possibly CentOS Stream 8 / other Red Hat Enterprise 8 derivatives
sudo dnf install epel-release

sudo dnf install python3 mariadb-server screen 

## CentOS 7 / Scientific Linux 7 / Oracle Linux 7 / other Red Hat Enterprise 7 derivatives
sudo yum install python3 mariadb-server screen

## Fedora Linux Workstation / Server
sudo dnf install python3 mariadb-server screen

## openSUSE Leap / Tumbleweed / SUSE Linux Enterprise
sudo zypper in python3 mariadb screen

## Mageia Linux
dnf install python3 mariadb screen

or

urpmi python3 mariadb screen

## Debian + derivatives / Ubuntu + derivatives
sudo apt install python3 mariadb-server screen

## Alpine linux + derivatives
sudo apk add python3 mysql mysql-client py3-pip

## Android (Termux)
pkg install python mariadb screen

## Other OS's
Other Linux distros and other operating systems that supply Python 3 and MariaDB server will work too (screen is an optional extra, just to allow the bot to run in the background), though its package installation instructions are not provided. Every following step should work though.


## Installing python packages from pip
pip3 install discord.py==1.7.3

pip3 install aiomysql

pip3 install python-dotenv

pip3 install discord-py-slash-command==1.1.2

## Adding credentials 

Edit the token ID in the .env file to be the bot's token. 

Edit the guild ID in the python file to be the ID of the Discord server/guild you plan to run the bot in.

Edit the whitelist ID in the python file to be the ID of the text channel you want the bot to write to when prompted.

Edit the MYSQL section's configuration details in the python file to values you plan to use in your implementation. This will be the host IP address, port, username and password.

## Enable and start mariadb server
systemctl enable mariadb --now

## Configuring mariadb for use
mysql_secure_installation


## Creating the database
mysql -u root -p

create database pizzabot;

commit;

exit;

## Create user account for db
mysql -u root -p

create user 'username'@'localhost' identified by 'password';

grant all privileges on * . * to 'username'@'localhost';

commit;

exit;

## Importing the tables
mysql -u username -p pizzabot < pizzabot.sql


## Starting the bot
screen

python3 pizzabot.py

(Control A D to disengage from the screen session, "screen -r" to re-engage)

## Backing up the database

mysqldump -u root -p pizzabot > backup.sql


## Updating pip modules in the future

sudo pip3 install pip-review

pip-review --local --interactive


In terms of bot setup on Discord's side, make sure the bot has Privileged Gateway intents turned on, and has suitable permissions (such as read messages/view channels, send messages, embed links, attach files, read message history, use external emojis. The integer would be 379904 in that example).

# Alternative version

In some cases main version refuses to respond to the messages, then you can use the alternative script.

# Credits
Chayleaf - for initial code this bot is forked from.

Jason098 - for fixing the original code into working condition.

Lazerdude - for updating the bot with various QOL features and writing proper documentation.
