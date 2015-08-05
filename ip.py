import json
import commands
import re
from utility import *

#get ip addresses on system, store in settings, check each time computer restarts in case changes
found_ips = []
ips = re.findall( r'[0-9]+(?:\.[0-9]+){3}', commands.getoutput("/sbin/ifconfig"))
for ip in ips:
    if ip.startswith("255") or ip.startswith("127") or ip.endswith("255"):
        continue
    found_ips.append(ip)

ip = ', '.join(found_ips)
settings = getSettings()
settings['ip'] = settings
saveSettings(settings)
usersettings = getUserSettings()
usersettings[key] = settings
saveUserSettings(usersettings)
