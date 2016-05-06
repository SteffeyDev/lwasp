# Copyright (C) 2015 Peter Steffey

#Needed import statemnts
import os
import string
import json
import time
import sys
import socket
from os.path import expanduser
import getpass
import shutil
import smtplib

from utility import *

print "\nCreating scoring file"

if not internet_on:
    print "Fatal Error: No internet connection, please connect to a network to initialize USELESS."
    sys.exit()

print "\nInstalling inotify-tools and needed python libraries. This may take a minute."
#installs inotifywait to watch files for changes
do("sudo apt-get install inotify-tools python-pygame python-tk -y")

print "\nGenerating front end in /usr/ScoringEngine"
try:
    shutil.move(getSafeDirPath() + "/ScoringEngine", "/usr/ScoringEngine")
except:
    if not os.path.isdir('/usr/ScoringEngine'):
        print ' ** ScoringEngine folder not found, useless folder has been corrupted in transport, please obtain a copy of useless that has the ScoringEngine folder in it.'
        sys.exit()


# source = os.listdir(safeDirpath + "/ScoringEngine/")
# destination = "/usr/ScoringEngine/"
# for files in source:
#     shutil.move(files,destination)

#moves sound to generally accessable system folder
try:
    shutil.move(getSafeDirPath() + "/success.wav", "/usr/share/sounds/ubuntu/success.wav")
    shutil.move(getSafeDirPath() + "/error.mp3", "/usr/share/sounds/ubuntu/error.mp3")
except:
    if not os.path.isfile('/usr/share/sounds/ubuntu/success.wav'):
        print ' ** success.wav file not found, useless folder has been corrupted in transport, please obtain a copy of useless that has the success.wav folder in it.'
        sys.exit()

print "\nCreating Scoring Report on Desktop"
#creates a desktop file to launch a firefox page in its own window, uses logo.png file
with open(expanduser("~") + '/Desktop/scoring.desktop', 'w') as deskFile:
    deskFile.write("[Desktop Entry]\nName=Scoring Report\nExec=firefox /usr/ScoringEngine/ScoringReport.html\nTerminal=false\nType=Application\nIcon=/usr/ScoringEngine/logo.png")
    deskFile.close()
    do("chmod +x ~/Desktop/scoring.desktop") # makes executable
    do("chmod +x open.bash") # makes executable

#creates dictionary object to hold objects
settings = {}
usersettings = {}

try:
    #Open input file and new file
    rawFile = open('elements.csv', 'r')

    print "\nUnloading elements.csv file into recording"
    #loading recording file
    recording = []
    points = 0
    count = 0
    itt = 0
    for line in rawFile.read().replace('\r','').split('\n'): #for each row in the csv
        if line == '' or line.replace(',','') == '':
            continue
        elements = line.split(',') #get all of the elements
        if len(elements) > 4: #if it is a valid line
            dict = {}

            dict['title'] = elements[0]

            mode = elements[1].lower().replace(' ','')

            #checks mode
            if mode != "v" and mode != "p":
                print "\n* Syntax error in the mode of element " + str(itt + 1) + ". Please only use V and P in this column."
                sys.exit()
            dict['mode'] = (mode == "v")

            #checks points
            try:
                dict['points'] = int(elements[2].replace(' ',''))
            except:
                print "\n* Syntax error in the points of element " + str(itt) + ". Please make sure that this is an integer value."
                sys.exit()

            #checks type ** If you add a custum type you should add it here
            type = elements[3].replace(' ', '')
            if not (type == "FileContents" or type == "FileExistance" or type == "Service" or type == "Forensics" or type == "Updates" or type == "Port" or type == "Permissions" or type == "Command"):
                print "\n* Syntax error in the type of element " + str(itt) + ". Please make sure it is one of the 8 valid types."
                sys.exit()
            dict['type'] = elements[3]

            #gets extras, but only valid ones
            extraArray = []
            for element in elements[4:]:
                if element != '\r' and element != '': #makes sure it is a valid element, some csv exports will contain lots of empty fields at the end of lines
                    extraArray.append(element.replace('\r',''))
            dict['extras'] = extraArray
            dict['complete'] = False
            recording.append(dict)

            #gets total to put in settings file
            if dict['mode'] == True:
                points += dict['points']
                count += 1

            itt += 1
        else:
            print "\n* Not enough items in element " + str(itt) + ". Needs 6, only " + str(len(elements))
            sys.exit()

    #settings to use on the scoring report
    usersettings['points'] = points
    usersettings['count'] = count

    #creates and encrypts recording file
    with open(getDirPath() + '/recording', 'w') as writeFile:
        encrypt(json.dumps(recording), writeFile, "A7jcCd88fl93ndAvy1d8cX0dl")
        writeFile.close()

    print "\nDeleting elements.csv"
    do("sudo rm elements.csv")
    rawFile.close()
