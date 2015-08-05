
import os.path
import time
from os.path import expanduser
import string
import os
import stat
import datetime
import json
import sys
import subprocess

import commands
import re
import smtplib

from utility import *

#for sounds
import pygame
pygame.mixer.init()

#tracks errors to show messages at end
fileError = False
saveError = False

#method to parse the boolean values in the csv
def parseBool(string):
    if string.lower() == "true": return True
    return False

#method to check the file to see if it contains all or none of the strings in the array of contents
def checkFileContents(filepath, contents, mode):
    try:
        for contains in contents:
            file = open(string.replace(filepath, '~', expanduser("~")), 'r') # if ~ exists in string, replace it with the user's home directory absolute path
            text = ' '.join(file.read().split())
            if mode:
                if contains not in text:
                    file.close()
                    return False
            else:
                if contains in text:
                    file.close()
                    return False
        file.close()
        return True
    except:
        print " * Could not find necessary file. Please contact your administrator"
        return None

#check if a file exists at a given filepath using os.path
def checkFileExists(filepath, should):
    if os.path.isfile(filepath) or os.path.isdir(filepath): return should
    return not should

#checks if a service is running using the bash command ps -A
def checkServiceRunning(serviceName, shouldBe):
    output = subprocess.check_output(['ps', '-A'])
    if serviceName in output: return shouldBe
    return not shouldBe

#checks the specific syntax for the CP forensics questions, and can handle multiple answers
def checkForensicsQuestion(filepath, answers):
    try:
        count = 0
        for ans in answers:
            file = open(filepath, 'r')
            for line in file.read().split('\n'):
                if line[:7] == "ANSWER:":
                    if ans.lower() in line[7:].lower(): # case insensitive
                        count = count + 1
        if count == len(answers): return True # if all are answered
        return False
    except:
        print " * Could not find Forensics question at " + filepath + ". Please contact your administrator"
        return None

