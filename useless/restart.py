# Copyright (C) 2015 Peter Steffey

#Needed import statemnts
from tempfile import mkstemp
from shutil import move
from os import remove, close
import subprocess
import os
import string
import datetime
import json
import socket
from os.path import expanduser
import time
import commands
import re
import getpass
import shutil

from utility import *

print 'Adding command "refresh" in /usr/bin'
#adds refresh command to bash, so users can just type "refresh" to run analyze.py
bashFile = open('refresh', 'w')
bashFile.write('#!/bin/bash\npython ' + getSafeDirPath() + '/analyze\n')
bashFile.close()
shutil.move('refresh', '/usr/bin/refresh')
do('sudo chmod +x /usr/bin/refresh')

#array to hold directory names to watch
toWatch = []

#starts watching init.d for updates, new programs, etc
toWatch.append('/etc/init.d')

#starts watching ufw for up/down events
toWatch.append('/etc/ufw')

#deletes initialization function
do('sudo rm ' + getSafeDirPath() + '/initialize.py')

with open(getDirPath() + '/recording', 'r') as readFile:
    text = decrypt(readFile)

    #for each vulnerability in the elements.csv file
    vulnerabilities = json.loads(text)
    for vul in vulnerabilities:

        #if this category involves a file path, watch that file path for changes and call analyze.py is it does
        if vul['type'] == "FileContents" or vul['type'] == "FileExistance" or vul['type'] == "Forensics" or vul['type'] == "Permissions":

            #get the url and place a watch on the directory above it (to catch all cases)
            filepath = vul['extras'][0]
            comps = filepath.split('/')
            filepathDir = "/".join(comps[:(len(comps)-1)])
            print "watching " + filepathDir + '/'
            if filepathDir not in toWatch:
                toWatch.append(filepathDir)

        #if this category involves a service, watch the configuration directory for that service for start/stop actions
        elif vul['type'] == "Service":

            #get the url and place a watch on the directory above it (to catch all cases)
            print "watching " + '/etc/' + vul['extras'][0]
            filepathDir = '/etc/' + vul['extras'][0]
            if filepathDir not in toWatch:
                toWatch.append(filepathDir)

    readFile.close()

#implement watching
for item in toWatch:
    watch(item)

settings = getSettings()

#if this is the first boot after initialization
if not hasattr(settings, 'start'):

    #get the current time string in seconds
    now = datetime.datetime.now()
    start = (now.hour * 3600) + (now.minute * 60) + (now.second)

    addSetting('start', start, True, True)

#run the analyze.py to catch any points that resulted from restarting the machine
if os.path.isfile(getSafeDirPath() + '/holder'):
    os.remove(getSafeDirPath() + '/holder')
os.system('python ' + getSafeDirPath() + '/analyze')
