EADME.md


# LWASP

###### The Linux Watchful Adaptive Security Compliance

Note: This repository is under rapid development (beta), do not expect everything to be functioning right now.  I'll be rolling out version 1.0 (stable) soon! Stay tuned.

## About
* LWASP is a service to scoring practice linux images in preparation for cyber security competitions
* Very versatile and open to modification, so that coaches can customize it specifically for their teams if they choose to do so
* Tested on Ubuntu 12.04, 14.04, & 16.04, but should work for all Debian-based linux distributions
* Uses Bash and Python for the backend, GTK+3 & Javascript with ReactJS and JQuery for the front end

## Installation & Setup
### Automatic
1. Run this command on the virtual machine that you want to set up: `wget -O - https://encompassx.com/lwasp/download_script.sh | bash`
2. If you are not logged in as root, you will have to put in the password for the current user when prompted.
3. Check what you want to score, and then follow the prompts to install LWASP on the image.

### Manual
1. Download `deploy.zip` from the [latest release](https://github.com/steffeydev/lwasp/releases/latest).
2. Unzip the downloaded file.
3. Drag the `deploy` folder onto the desktop of the image that you want to install LWASP on (or otherwise move the folder onto the virtual machine).
4. Open a command prompt (terminal) on the image and run the following commands:
  * `cd ~/Desktop/deploy`
  * `./setup`
5. If you are not logged in as root, you will have to put in the password for the current user when prompted.
6. Check what you want to score, and then follow the prompts to install LWASP on the image.

You can see a step-by-step guide in [the Tutorial](/Tutorial.pdf).

## Steps for Competitor to Take
1. Once the image is started and they log in, they double click the "Set ID" shortcut on the desktop to set their unique ID. You will receive this ID and the image ID you set during initialization in the email (if enabled). This is so that if you have several duplicate images, you can tell them apart.
2. They try to secure the image, gaining points by what was set in the elements file.
3. The scoring report will refresh every time a file is changed and once every minute. If this is not often enough or this does not seem to be working, they can type `sudo refresh` into a terminal to reload the score manually.
4. The instructor should tell them not to view or modify or view anything in the `/etc/lwasp` and `/usr/lwasp` directories, and they shouldn't touch the `/etc/init.d/lwasp` file.  In addition, if they edit the crontab and remove the scheduled task that calls `sudo refresh` every minute, they may have to run `sudo refresh` manually to see scoring updates. The list of what scores on the image is securely encrypted, so even if they go looking for it in these directories, they won't find it.  The worst they could do is simply break the scoring engine, in which case they can't get more points, which should be enough motivation for them to not touch these files and directories.

# LWASP Advanced Usage and Modification

## How it works
LWASP is a two part service: The setup utility and the installer. The setup utility is a simple GUI (graphical user interface) with several tabs, one for each category of what can score. The setup utility reads what the user enters/checks should be scored and generate two files: `elements.csv` and `commands.bash`.
The `elements.csv` is a CSV (comma-separated value) file that contains the scoring elements, or what will show up in the scoring report as the student secures the image. The commands.bash is a BASH (bourne-again shell) script that creates the needed vulnerabilities on the image so that when fixed, they can be scored. BASH commands are just commands that can be run at the command line. The setup utility places these two files in the `lwasp-install` directory after they are generated. The installer downloads various libraries, runs the command.bash script, turns the elements.csv file into an encrypted scoring.json file, and runs various other commands to install the scoring engine on the virtual machine.
There are two ways that advanced users can leverage these characteristics of LWASP to score more advanced vulnerabilities on a Linux system. First, you can create your own vulnerabilities on the image, such as modifying boot files in the /boot folder to create a low-level backdoor, and then add how to score this in the elements.csv file before you run the installer. Secondly, you can modify the scoring engine code itself (written in python) so that you can score different types of vulnerabilities, such as whether a given file has been modified by a specific daemon. This guide will document both ways.

## The `elements.csv` file

### Format

Each line in the `elements.csv` file is in the form: 
`Display Name,Mode,Points,Module,Module Parameters`
* The Mode can be `V` for vulnerability or `P` for penalty.  If it is marked as a vulnerability, then the student will earn that number of points when the module, given the parameters, returns true.  A penalty will *subtract* that number of points from their score when the module returns true, and alert the student that a penalty is being assessed.
* The `Points` should be an integer value greater than 0

### Modules
Each module takes its own set of parameters.  If you want to take the inverse of a module's check result, you can include the `!` symbol next to the module name (see example in FileExistance).

#### FileContents
Checks if the file contains or does not contains the given search strings 

Parameter 1: Absolute File Path
Parameter 2: (T/F) Whether the file should contain the search string(s) 
Parameter 3: The first search string
Parameter 4: The second search string (optional)
Parameter X: Any number of search strings can be passed in

Example: `User baduser removed from system,V,10,FileContents,/etc/passwd,false,baduser`
Example: `A maximum and minumum password age is set,V,15,FileContents,/etc/login.defs,true,PASS_MAX_DAYS 30,PASS_MIN_DAYS 1`

Notes:
* Search strings should be provided as regular expressions.  If you don't know how regular expressions (regex) works, start here: [RegexOne](https://regexone.com).
* The module automatically sanatizes each line of the input file to remove leading and trailing spaces, and converting all gaps between non-space characters to spaces.  This means that your regex can assume the the there is no white space before the first character of a line, and you will only have to match a maximum of one space between words (no tabs).
* Each expression is tested on each line, so you can't pattern match accross several lines of the file.  Instead, you should just pass one search string for each line you want to match.

#### FileExistance
Checks if the path provided is a valid file or directory

Parameter 1: Absolute File Path
Parameter 2: (T/F) Whether the file or direcotry should exist

Example: `Invalid hacking tool 'John the Ripper' removed,V,8,!FileExistance,/home/user/Downloads/john.zip`

#### Forensics
Checks if the student has provided the correct answer to a forensics question in a file.

Parameter 1: Absolute File Path
Parameter 2: First required answer
Parameter 3: Second required answer (optional)
Parameter X: Any number of required answers (optional)

Example: `Forensics question 1 correct,V,15,Forensics,/home/user/Desktop/ForensicsQuestion1.txt/,644`
File contents:
```
What file permissions allow the owner to read and write, and everyone else to only read? Answer should be 3 numbers with no spaces in between (e.g. 146)

ANSWER:
```

Notes:
* Support included for multiple answers; if the set of answers provided in the file matches the set of answers required by the line in `elements.csv` (case-insensitive), then the check passes.  Each answer in the file must be provided on its own line followed by `ANSWER:`

#### Package
Checks whether a package is installed, and optionally whether it matches a given version

Parameter 1: Package Name (as seen in `dpkg -l`)
Parameter 2: `installed` or `updated`
Parameter 3: (`updated` only) The version that should be updated to

Example: `Telnet no longer installed,V,10,!Package,telnet-common,installed`
Example: `Critical service ssh is no longer installed,P,5,!Package,openssh-server,installed`
Example: `MySQL server has been updated,V,8,Package,mysql-server,updated,5.7.21-0ubuntu0.16.04`

#### Service
Checks the `service` output to see if a package is loaded (exists) or active (running)

Parameter 1: Service Name (as seen in `service --status-all`)
Parameter 2: `loaded` or `active`

Example: `Critical service Apache is not running,P,8,!Service,apache2,active`
Example: `CUPS print server has been removed,V,10,!Service,cups,loaded`

#### Permissions
Checks file permissions

Parameter 1: Absolute File Path
Parameter 2: Permission Octal Code (3-digit, e.g. `644`)
Parameter X: Additional valid permission string

Example: `Shadow file secures,V,15,Permissions,/etc/shadow,640,600`

# Modifying LWASP

If the built in options aren't enough for you, here are some basic steps to extend the service.  You can find a more detailed guide in [the Advanced Users Guide](/Advanced%20Users%20Guide.pdf).

## Add Scoring Categories
1. Add a python file in `deploy-dev/lwasp-install/modules` (`MyModuleName.py`) that contains a `check` function which takes the `extras` as a parameter and returns whether the check was successful (True/False).  You should raise `TypeError` if the array passed in is not long enough for your module to run. You can look at some of the built-in modules for clarification.
2. Run `cd deploy-dev; ./generate_deploy` to move your new module and any other changes to the deploy folder.
2. Add your category in the elements.csv file with the needed extras, and start using it!
with any questions.

## Breakdown of the files
(** indicates a file that you should provide)


###### These are the python files that do all of the grunt work
* **initialize.py** - Sets up the scoring engine to run, and puts everything in motion.
* **analyze.py** - Called every minute from a crontab and every time a file that is scored changes. It parses through what should be scored and determines what score the user of the image has achieved, then writes that back to **recording.json**.
* **modules/** - Each of the files are used by **analyze.py** to complete the scoring checks.
* **restart.py** - Sets up the file watches and does several other tasks that must be run on boot. It is called from **cse.bash**.


###### These are the files that are referenced / used by **initialize.py**
* **cron.bash** - Called in **initialize.py** to setup the cron job that calls **analyze.py**. It is only ever called once.
* **cse.bash** - Moved into /etc/init.d from **initialize.py** and set to run at boot. It simply calls **restart.py** when run.
* ** **elements.csv** - The user-generated comma-separated-value file that contains what should be scored and what should be penalized.


###### These elements in the lwasp folder make up the UI
* **main.js** - The heart of what powers the UI. It is loaded from report.html, which is opened when the user double clicks on it from their desktop.
* **jquery.js** - Used in **main.js** to power the ajax calls that retrieves **recording.json** and **settings.json** in javascript to do some calculations on and display to the user.
* **transform.js** - What powers the use of JSX in main.js. See https://facebook.github.io/react/docs/tooling- integration.html for more information.
* ** **logo.png** - The image that is used on the scoring report and on the desktop images.
* **react.js** - Powers the react code in **main.js**.


###### These store data to be used by the main three python scripts above.
* **recording** - Stores all of the user-imported elements from **elements.csv** but in a more computer friendly format, also adding a field for whether each item is completed.
* **settings.json** - Contains some user-generated settings that were entered during initialization.


## Notes

* You can reach me for contact at [steffeydev@icloud.com](mailto:steffeydev@icloud.com) with any questions, concerns, etc.
* Forensics questions are in the CyberPatriot model; only checks the text after “ANSWER: “ (can support multiple answers.)
* Feel free to read through all of my code, I have tried to comment it as much as needed. If you know any amount of python it should be fairly easy to understand and modify to fit your needs.
* The scoring report generator is written in javascript using a framework called [React](https://reactjs.org), which was created by Facebook in 2013. Feel free to research and learn it, but I have to warn you that just messing with it as plain javascript may not work that well.

## Contributing

PRs are welcome!  I would love some help creating more modules, adding more pre-configured elements in the setup GUI, etc.

Feature requests and discussions are also welcome! I'm always looking for more ways to make LWASP as useful and simple as possible, for both new linux users and linux ninjas.

Finally, if you want to help port LWASP to RHEL-based or even *BSD systems, I would love to work with you on that as well.  I've set the system up so that this kind of port should not be too complicated, but extensive testing and validation would be needed.