#check if updates are installed for a specific service
def checkUpdates(serviceName, version):
    cmd = 'dpkg -l ' + serviceName + ' | grep -E \"^ii\" | tr -s \' \' | cut -d\' \' -f3'
    output,error = subprocess.Popen(cmd, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if version in output:
        return True
    return False

#checks whether a port is open
def checkPort(port, open):
    try:
        output = subprocess.check_output(['sudo','netstat','-tunelp'])
        lines = output.split('\n')
        for line in lines:
            if ':' + port in line and 'LISTEN' in line:
                return open
        return not open
    except:
        print " * Could not execute command.  Please contact your administrator"
        return None

#checks the permissions on a file and returns false if any of the permissions don't match - need to simplify
def checkPermissions(filepath, permission):
    try:
        current = oct(os.stat(filepath)[stat.ST_MODE])[-3:]
        return int(permission) == int(current)
    except:
        print " * Could not find necessary file. Please contact your administrator"
        return None

#generic command analysis for output, allowing greater flexibility
def checkCommand(command, content, should):
    try:
        output = subprocess.check_output(command.split(' '))
        shortOutput = ' '.join(output.split())
        if content in shortOutput:
            return should
        return not should
    except:
        print " * Could not execute command.  Please contact your administrator"
        return None

#to send scoring report at end
def send_email(settings):
    try:
        sendScoringReport()
        print '\n* Time is up! Scoring report has been sent to the Administrator; exiting script now...\n'
    except:
        print '\n* Time is up! Exiting script now...\n'

    #prevents email from being sent more than once
    addSetting('email', 'done', True, False)

    sys.exit()

#######################
# Program starts here #
#######################

#load the settings dictionary from the encrypted file
settings = getSettings()

#if the administrator made this a timed image
if settings['limit'] != -1:

    #get the current time string in seconds
    now = datetime.datetime.now()

    #if the email has already been sent, inform the user and get out of here
    if settings['email'] == 'done':
        print '\n* Time is up! Scoring report has been sent to the Administrator; exiting script now...\n'
        sys.exit()

    timeNow = (now.hour * 3600) + (now.minute * 60) + (now.second)
    timeStart = settings['start']
    timeLimit = settings['limit']

    #if time is up, inform user and send email to coach/mentor
    if timeNow - timeStart > timeLimit:
        notify("Out of Time!", "Your score is frozen.  Please stop working and back away from this image.  It may explode.")

        if settings['email'] == 'n/a':
            print '\n* Time is up! Exiting script now...\n'
            sys.exit()

        #prevents the email from being sent multiple times
        send_email(settings)

#more checks
changed = False
new = False
penalty = False

with open(getDirPath() + '/recording', 'r') as readFile:
    text = decrypt(readFile, "A7jcCd88fl93ndAvy1d8cX0dl")
    rows = json.loads(text)

    #for each line in the recording file
    i = 0
    for row in rows:
        print "Checking element " + str(i+1)
        function = False # function is goine to be a boolean value
        if row['type'] == "FileContents":
            function = checkFileContents(row['extras'][0], row['extras'][2:], parseBool(row['extras'][1]))
        elif row['type'] == "FileExistance":
            function = checkFileExists(row['extras'][0], parseBool(row['extras'][1]))
        elif row['type'] == "Service":
            function = checkServiceRunning(row['extras'][0], parseBool(row['extras'][1]))
        elif row['type'] == "Forensics":
            function = checkForensicsQuestion(row['extras'][0], row['extras'][1:])
        elif row['type'] == "Updates":
            function = checkUpdates(row['extras'][0], row['extras'][1])
        elif row['type'] == "Permissions":
            function = checkPermissions(row['extras'][0], row['extras'][1])
        elif row['type'] == "Command":
            function = checkCommand(row['extras'][0], row['extras'][2], parseBool(row['extras'][1]))
        elif row['type'] == "Port":
            function = checkPort(row['extras'][0], parseBool(row['extras'][1]))

        #nil case, can't find what is needed for this element
        if function is None:
            fileError = True
        else:
            #if the new value is different than what it was before...
            if row['complete'] != function:
                changed = True #record and save to file
                row['complete'] = function
                if function == True:
                    title = row['title']
                    if row['mode'] == True:
                        notify("You Earned a Point!", title)
                        new = True #make sound
                    else:
                        penalty = True
                        notify("You Lost Points!", title)
        i = i + 1

    #if one or more of the values is changed, rewrites the recording file with these changes
    if changed:

        try:
            #updates and re-encrypts recording file
            with open(getDirPath() + '/recording', 'w') as recFile:
                encrypt(json.dumps(rows), recFile, "A7jcCd88fl93ndAvy1d8cX0dl")
                recFile.close()

            #save again to be accessed by scoring report html page
            with open('/usr/ScoringEngine/score.json', 'w') as scoreFile:
                newArray = []
                for row in rows:
                    if row['complete'] == True:
                        newArray.append(row)
                scoreFile.write(json.dumps(newArray))
                scoreFile.close()
        except:
            saveError = True
            print "\n * Could not save to file"

#logs time for debugging purposes
try:
    with open(getDirPath() + "/log", "a") as logFile:
        logFile.write('Analyze.py ran at ' + time.strftime("%H:%M:%S") + '\n')
        logFile.close()
except:
    saveError = True
    print "\n * Could not log"

#informs user of any errors, gives steps to resolve
if fileError:
    if saveError:
        print "\nERROR: Some of the item checks failed, and thus cannot be scored.  Please check the output of this command denoted with a *."
    else:
        print "\nERROR: Some of the item checks failed, and thus cannot be scored.  Please check the output of this command denoted with a *. What could be checked has been saved successfully."
if saveError:
    print "ERROR: Could not save properly, please try 'sudo refresh'"

if new: #play sound
    pygame.mixer.music.load("/usr/share/sounds/ubuntu/success.wav")
    pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
    continue
if penalty:
    pygame.mixer.music.load("/usr/share/sounds/ubuntu/error.mp3")
    pygame.mixer.music.play()
#waits until sound is finished playing to end script
while pygame.mixer.music.get_busy():
    continue
