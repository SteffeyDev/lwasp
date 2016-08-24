#!/usr/bin/env python
# Copyright (C) 2015 Peter Steffey

#Needed import statemnts
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GObject
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

import threading
import time

GObject.threads_init()

#creates dictionary object to hold objects
settings = {}
settings['user'] = os.environ['SUDO_USER']
usersettings = {}
locString = "/etc/lwasp"

class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="LWASP Installer")
        self.set_default_size(800, 600)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        main_box.set_border_width(10)

        self.progress_label = Gtk.Label("Installation Progress")
        self.progress_label.props.halign = Gtk.Align.CENTER
        main_box.pack_end(Gtk.HSeparator(), False, False, 0)
        main_box.pack_end(self.progress_label, False, False, 0)
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

        self.set_icon_from_file(self.get_resource_path("icon.png"))

        self.add(main_box)
        main_box.show_all()

        if not internet_on:
            print "Fatal Error: No internet connection, please connect to a network to initialize LWASP."
            show_error(self, "Error: No internet connection", "Please connect to a network, then try again.")
            Gtk.main_quit()
            sys.exit()

    def get_resource_path(self, rel_path):
        dir_of_py_file = os.path.dirname(__file__)
        rel_path_to_resource = os.path.join(dir_of_py_file, rel_path)
        abs_path_to_resource = os.path.abspath(rel_path_to_resource)
        return abs_path_to_resource

    def update_progress(self, fraction, title):
        self.progress_bar.set_fraction(fraction)
        self.progress_label.set_text("Installation Progress: " + title)

    def install_dependencies(self, button):
        threading.Thread(target=self.install_dependencies_backthread, args=()).start()
        self.content_area.remove(self.welcome_box)
        self.general_setup()

    def install_dependencies_backthread(self):

        GObject.idle_add(lambda: self.update_progress(0.02, "Downloading Content"))

        print "\nInstalling inotify-tools and needed python libraries. This may take a minute."
        #installs inotifywait to watch files for changes
        do("sudo apt-get install inotify-tools python-pygame python-tk python-gtk2 firefox -y --force-yes")

        GObject.idle_add(lambda: self.update_progress(0.1, "Moving Files"))

        self.install_frontend()

    def install_frontend(self):

        print "\nGenerating front end in /usr/lwasp"
        try:
            shutil.move("lwasp-report", "/usr/lwasp")
        except:
            if not os.path.isdir('/usr/lwasp'):
                print ' ** lwasp-report folder not found, lwasp folder has been corrupted in transport, please obtain a copy of lwasp that has the lwasp-report folder in it.'
                show_error(self, 'lwasp-report folder not found', 'lwasp folder has been corrupted in transport, please obtain a copy of lwasp that has the lwasp-report folder in it.')
                Gtk.main_quit()
                sys.exit()

        print "\nCreating Scoring Report on Desktop"
        #creates a desktop file to launch a firefox page in its own window, uses icon.png file
        with open(expanduser("~") + '/Desktop/scoring.desktop', 'w') as deskFile:
            deskFile.write("[Desktop Entry]\nName=Scoring Report\nExec=firefox /usr/lwasp/report.html\nTerminal=false\nType=Application\nIcon=/usr/lwasp/icon.png")
            deskFile.close()
            do("chmod +x ~/Desktop/scoring.desktop") # makes executable
            do("chmod +x open.bash") # makes executable

        print '\nAdding Set ID script on desktop'
        with open(expanduser("~") + '/Desktop/lwasp.desktop', 'w') as deskFile:
            deskFile.write("[Desktop Entry]\nName=Set ID\nExec=python " + locString + "/uid.py\nTerminal=false\nType=Application\nIcon=/usr/lwasp/icon.png")
            deskFile.close()
            do("chmod +x ~/Desktop/lwasp.desktop")
            do("chmod +x " + getSafeDirPath() + "/uid.py")

        GObject.idle_add(lambda: self.update_progress(0.2, "Creating Vulnerabilities"))

        self.install_backend()

    def install_backend(self):

        if os.path.isfile(getDirPath() + '/commands.bash'):
            os.system("/bin/bash " + getDirPath() + "/commands.bash")
            os.remove(getDirPath() + "/commands.bash")
            print "\n vulnerabilities installed"

        #sets up system to use notify-send from root crontab
        do("sudo printf 'env | grep DBUS_SESSION_BUS_ADDRESS > $HOME/.lwasp_dbus\n' >> /home/" + settings['user'] + "/.profile && printf 'export DBUS_SESSION_BUS_ADDRESS >> $HOME/.lwasp_dbus' >> /home/" + settings['user'] + "/.profile")
        do("sudo sed -i.bak s/template/" + settings['user'] + "/g notify.bash && sudo rm notify.bash.bak")

        #moves sound to generally accessable system folder
        try:
            shutil.move(getSafeDirPath() + "/lwasp-sounds", "/usr/share/sounds/lwasp")
        except:
            if not os.path.isfile('/usr/share/sounds/lwasp/success.wav'):
                print ' ** success.wav file not found, lwasp folder has been corrupted in transport, please obtain a copy of lwasp that has the success.wav folder in it.'
                show_error(self, 'Audio files not found', 'lwasp folder has been corrupted in transport, please obtain a copy of lwasp that has the .wav files in it.')
                Gtk.main_quit()
                sys.exit()

        GObject.idle_add(lambda: self.update_progress(0.25, "Analyzing Scoring Elements"))

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

        GObject.idle_add(lambda: self.update_progress(0.3, "Moving Files"))

        #creates scores file to only store parts of the recording file to show on the scoring html page
        with open('/usr/lwasp/score.json', 'w') as scoreFile:
            scoreFile.write("")
            scoreFile.close()
        do("sudo chmod 664 /usr/lwasp/score.json")

        print '\nSetting up script at /etc/init.d/lwasp to create file watches on boot'
        #run restart every time the image restarts to fun cleanup function
        bootfile = open('lwasp','w')
        bootfile.write('#!/bin/sh\ncase "$1" in\nstart)\nsudo /usr/bin/python ' + locString + '/restart\n;;\n*)\n;;\nesac\nexit 0')
        bootfile.close()
        shutil.move('lwasp', '/etc/init.d/lwasp')
        do("sudo chmod ugo+x /etc/init.d/lwasp")
        do("sudo update-rc.d lwasp defaults")

        GObject.idle_add(lambda: self.update_progress(0.4, "Compiling Python"))

        #makes sure competitor can't modify code to reveal what is scored
        print '\nCompiling python'
        if not os.path.isfile('analyze'):
            do("sudo python -m py_compile analyze.py")
            os.rename('analyze.pyc', 'analyze')
            os.remove('analyze.py')
        if not os.path.isfile('restart'):
            do("sudo python -m py_compile restart.py")
            os.rename('restart.pyc', 'restart')
            os.remove('restart.py')
        if not os.path.isfile('utility.pyc'):
            do("sudo python -m py_compile utility.py")
            os.remove('utility.py')

        print '\nAdding cron job to reload the scoring every minute.  You can change the frequency of this by running "sudo crontab -e"'
        do("sudo bash cron.bash")

        GObject.idle_add(lambda: self.update_progress(0.5, "Waiting on User Input"))
        GObject.idle_add(lambda: self.add_next_button())

    def general_setup(self):

        name_box = Gtk.Box(spacing=5)
        name_label = Gtk.Label("Image Common Name: ")
        self.name_entry = Gtk.Entry()
        name_box.pack_start(name_label, False, False, 0)
        name_box.pack_start(self.name_entry, False, False, 0)
        self.content_area.pack_start(name_box, False, False, 0)

        note_label = Gtk.Label()
        note_label.set_markup('<span foreground="grey"><small>The common name will be the same across all instances of this image.  If this image is duplicated, each user can input their own unique identifier on each image for differentiation on the scoring reports.</small></span>')
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
        hbox1 = Gtk.Box(spacing=10)
        hbox2 = Gtk.Box(spacing=20)
        hbox3 = Gtk.Box()
        hbox4 = Gtk.Box(spacing=3)
        self.email_address_entry = Gtk.Entry(placeholder_text="e.g. email@example.com")
        self.email_address_entry.set_width_chars(30)
        hbox1.pack_start(Gtk.Label("Email Address: "), False, False, 0)
        hbox1.pack_start(self.email_address_entry, False, False, 0)
        # self.email_smtp_server_entry = Gtk.Entry(placeholder_text="e.g. smtp.gmail.com")
        # self.email_smtp_server_entry.set_width_chars(30)
        # hbox2.pack_start(Gtk.Label("SMTP Server: "), False, False, 0)
        # hbox2.pack_start(self.email_smtp_server_entry, False, False, 0)
        # self.email_smtp_username_entry = Gtk.Entry(placeholder_text="e.g. example@gmail.com")
        # self.email_smtp_username_entry.set_width_chars(30)
        # hbox3.pack_start(Gtk.Label("SMTP Username: "), False, False, 0)
        # hbox3.pack_start(self.email_smtp_username_entry, False, False, 0)
        # self.email_smtp_password_entry = Gtk.Entry()
        # self.email_smtp_password_entry.set_visibility(False)
        # self.email_smtp_password_entry.set_width_chars(30)
        # hbox4.pack_start(Gtk.Label("SMTP Password: "), False, False, 0)
        # hbox4.pack_start(self.email_smtp_password_entry, False, False, 0)
        self.email_box.pack_start(hbox1, False, False, 0)
        # self.email_box.pack_start(hbox2, False, False, 0)
        # self.email_box.pack_start(hbox3, False, False, 0)
        # self.email_box.pack_start(hbox4, False, False, 0)
        self.email_desktop_button = Gtk.CheckButton("Create Desktop icon to send scoring report")
        self.email_box.pack_start(self.email_desktop_button, False, False, 0)
        note_label_2 = Gtk.Label()
        note_label_2.set_markup('<span foreground="grey"><small>If this is a timed image, scoring reports will be sent automatically when time is up.</small></span>')
        note_label_2.set_line_wrap(True)
        self.content_area.pack_start(note_label, False, False, 0)
        self.email_box.pack_start(note_label_2, False, False, 0)
        self.email_box.pack_end(Gtk.HSeparator(), False, False, 0)

        self.content_area.show_all()

    def add_next_button(self):
        next_box = Gtk.Box(spacing=10)
        self.next_button = Gtk.Button(label="Continue")
        self.next_button.props.halign = Gtk.Align.END
        self.next_button.connect("clicked", self.next_button_pressed)
        next_box.pack_end(self.next_button, False, False, 0)
        self.content_area.pack_end(next_box, False, False, 0)

        self.content_area.show_all()


    def email_button_changed(self, button):
        if button.get_active():
            self.content_area.pack_start(self.email_box, False, False, 0)
            self.content_area.show_all()
        else:
            self.content_area.remove(self.email_box)

    def next_button_pressed(self, button):
        threading.Thread(target=self.next_button_pressed_backthread, args=()).start()

    def next_button_pressed_backthread(self):

        GObject.idle_add(lambda: self.update_progress(0.7, "Processing Input"))

        if self.name_entry.get_text() == "":
            GObject.idle_add(lambda: show_error(self, "Name Needed", "Please enter a Common Name for this image"))
            return

        settings['name'] = self.name_entry.get_text()
        usersettings['name'] = self.name_entry.get_text()

        #sets initial id as blank
        settings['id'] = ""
        usersettings['id'] = ""

        if self.time_check_button.get_active():
            if self.time_check_entry.get_text() == "":
                GObject.idle_add(lambda: show_error(self, "Time Needed", "Please enter a time or deselect the Timed Image option"))
                return
            try:
                hours = int(self.time_check_entry.get_text().split(":")[0])
                minutes = int(self.time_check_entry.get_text().split(":")[1])
                seconds = (hours * 3600) + (minutes * 60)
                settings['limit'] = seconds
                usersettings['limit'] = seconds
            except:
                GObject.idle_add(lambda: show_error(self, "Invalid Time", "Please enter a time value in the correct format"))
                return
        else:
            settings['limit'] = -1
            usersettings['limit'] = -1

        if self.email_button.get_active():
            if self.email_address_entry.get_text() == "" or self.email_smtp_server_entry.get_text() == "" or self.email_smtp_username_entry.get_text() == "" or self.email_smtp_password_entry.get_text() == "":
                GObject.idle_add(lambda: show_error(self, "Email Information Needed", "Please fill out all of the email information fields or deselect the Sending Scoring Reports Over Email checkbox"))
                return
            settings['email'] = self.email_address_entry.get_text()
            settings['server'] = 'smtp.sendgrid.com' #self.email_smtp_server_entry.get_text()
            settings['username'] = 'lwasp' #self.email_smtp_username_entry.get_text()
            settings['password'] = 'kw4-SCt-sts-eqS' #self.email_smtp_password_entry.get_text()

            #if settings['server'] == "smtp.gmail.com":
            #    GObject.idle_add(lambda: show_error(self, "Gmail SMTP Setup", 'You need to login to your gmail account on a web browser, Click your avatar in the top right corner > My Account > Connected apps & sites > Turn On Allow less secure apps', Gtk.MessageType.INFO))
            if self.email_desktop_button.get_active():
                print "Creating Send Scoring Report button on desktop"
                #creates a desktop file to launch a firefox page in its own window, uses icon.png file
                with open(expanduser("~") + '/Desktop/email.desktop', 'w') as deskFile:
                    deskFile.write("[Desktop Entry]\nName=Send Scoring Report\nExec=python " + locString + "/emailz.py\nTerminal=false\nType=Application\nIcon=/usr/lwasp/icon.png")
                    deskFile.close()
                    do("chmod +x ~/Desktop/email.desktop") # makes executable
            message = "This is an LWASP test email. It is intentionally blank. Please continue configuring your image."
            sendEmail(message, settings)

            GObject.idle_add(lambda: self.update_progress(0.8, "Waiting on User Input"))
            GObject.idle_add(lambda: self.launch_email_check_dialog())

        else:
            settings['email'] = 'n/a'
            if os.path.isfile('emailz.py'):
                os.remove('emailz.py')
            self.finish_installation()

    def launch_email_check_dialog(self):
        self.check_dialog = Gtk.Dialog("Email Confirmation", self, 0)
        self.check_dialog.set_default_size(200, 100)
        vbox = self.check_dialog.get_content_area()
        email_label = Gtk.Label("A test email was sent to " + settings['email'] + " using these SMTP server settings, please confirm whether or not you recieved this email.")
        email_label.set_line_wrap(True)
        vbox.pack_start(email_label, False, False, 0)
        vbox.pack_start(Gtk.HSeparator(), False, False, 0)
        vbox.props.spacing = 6

        recieved_button = Gtk.Button(label="Email Recieved")
        recieved_button.connect("clicked", self.finish_installation)
        vbox.pack_start(recieved_button, False, False, 0)

        not_recieved_button = Gtk.Button(label="Email NOT Recieved")
        not_recieved_button.connect("clicked", self.email_not_recieved)
        vbox.pack_start(not_recieved_button, False, False, 0)
        vbox.set_border_width(10)
        vbox.show_all()

        self.check_dialog.set_modal(True)
        self.check_dialog.run()

    def email_not_recieved(self, button):
        self.check_dialog.destroy()
        show_error(self, "Check SMTP Settings", "Check the settings on your SMTP account to ensure it did not block the email.  You may want to specify a different SMTP server, visit https://www.arclab.com/en/kb/email/list-of-smtp-and-pop3-servers-mailserver-list.html for a full list", Gtk.MessageType.INFO)

    def finish_installation(self, button=None):
        try:
            self.check_dialog.destroy()
        except:
            h = "ignore"
        self.update_progress(0.9, "Finishing Up")
        threading.Thread(target=self.finish_installation_backthread, args=()).start()

    def finish_installation_backthread(self):

        user = settings['user'];

        saveSettings(settings)
        saveUserSettings(usersettings)
        do("sudo chown " + user + " settings.json") #sets the file back to being accessable by the normal user, so that we don't have to use sudo on uid.py
        do("sudo chown " + user + " /usr/lwasp/settings.json")

        print "\nDeleting Bash History"
        do("sudo -u " + user + " bash -c 'history -c; echo '' > ~/.bash_history'")

        print "\nDeleting Authentication Logs"
        do("sudo chmod 664 /var/log/auth.log; sudo echo '' > /var/log/auth.log; sudo chmod 640 /var/log/auth.log")

        print "\nRemoving Unused backdoors"
        shutil.rmtree('backdoors')

        print "\nMoving this folder to " + locString
        shutil.move(getSafeDirPath(), locString)

        print "\nDeleting all other files"
        do("sudo rm -rf " + '/'.join(getDirPath().split("/")[0:len(getDirPath().split("/"))-1]))

        GObject.idle_add(lambda: self.update_progress(1, "Done"))
        GObject.idle_add(lambda: self.finish())

    def finish(self):

        show_error(self, "Scoring Engine Initialized", "Please shut down the image now by running \'sudo poweroff\'. The next time this computer boots up, the timer will start (if used) and the scoring engine will be running.", Gtk.MessageType.INFO)
        Gtk.main_quit()
        sys.exit()
        print "exited"

win = MyWindow()
win.connect('delete-event', Gtk.main_quit)
win.show_all()
Gtk.main()
