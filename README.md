# chivalry-server-configuration
automated installation and configuration of a dedicated server for Chivalry Medieval Warfare - Windows only

## Author: 
MrFDA - follow me @MrFDA69 on twitter

## Requirements: 
- python 2.7 on a Windows platform (32 and 64 bits are supported)
- several python modules, most of them beeing 'standard' modules. More precisely:
    - os, sys, json, re, shutil, zipfile, urllib2, random, subprocess, platform
    - argparse
If some of them are not included in your python distribution, the simplest way to obtain the missing ones is with pip in the console (pip install + module_name). For more information, see python documentation.

## Objectives
This project tries to simplify the installation and configuration of a dedicated server for Chivalry Medieval Warfare.
First things first, only a small number of options are intended to be modified with this project. The selection might be higly personnal, but this project tries to stay simple and default configuration seems fine for other parameters.
Options that can be modified with this project:
- server name
- server 'user' and administrator passwords
- number of players allowed on the server
- activation/deactivation of auto-balance
- gore level
- maps used ++++ (probably the most usefull part of the project)

## What does this project do?
Check if steamcmd is installed, and install if it isn't.
Install and update Chivalry dedicated server.
Configure Chivalry dedicated server.
Launch Chivalry dedicated server.

## What does this project don't do?
The most important thing that is left to the user is to configure (if necessary) its router to forward the ports used by the server (UDP protocol only).
By default, the ports used are 7777, 7778, and 27015 (this last one beeing for steam itself) (this is true at the time this readme is being written (i.e. March 2017)).
You might also have to allow UDP connections on this ports in your firewall, see its documentation.

## Important notes
Some bits of code comes from comments on sites like stackoverflow. They are clearly identified and linked to their sources. I do not have any rights on them, and any licencing of this product do not apply to them.
This project comes with ABSOLUTELY NO WARRANTY. Use it at your OWN RISKS. Modifing options as you like should be safe, but any sort of code injection through these parameters is likely to succed and might be disastrous.

## How to use this project
This project is mainly composed of 3 files:
- a configuration script: core of the project, nothing should be changed here
- a txt file containing a list of maps: based on a list available online, not intended to be modified
- a json configuration file, where you can change parameters.

To open the configuration file (default name: ServerConfig.json) use a text editor (right click -> open with -> notepad or equivalent -- I recommand Notepad++, see https://notepad-plus-plus.org)
Each parameter should be included within a double quotation mark (") and each line should end with a comma.
Parameters into brackets can contain multiple values, each value should be included within a double quotation mark and separated from the previous one with a comma.
Do not change the parameter name (the name before the colon) (or configuration will fail).

Parameters available in the [configuration file](chivalry_server_configuration.py):
- SteamCMD: path to the directory where steamcmd (a steam client usable with command line) is installed or should be installed, default "C:\steamcmd"
- ServerDir: name of the directory where the server files will be installed (or are already installed) in the steamcmd directory
- ServerName: name of the server (no kidding ^^) as it will appear in the server list
- GamePassword: password required to access to the server, leave an empty string ("") for no password
- AdminPassword: password required to gain administrator rights on the server (within the game). It is highly advised to change the default password ("azerty"). Leave an empty string ("") for no password (not recommended)
- MaxPlayers: maximum number of players allowed on the server. Default=32. Valid values for this project range from 1 to 64.
- GoreLevel: how gore is the game. Default=2(maximum). Valid values for this project range from 0 to 2 (as it seems to be the official range of values).
- bAutoBalance: should there be some autobalance between the teams ? Must be "true" (default) or "false"
- MapTypes: types of maps that should be included in the list of map available on the server. Multiple values can be set. Valid values are "TO", "LTS", "CTF", "Duel", "FFA", "KOTH", "TD". See below for more explanations
- MapExclude: name of maps that should not be included in the list of map available on the server. Multiple values can be set. Map names can be found in [MapList](MapList.txt).

To launch the script, you will need one command line: right click in the folder containing the script while holding the shift key, and select 'open a command prompt here', then type 'python chivalry_server_configuration.py' (alternatively, you can use the run command of ipython)
Four options can be set at the end of this command: 
- -c path_of_the_configuration_file -- allow you to have different configurations stores and to chose which one to use (the command will look like 'python chivalry_server_configuration.py -c MyConfiguration.json')
- -m path_of_the_map_list_file -- similarly, allow you to precise the path of the file containing the list of maps (could be another way to customize your set of maps)
- -s -- skip the update of the server before launch
- -h -- show the available options (i.e. -c, -m and -s) and exit the script

## Note on maps
The most simple way to select a set of maps is to indicate a type of map in the configuration file as described above. 
"TO" = TEAM OBJECTIVE, "LTS" = LAST TEAM STANDING, "CTF" = CAPTURE THE FLAG, "Duel" = self explanatory ^^, "FFA" = FREE FOR ALL, "KOTH" = KING OF THE HILL, "TD" = TEAM DEATHMATCH (for more information on each mode, see the game documentation).
All the maps included in each set are available in the [MapList](MapList.txt) file.
If you don't want one (or more) specific map to be included in the set, put its name under MapExclude in [the configuration file](chivalry_server_configuration.py).
The order of the maps is randomised each time the script is executed, and the first map (required to launch the server) is randomly chosen within this set.
