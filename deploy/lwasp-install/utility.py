# Copyright (C) 2015 Peter Steffey

from hashlib import md5
import subprocess, os, string, smtplib, json, urllib2, re, commands, sys
from os import path

#Function to run a bash command
def do(cmd):
    p = subprocess.Popen(cmd , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()

try:
    from Crypto.Cipher import AES
    from Crypto import Random
except:
    print "\nInstalling python-crypto library..."
    do('sudo apt-get install python-crypto -y')
    from Crypto.Cipher import AES
    from Crypto import Random

try:
    import pygame
except:
    print "pygame not installed"

def internet_on():
    try:
        response=urllib2.urlopen('http://74.125.228.100',timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False

def saveSettings(settings):
    with open(getDirPath() + '/settings.json', 'w') as setFile:
        text = json.dumps(settings)
        encrypt(text, setFile)
        setFile.close()
    do('sudo chown ' + settings['user'] + ' /etc/lwasp/settings.json')


def saveUserSettings(settings):
    text = json.dumps(settings)
    with open('/usr/lwasp/settings.json', 'w') as userWriteFile:
        userWriteFile.write(text)
        userWriteFile.close()
    settings = getSettings()
    do('sudo chown ' + settings['user'] + ' /usr/lwasp/settings.json')

def getSettings():
    setFile = open(getDirPath() + '/settings.json', 'r')
    text = json.loads(decrypt(setFile))#, "f8R843nF9d1nXEoIz7D01mE"))
    setFile.close()
    return text

def getUserSettings():
    setFile = open('/usr/lwasp/settings.json', 'r')
    text = json.loads(setFile.read())
    setFile.close()
    return text

def addSetting(key, setting, etc, usr):
    if etc:
        settings = getSettings()
        settings[key] = setting
        saveSettings(settings)
    if usr:
        settings = getUserSettings()
        settings[key] = setting
        saveUserSettings(settings)

def derive_key_and_iv(password, salt, key_length, iv_length):
    d = d_i = ''
    while len(d) < key_length + iv_length:
        d_i = md5(d_i + password + salt).digest()
        d += d_i
    return d[:key_length], d[key_length:key_length+iv_length]

def decrypt(in_file):#, password, key_length=32):
    obj = AES.new("2Ad8fj3HdF83jD8f", AES.MODE_CFB, 'nC8eiOsx10J8dshI')
    return obj.decrypt(in_file.read())

def encrypt(in_text, out_file):#, password, key_length=32):
    obj = AES.new("2Ad8fj3HdF83jD8f", AES.MODE_CFB, 'nC8eiOsx10J8dshI')
    out_file.write(obj.encrypt(in_text))
    out_file.close()

#gets path to current directory for using in the open command
def getDirPath():
    return os.path.dirname(os.path.realpath(__file__))

#gets path to current directory for using in bash do commands
def getSafeDirPath():
    return getDirPath().replace(" ", "\\ ")

def getIP():
    #get ip addresses on system, store in settings, check each time computer restarts in case changes
    found_ips = []
    ips = re.findall( r'[0-9]+(?:\.[0-9]+){3}', commands.getoutput("/sbin/ifconfig"))
    for ip in ips:
        if ip.startswith("255") or ip.startswith("127") or ip.endswith("255"):
            continue
        found_ips.append(ip)

    return found_ips[0]

#emails scoring report, either automatically or by the program on the desktop
def sendScoringReport():

    settings = getSettings()

    message = 'Here is the report for the team <b>' + settings['id'] + '</b> using the image <b>' + settings['name'] + '</b> with the IP address <b>' + str(getIP()) + '</b>.<br><br>'

    pointsTotal = 0
    pointsGained = 0
    points = 0
    completeArray = []
    missedArray = []
    penaltiesLostArray = []
    penaltiesArray = []
    penaltyPoint = 0
    with open(getDirPath() + '/recording', 'r') as readFile:
        text = decrypt(readFile)#, "A7jcCd88fl93ndAvy1d8cX0dl")
        rows = json.loads(text)
        for row in rows:
            if row['mode'] == True:
                pointsTotal += row['points']
                if row['complete'] == True:
                    completeArray.append(row['title'] + ' - ' + str(row['points']) + 'pts<br>')
                    pointsGained += row['points']
                    points += row['points']
                else:
                    missedArray.append(row['title'] + ' - ' + str(row['points']) + 'pts<br>')
            else:
                if row['complete'] == True:
                    penaltiesLostArray.append(row['title'] + ' - ' + str(row['points']) + 'pts<br>')
                    points -= row['points']
                    penaltyPoint += row['points']
                else:
                    penaltiesArray.append(row['title'] + ' - ' + str(row['points']) + 'pts<br>')
    message += 'Points Total: ' + str(points) + ' out of ' + str(pointsTotal) + '<br>'
    message += '<br>Points Gained: ' + str(pointsGained) + '<br>'
    for element in completeArray:
        message += element
    message += '<br>Points Missed: ' + str(pointsTotal - pointsGained) + '<br>'
    for element in missedArray:
        message += element
    message += '<br>Points lost through penalties: ' + str(penaltyPoint) + '<br>'
    for element in penaltiesLostArray:
        message += element
    message += '<br>Penalties not triggered:<br>'
    for element in penaltiesArray:
        message += element

    message += '<br>Generated by LWASP, the Linux Watchful Adaptable Security Profiler<br>Built by MIDN Peter Steffey<br>Email <a href="mailto:contact@nsccmanager.com">contact@nsccmanager.com</a> with questions, comments, and suggestions<br>If you are in the NSCC program, visit <a href="http://www.nsccmanager.com">NSCCManager.com</a> to explore the future of personnel management'

    return sendEmail(message)

#sends any email given the message and the email the administrator supplied
def sendEmail(message, settings={}):

    if len(settings) == 0:
        settings = getSettings()

    if settings['email'] == 'done':
        return False

    server = settings['server']
    server_port = '587'

    username = settings['username']
    password = settings['password']
    email = settings['email']

    headers = ["From: " + username + "@sendgrid.net", "To: " + email, "MIME-Version: 1.0", "Subject: LWASP Scoring Report", "Content-Type: text/html"]
    headers = "\r\n".join(headers)

    try:
        server = smtplib.SMTP(server + ':' + server_port)
        server.ehlo()

        # If we can encrypt this session, do it
        if server.has_extn('STARTTLS'):
            server.starttls()
            server.ehlo() # re-identify ourselves over TLS connection

        server.login(username, password)
        server.sendmail(username, email, headers + "\r\n\r\n" + message)
        server.quit()
    except smtplib.SMTPException as error:
        print "Error: unable to send email :  {err}".format(err=error)

    return True

#Sends notification on screen to show user
def notify(title, message):
    settings = getSettings()
    #do('sudo -u ' + settings['user'] + ' /etc/lwasp/notify.bash "' + title + '" "' + message + '"')
    do('notify-send -u critical "' + title + '" "' + message + '"')

#Sets up an inotifywait on the file passed in to call analyze.py on file change, delete, etc
def watch(filepath):
    do("while true; do sudo inotifywait -e modify,close_write,moved_to,create,delete " + filepath + " && sudo python /etc/lwasp/analyze; done &")

def encode(thing):
    textStr = "{"
    i = 0
    for key, value in thing.iteritems():
        print key
        if i != 0:
            textStr += ","
        textStr += "\"" + key + "\":"
        if type(value) is int:
            textStr += `value`
        else:
            print value
            newStr = "\"" + value + "\""
            textStr += newStr
        i = i + 1
    textStr += "}"
    return textStr

def decode(text):
    dictStr = text.replace('{','').replace('}','').split(',')
    dict = {}
    for item in dictStr:
        key = item.split(":")[0].replace('\"','')
        value = item.split(":")[1]
        if "\"" in value:
            dict[key] = value.replace('\"','')
        else:
            dict[key] = int(value)
    return dict

def playSound(type):
    try:
        pygame.init()
        pygame.mixer.init()
    except:
        return

    if type == "new" or type == "both":
        pygame.mixer.music.load("/usr/share/sounds/lwasp/success.wav")
        pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    if type == "penalty" or type == "both":
        pygame.mixer.music.load("/usr/share/sounds/lwasp/error.mp3")
        pygame.mixer.music.play()
    #waits until sound is finished playing to end script
    while pygame.mixer.music.get_busy():
        continue
