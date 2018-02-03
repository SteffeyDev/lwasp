# Copyright (C) 2015 Peter Steffey

import os.path
import time
import string
import os
import datetime
import json
import sys
import re
import smtplib
import traceback

from utility import *

# Fetch modules
modulesImports = [__import__('modules.' + moduleName.split('.')[0], fromlist=["modules"]) for moduleName in os.listdir('modules')]
moduleNames = [moduleName.split('.')[0] for moduleName in os.listdir('modules')]
modules = dict(zip(moduleNames, modulesImports))

debug = (len(sys.argv) == 2 and sys.argv[1] == "debug")

# Tracks errors to show messages at end
fileError = False
saveError = False

if os.path.isfile('/etc/lwasp/holder'):
    print "\n * analyze already running, exiting...\n"
    sys.exit()

file = open(getDirPath() + '/holder','w')
file.close()

#to send scoring report at end
def send_email(settings):
    try:
        sendScoringReport()
        print '\n* Time is up! Scoring report has been sent to the Administrator; exiting script now...\n'
    except:
        print '\n* Time is up! Exiting script now...\n'

    # Prevents email from being sent more than once
    addSetting('email', 'done', True, False)

    sys.exit()

# Load the settings dictionary from the encrypted file
settings = getSettings()

# If the administrator made this a timed image
if settings['limit'] != -1:

    # Get the current time string in seconds
    now = datetime.datetime.now()

    # If the email has already been sent, inform the user and get out of here
    if settings['email'] == 'done':
        print '\n* Time is up! Scoring report has been sent to the Administrator; exiting script now...\n'
        sys.exit()

    timeNow = (now.hour * 3600) + (now.minute * 60) + (now.second)
    timeStart = settings['start']
    timeLimit = settings['limit']

    # If time is up, inform user and send email to coach/mentor
    if timeNow - timeStart > timeLimit:
        notify("Out of Time!", "Your score is frozen.  Please stop working and back away from this image.  It may explode.")

        if settings['email'] == 'n/a':
            print '\n* Time is up! Exiting script now...\n'
            sys.exit()

        # Prevents the email from being sent multiple times
        send_email(settings)

changed = False
new = False
penalty = False

with open(getDirPath() + '/recording', 'r') as readFile:
    text = decrypt(readFile)#, "A7jcCd88fl93ndAvy1d8cX0dl")
    rows = json.loads(text)

    # For each line in the recording file
    i = 0
    for row in rows:
        print "Checking element " + str(i+1)

        try:
            returnVal = modules[row['type']].check(row['extras'], debug)

            # If the new value is different than what it was before...
            if row['complete'] != returnVal:
                changed = True #record and save to file
                row['complete'] = returnVal
                if returnVal == True:
                    title = row['title']
                    if row['mode'] == True:
                        notify("You Earned a Point!", title)
                        new = True #make sound
                    else:
                        penalty = True
                        notify("You Lost Points!", title)

        except TypeError:
            if debug:
                print "Not enough extras in row ", str(i+1)

        except:
            if debug:
                print "Unexpected error of " + str(sys.exc_info()[0]) + ":", traceback.format_exc()
            print " * Could not execute command.  Please contact your administrator"
            fileError = True
            
        i = i + 1

    readFile.close()
    # If one or more of the values is changed, rewrites the recording file with these changes
    if changed:

        try:
            # Updates and re-encrypts recording file
            with open(getDirPath() + '/recording', 'w') as recFile:
                encrypt(json.dumps(rows), recFile)

            # Save again to be accessed by scoring report html page
            with open('/usr/lwasp/score.json', 'w') as scoreFile:
                newArray = []
                for row in rows:
                    if row['complete'] == True:
                        newObj = {'title': row['title'], 'points': row['points'], 'mode': row['mode']}
                        newArray.append(newObj)
                masterObj = {'score': newArray}
                scoreFile.write(json.dumps(masterObj))
                scoreFile.close()
            try:
                do("sudo chown " + settings['user'] + "/usr/lwasp/score.json")
            except:
                print "* Could not own score.json"
        except:
            saveError = True
            print "\n * Could not save to file"

# Logs time for debugging purposes
try:
    with open(getDirPath() + "/log", "a") as logFile:
        logFile.write('Analyze.py ran at ' + time.strftime("%H:%M:%S") + '\n')
        logFile.close()
except:
    saveError = True
    print "\n * Could not log"

# Informs user of any errors, gives steps to resolve
if fileError:
    if saveError:
        print "\nWARNING: Some of the item checks failed, and thus cannot be scored.  Please check the output of this command denoted with a *."
    else:
        print "\nWARNING: Some of the item checks failed, and thus cannot be scored.  Please check the output of this command denoted with a *. What could be checked has been saved successfully."
if saveError:
    print "ERROR: Could not save properly, please try 'sudo refresh'"

if new and penalty:
    playSound('both')
elif new:
    playSound('new')
elif penalty:
    playSound('penalty')

os.remove(getSafeDirPath() + '/holder')
