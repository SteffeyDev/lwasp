#!/usr/bin/env python
# Copyright (C) 2015 Peter Steffey

#Needed import statemnts
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
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

os.chdir(getDirPath())

def show_error(top, title, message, type=Gtk.MessageType.ERROR):
    dialog = Gtk.MessageDialog(top, 0, type, Gtk.ButtonsType.OK, title)
    dialog.format_secondary_text(message)
    dialog.set_modal(True)
    dialog.run()
    dialog.destroy()

#creates dictionary object to hold objects
settings = {}
usersettings = {}
locString = "/etc"

class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="LWASP Installer")
        self.set_default_size(800, 600)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        main_box.set_border_width(10)

        label = Gtk.Label("Installation Progress")
        label.props.halign = Gtk.Align.CENTER
        main_box.pack_end(Gtk.HSeparator(), False, False, 0)
        main_box.pack_end(label, False, False, 0)
        self.progress_bar = Gtk.ProgressBar()
        main_box.pack_end(self.progress_bar, False, False, 0)
        main_box.pack_end(Gtk.HSeparator(), False, False, 0)

        self.content_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.content_area.set_border_width(5)
        main_box.pack_start(self.content_area, True, True, 0)

        self.welcome_box = Gtk.Box(spacing=5, orientation=Gtk.Orientation.VERTICAL)
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale('icon.png', width=200, height=200, preserve_aspect_ratio=False)
        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf)
        self.welcome_box.pack_start(image, False, False, 0)
        internal_box = Gtk.Box(spacing=5)
        internal_box.pack_start(Gtk.Label("Thanks for using LWASP! Click here to get started: "), False, False, 0)
        get_started_button = Gtk.Button("Install")
        get_started_button.connect("clicked", self.install_dependencies)
        internal_box.pack_start(get_started_button, False, False, 0)
        internal_box.props.halign = Gtk.Align.CENTER
        self.welcome_box.pack_start(internal_box, False, False, 0)
        self.welcome_box.props.valign = Gtk.Align.CENTER
        self.content_area.pack_start(self.welcome_box, True, True, 0)

        self.add(main_box)
        main_box.show_all()

        if not internet_on:
            print "Fatal Error: No internet connection, please connect to a network to initialize LWASP."
            show_error(self, "Error: No internet connection", "Please connect to a network, then try again.")
            Gtk.main_quit()
            sys.exit()

    def install_dependencies(self, button):

        self.content_area.remove(self.welcome_box)

        hbox = Gtk.Box()
        spinner = Gtk.Spinner()
        label = Gtk.Label("Installing inotify-tools and needed python libraries. This may take a minute.")
        hbox.add(spinner)
        hbox.add(label)
        self.content_area.add(hbox)

        self.content_area.show_all()

        print "\nInstalling inotify-tools and needed python libraries. This may take a minute."
        #installs inotifywait to watch files for changes
        do("sudo apt-get install inotify-tools python-pygame python-tk python-gtk2 firefox -y")

        self.content_area.remove(hbox)

        self.progress_bar.set_fraction(0.1)

        self.install_frontend()

    def install_frontend(self):

        print "\nGenerating front end in /usr/ScoringEngine"
        try:
            shutil.move("ScoringEngine", "/usr/ScoringEngine")
        except:
            if not os.path.isdir('/usr/ScoringEngine'):
                print ' ** ScoringEngine folder not found, lwasp folder has been corrupted in transport, please obtain a copy of lwasp that has the ScoringEngine folder in it.'
                show_error(self, 'ScoringEngine folder not found', 'lwasp folder has been corrupted in transport, please obtain a copy of lwasp that has the ScoringEngine folder in it.')
                Gtk.main_quit()
                sys.exit()

        print "\nCreating Scoring Report on Desktop"
        #creates a desktop file to launch a firefox page in its own window, uses logo.png file
        with open(expanduser("~") + '/Desktop/scoring.desktop', 'w') as deskFile:
            deskFile.write("[Desktop Entry]\nName=Scoring Report\nExec=firefox /usr/ScoringEngine/ScoringReport.html\nTerminal=false\nType=Application\nIcon=/usr/ScoringEngine/logo.png")
            deskFile.close()
            do("chmod +x ~/Desktop/scoring.desktop") # makes executable
            do("chmod +x open.bash") # makes executable

        print '\nAdding Set ID script on desktop'
        with open(expanduser("~") + '/Desktop/lwasp.desktop', 'w') as deskFile:
            deskFile.write("[Desktop Entry]\nName=Set ID\nExec=python " + locString + "/lwasp/uid.py\nTerminal=false\nType=Application\nIcon=/usr/ScoringEngine/logo.png")
            deskFile.close()
            do("chmod +x ~/Desktop/lwasp.desktop")
            do("chmod +x " + getSafeDirPath() + "/uid.py")

        self.progress_bar.set_fraction(0.2)

        self.install_backend()

    def install_backend(self):

        #moves sound to generally accessable system folder
        try:
            os.mkdir("/usr/share/sounds/lwasp")
            shutil.move(getSafeDirPath() + "/success.wav", "/usr/share/sounds/lwasp/success.wav")
            shutil.move(getSafeDirPath() + "/error.mp3", "/usr/share/sounds/lwasp/error.mp3")
        except:
            if not os.path.isfile('/usr/share/sounds/lwasp/success.wav'):
                print ' ** success.wav file not found, lwasp folder has been corrupted in transport, please obtain a copy of lwasp that has the success.wav folder in it.'
                show_error(self, 'Audio files not found', 'lwasp folder has been corrupted in transport, please obtain a copy of lwasp that has the .wav files in it.')
                Gtk.main_quit()
                sys.exit()

        self.progress_bar.set_fraction(0.23)

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
                        Gtk.main_quit()
                        sys.exit()
                    dict['mode'] = (mode == "v")

                    #checks points
                    try:
                        dict['points'] = int(elements[2].replace(' ',''))
                    except:
                        print "\n* Syntax error in the points of element " + str(itt) + ". Please make sure that this is an integer value."
                        Gtk.main_quit()
                        sys.exit()

                    #checks type ** If you add a custum type you should add it here
                    type = elements[3].replace(' ', '')
                    if not (type == "FileContents" or type == "FileExistance" or type == "Service" or type == "Forensics" or type == "Updates" or type == "Port" or type == "Permissions" or type == "Command"):
                        print "\n* Syntax error in the type of element " + str(itt) + ". Please make sure it is one of the 8 valid types."
                        Gtk.main_quit()
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
                    Gtk.main_quit()
                    sys.exit()

            #settings to use on the scoring report
            usersettings['points'] = points
            usersettings['count'] = count

            #creates and encrypts recording file
            with open('recording', 'w') as writeFile:
                encrypt(json.dumps(recording), writeFile)#, "A7jcCd88fl93ndAvy1d8cX0dl")
                #writeFile.close()

            print "\nDeleting elements.csv"
            do("sudo rm elements.csv")
            rawFile.close()
        except:
            if not os.path.isfile('recording'):
                print "\n* Could not find elements.csv file in this directory.  Please see the readme and excel file.  Exiting..."
                show_error(self, "Could not find elements.csv file","Please run the lwasp-setup script before this one.")
                Gtk.main_quit()
                sys.exit()

        self.progress_bar.set_fraction(0.3)

        #creates scores file to only store parts of the recording file to show on the scoring html page
        with open('/usr/ScoringEngine/score.json', 'w') as scoreFile:
            scoreFile.write("")
            scoreFile.close()

        print '\nSetting up script at /etc/init.d/lwasp to create file watches on boot'
        #run restart every time the image restarts to fun cleanup function
        bootfile = open('lwasp','w')
        bootfile.write('#!/bin/sh\ncase "$1" in\nstart)\nsudo /usr/bin/python ' + locString + '/lwasp/restart\n;;\n*)\n;;\nesac\nexit 0')
        bootfile.close()
        shutil.move('lwasp', '/etc/init.d/lwasp')
        do("sudo chmod ugo+x /etc/init.d/lwasp")
        do("sudo update-rc.d lwasp defaults")

        self.progress_bar.set_fraction(0.4)

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

        self.progress_bar.set_fraction(0.5)

        self.general_setup()


    def general_setup(self):

        name_box = Gtk.Box(spacing=5)
        name_label = Gtk.Label("Image Common Name: ")
        self.name_entry = Gtk.Entry()
        name_box.pack_start(name_label, False, False, 0)
        name_box.pack_start(self.name_entry, False, False, 0)
        self.content_area.pack_start(name_box, False, False, 0)

        note_label = Gtk.Label()
        note_label.set_markup('<span foreground="grey"><small>The common name will be the same accross all instances of this image.  If this image is duplicated, each user can input their own unique identifier on each image for differentiation on the scoring reports.</small></span>')
        note_label.set_line_wrap(True)
        self.content_area.pack_start(note_label, False, False, 0)

        self.content_area.pack_start(Gtk.HSeparator(), False, False, 0)

        time_box = Gtk.Box(spacing=5)
        self.time_check_button = Gtk.CheckButton("Timed Image")
        self.time_check_entry = Gtk.Entry(placeholder_text="hh:mm")
        time_box.pack_start(self.time_check_button, False, False, 0)
        time_box.pack_start(self.time_check_entry, False, False, 0)
        self.content_area.pack_start(time_box, False, False, 0)

        self.content_area.pack_start(Gtk.HSeparator(), False, False, 0)

        self.email_button = Gtk.CheckButton("Setup sending scoring reports over email")
        self.email_button.connect("clicked", self.email_button_changed)
        self.content_area.pack_start(self.email_button, False, False, 0)
        self.email_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        hbox1 = Gtk.Box(spacing=8)
        hbox2 = Gtk.Box(spacing=15)
        hbox3 = Gtk.Box()
        hbox4 = Gtk.Box(spacing=4)
        self.email_address_entry = Gtk.Entry(placeholder_text="e.g. email@example.com")
        self.email_address_entry.set_width_chars(30)
        hbox1.pack_start(Gtk.Label("Email Address: "), False, False, 0)
        hbox1.pack_start(self.email_address_entry, False, False, 0)
        self.email_smtp_server_entry = Gtk.Entry(placeholder_text="e.g. smtp.gmail.com")
        self.email_smtp_server_entry.set_width_chars(30)
        hbox2.pack_start(Gtk.Label("SMTP Server: "), False, False, 0)
        hbox2.pack_start(self.email_smtp_server_entry, False, False, 0)
        self.email_smtp_username_entry = Gtk.Entry(placeholder_text="e.g. example@gmail.com")
        self.email_smtp_username_entry.set_width_chars(30)
        hbox3.pack_start(Gtk.Label("SMTP Username: "), False, False, 0)
        hbox3.pack_start(self.email_smtp_username_entry, False, False, 0)
        self.email_smtp_password_entry = Gtk.Entry()
        self.email_smtp_password_entry.set_visibility(False)
        self.email_smtp_password_entry.set_width_chars(30)
        hbox4.pack_start(Gtk.Label("SMTP Password: "), False, False, 0)
        hbox4.pack_start(self.email_smtp_password_entry, False, False, 0)
        self.email_box.pack_start(hbox1, False, False, 0)
        self.email_box.pack_start(hbox2, False, False, 0)
        self.email_box.pack_start(hbox3, False, False, 0)
        self.email_box.pack_start(hbox4, False, False, 0)
        self.email_desktop_button = Gtk.CheckButton("Create Desktop icon to send scoring report")
        self.email_box.pack_start(self.email_desktop_button, False, False, 0)
        note_label_2 = Gtk.Label()
        note_label_2.set_markup('<span foreground="grey"><small>If this is a timed image, scoring reports will be sent automatically when time is up.</small></span>')
        note_label_2.set_line_wrap(True)
        self.content_area.pack_start(note_label, False, False, 0)
        self.email_box.pack_start(note_label_2, False, False, 0)
        self.email_box.pack_end(Gtk.HSeparator(), False, False, 0)

        next_box = Gtk.Box(spacing=10)
        next_button = Gtk.Button(label="Continue")
        next_button.props.halign = Gtk.Align.END
        next_button.connect("clicked", self.next_button_pressed)
        next_box.pack_end(next_button, False, False, 0)
        self.content_area.pack_end(next_box, False, False, 0)

        self.content_area.show_all()

    def email_button_changed(self, button):
        if button.get_active():
            self.content_area.pack_start(self.email_box, False, False, 0)
            self.content_area.show_all()
        else:
            self.content_area.remove(self.email_box)

    def next_button_pressed(self, button):

        self.progress_bar.set_fraction(0.7)

        if self.name_entry.get_text() == "":
            show_error(self, "Name Needed", "Please enter a Common Name for this image")
            return

        settings['name'] = self.name_entry.get_text()
        usersettings['name'] = self.name_entry.get_text()

        #sets initial id as blank
        settings['id'] = ""
        usersettings['id'] = ""

        if self.time_check_button.get_active():
            if self.time_check_entry.get_text() == "":
                show_error(self, "Time Needed", "Please enter a time or deselect the Timed Image option")
                return
            try:
                hours = int(self.time_check_entry.get_text().split(":")[0])
                minutes = int(self.time_check_entry.get_text().split(":")[1])
                seconds = (hours * 3600) + (minutes * 60)
                settings['limit'] = seconds
                usersettings['limit'] = seconds
            except:
                show_error(self, "Invalid Time", "Please enter a time value in the correct format")
                return
        else:
            settings['limit'] = -1
            usersettings['limit'] = -1

        if self.email_button.get_active():
            if self.email_address_entry.get_text() == "" or self.email_smtp_server_entry.get_text() == "" or self.email_smtp_username_entry.get_text() == "" or self.email_smtp_password_entry.get_text() == "":
                show_error(self, "Email Information Needed", "Please fill out all of the email information fields or deselect the Sending Scoring Reports Over Email checkbox")
                return
            settings['email'] = self.email_address_entry.get_text()
            settings['server'] = self.email_smtp_server_entry.get_text()
            settings['username'] = self.email_smtp_username_entry.get_text()
            settings['password'] = self.email_smtp_password_entry.get_text()

            if settings['server'] == "smtp.gmail.com":
                show_error(self, "Gmail SMTP Setup", 'You need to login to your gmail account on a web browser, Click your avatar in the top right corner > My Account > Connected apps & sites > Turn On Allow less secure apps', Gtk.MessageType.INFO)
            if self.email_desktop_button.get_active():
                print "Creating Send Scoring Report button on desktop"
                #creates a desktop file to launch a firefox page in its own window, uses logo.png file
                with open(expanduser("~") + '/Desktop/email.desktop', 'w') as deskFile:
                    deskFile.write("[Desktop Entry]\nName=Send Scoring Report\nExec=python " + locString + "/lwasp/emailz.py\nTerminal=false\nType=Application\nIcon=/usr/ScoringEngine/logo.png")
                    deskFile.close()
                    do("chmod +x ~/Desktop/email.desktop") # makes executable
            message = "This is an LWASP test email. It is intentionally blank. Please continue configuring your image."
            sendEmail(message, settings)

            self.progress_bar.set_fraction(0.8)

            check_dialog = Gtk.Dialog("Email Confirmation", self, 0)
            check_dialog.set_default_size(200, 100)
            vbox = check_dialog.get_content_area()
            email_label = Gtk.Label("A test email was sent to " + settings['email'] + " using these SMTP server settings, please confirm whether or not you recieved this email.")
            email_label.set_line_wrap(True)
            vbox.pack_start(email_label, False, False, 0)
            vbox.pack_start(Gtk.HSeparator(), False, False, 0)

            recieved_button = Gtk.Button(label="Email Recieved")
            recieved_button.connect("clicked", self.finish_installation)
            vbox.pack_start(recieved_button, False, False, 0)

            not_recieved_button = Gtk.Button(label="Email NOT Recieved")
            not_recieved_button.connect("clicked", self.email_not_recieved)
            vbox.pack_start(not_recieved_button, False, False, 0)
            vbox.set_border_width(10)
            vbox.show_all()

            check_dialog.set_modal(True)
            check_dialog.run()

            self.check_dialog = check_dialog
        else:
            settings['email'] = 'n/a'
            if os.path.isfile('emailz.py'):
                os.remove('emailz.py')
            self.finish_installation()

    def email_not_recieved(self, button):
        self.check_dialog.destroy()
        show_error(self, "Check SMTP Settings", "Check the settings on your SMTP account to ensure it did not block the email.  You may want to specify a different SMTP server, visit https://www.arclab.com/en/kb/email/list-of-smtp-and-pop3-servers-mailserver-list.html for a full list", Gtk.MessageType.INFO)

    def finish_installation(self, button=None):
        try:
            self.check_dialog.destroy()
        except:
            h = "ignore"
        self.progress_bar.set_fraction(0.9)

        saveSettings(settings)
        saveUserSettings(usersettings)
        do("sudo chown " + os.environ['SUDO_USER'] + " settings.json") #sets the file back to being accessable by the normal user, so that we don't have to use sudo on uid.py
        do("sudo chown " + os.environ['SUDO_USER'] + " /usr/ScoringEngine/settings.json")

        user = os.environ['SUDO_USER'];
        print "\nDeleting Bash History"
        do("sudo -u " + user + " bash -c 'history -c; echo \"\" > ~/.bash_history'")

        print "\nMoving this folder to " + locString
        shutil.move(getSafeDirPath(), locString)

        self.progress_bar.set_fraction(1)

        show_error(self, "Scoring Engine Initialized", "Please shut down the image now by running \'sudo poweroff\'. The next time this computer boots up, the timer will start (if used) and the scoring engine will be running.", Gtk.MessageType.INFO)
        Gtk.main_quit()
        sys.exit()
        print "exited"

win = MyWindow()
win.connect('delete-event', Gtk.main_quit)
win.show_all()
Gtk.main()