except:
    if not os.path.isfile('recording'):
        print "\n* Could not find elements.csv file in this directory.  Please see the readme and excel file.  Exiting..."
        sys.exit()

#creates scores file to only store parts of the recording file to show on the scoring html page
with open('/usr/ScoringEngine/score.json', 'w') as scoreFile:
    scoreFile.write("")
    scoreFile.close()

print '\nSetting up script at /etc/init.d/cse.bash to create file watches on boot'
#run restart every time the image restarts to fun cleanup function
bootfile = open('cse','w')
bootfile.write('#!/bin/bash\nsudo /usr/bin/python ' + getSafeDirPath() + '/restart')
bootfile.close()
shutil.move('cse.bash', '/etc/init.d/cse')
do("sudo chmod ugo+x /etc/init.d/cse")
do("sudo ln -s /etc/init.d/cse /etc/rc3.d/S02cse")

if os.path.isfile('/etc/rc6.d/K20cse.bash'):
    os.remove('/etc/rc6.d/K20cse.bash')

#makes sure competitor can't modify code to reveal what is scored
print '\nCompiling python'
if not os.path.isfile('analyze'):
    do("sudo python -O -m py_compile analyze.py")
    os.rename('analyze.pyo', 'analyze')
    os.remove('analyze.py')
if not os.path.isfile('restart'):
    do("sudo python -O -m py_compile restart.py")
    os.rename('restart.pyo', 'restart')
    os.remove('restart.py')
if not os.path.isfile('utility.pyo'):
    do("sudo python -O -m py_compile utility.py")
    os.remove('utility.py')

print '\nAdding cron job to reload the scoring every minute.  You can change the frequency of this by running "sudo crontab -e"'
do("sudo bash cron.bash")

print '\nAdding Set ID script on desktop'
with open(expanduser("~") + '/Desktop/useless.desktop', 'w') as deskFile:
    deskFile.write("[Desktop Entry]\nName=Set ID\nExec=python " + getSafeDirPath() + "/uid.py\nTerminal=false\nType=Application\nIcon=/usr/ScoringEngine/logo.png")
    deskFile.close()
    do("chmod +x ~/Desktop/useless.desktop")
    do("chmod +x " + getSafeDirPath() + "/uid.py")

emailQuestion = ""

relaxing = str(raw_input('\nDo you want this to be a timed image? [y/n]: '))
if relaxing == "y":

    #gets time until image expires
    seconds = 0
    while True:
        secondsStr = raw_input('\nEnter time limit for this image in seconds: ')
        try:
            seconds = int(secondsStr)
            if seconds <= 0:
                print "You must enter a positive integer"
                continue

            response = raw_input('You entered ' + time.strftime('%H', time.gmtime(seconds)) + ' hours, ' + time.strftime('%M', time.gmtime(seconds)) + ' mintues, and ' + time.strftime('%S', time.gmtime(seconds)) + ' seconds, is this correct? [y/n]: ')
            if response == "y":
                break
        except:
            print "Invalid input, please type an integer value"
            continue

    settings['limit'] = seconds
    usersettings['limit'] = seconds
    emailQuestion = '\nDo you want to send the scoring reports to your email automatically when the time is up? [y/n]: '
else:
    settings['limit'] = -1
    usersettings['limit'] = -1
    emailQuestion = '\nDo you want the students to be able to email you the scoring report automatically when they are finished? [y/n]: '

question = str(raw_input(emailQuestion))
if question == "y":

    if settings['limit'] == -1:
        print "Creating Send Scoring Report button on desktop"
        #creates a desktop file to launch a firefox page in its own window, uses logo.png file
        with open(expanduser("~") + '/Desktop/email.desktop', 'w') as deskFile:
            deskFile.write("[Desktop Entry]\nName=Send Scoring Report\nExec=python " + getSafeDirPath() + "/emailz.py\nTerminal=false\nType=Application\nIcon=/usr/ScoringEngine/logo.png")
            deskFile.close()
            do("chmod +x ~/Desktop/email.desktop") # makes executable
    else:
        if os.path.isfile('emailz.py'):
            os.remove('emailz.py')

    #gets email to send scoring report to
    email = ""
    while True:
        email = str(raw_input('\nEnter the email address to send the final scoring report to: '))
        if "@" not in email or len(email) != len(''.join(email.split())):
            print "Please input a valid email address"
            continue
        response = raw_input('You entered "' + email + '", is this correct? [y/n]: ')
        if response == "y":
            break

    settings['email'] = email

    while True:
        #gets email to send scoring report to
        server = ""
        while True:
            server = str(raw_input('\nEnter the SMTP server to send the email from (leave blank to use gmail): '))
            if server == '':
                server = 'smtp.gmail.com'
                break
            else:
                response = raw_input('You entered "' + server + '", is this correct? [y/n]: ')
            if response == "y":
                break
        if server == 'smtp.gmail.com':
            raw_input('\n ** You need to login to your gmail account on a web browser, Click your avatar in the top right corner > My Account > Connected apps & sites > Turn On Allow less secure apps [ok]: ')
        else:
            print '\n ** Make sure to configure your SMTP server to alow this connection.'

        settings['server'] = server

        #gets email to send scoring report to
        username = ""
        while True:
            username = str(raw_input('\nUsername for the SMTP Server (e.g. test.me@gmail.com): '))
            response = raw_input('You entered "' + username + '", is this correct? [y/n]: ')
            if response == "y":
                break

        settings['username'] = username

        #gets email to send scoring report to
        password = ""
        while True:
            password = str(raw_input('\nPassword for the SMTP Server (This will be encrypted): '))
            response = raw_input('You entered "' + password + '", is this correct? [y/n]: ')
            if response == "y":
                break

        settings['password'] = password

        message = "This is a USELESS test email."

        sendEmail(message, settings)

        test = str(raw_input('\nSent a test email to ' + email + '... Did you recieve it? [y/n]: '))
        if test == "y":
            break

        print '\n ** Check the settings on your SMTP account to ensure it did not block the email.  You may want to specify a different SMTP server, visit https://www.arclab.com/en/kb/email/list-of-smtp-and-pop3-servers-mailserver-list.html for a full list'

        restart = str(raw_input('\nDo you want to put in a new SMTP Server? [y/n]: '))
        if restart == "n":
            break
else:
    settings['email'] = 'n/a'
    if os.path.isfile('emailz.py'):
        os.remove('emailz.py')

name = ""
while True:
    name = str(raw_input('\nEnter the common name for this image: '))
    response = raw_input('You entered "' + name + '", is this correct? [y/n]: ')
    if response == "y":
        break

settings['name'] = name
usersettings['name'] = name

#sets initial id as blank
settings['id'] = ""
usersettings['id'] = ""

print '\n* This name will be the same accross all instances of this image.  If this image is duplicated, each user can input their own unique identifier on each image for differentiation'

saveSettings(settings)
saveUserSettings(usersettings)
do("sudo chown " + os.environ['SUDO_USER'] + " settings.json") #sets the file back to being accessable by the normal user, so that we don't have to use sudo on uid.py
do("sudo chown " + os.environ['SUDO_USER'] + " /usr/ScoringEngine/settings.json")

print '\n* Scoring Engine Initialized.  The next time this computer boots up, the timer will start and the scoring engine will be running.\n'
