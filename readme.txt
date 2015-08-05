Welcome to the USELESS service, the Universal Security-Enhancing Linux Engine for Synchronous Scoring.  It has been tested on ubuntu 12.04 and 14.04, though should work on all versions of linux.

USELESS is built on python and bash for the backend; javascript with react and jquery for the front end.

Initializing it is simple:
1) Follow the instructions in the USELESS Elements Generator Excel file to create the elements.csv file in the useless directory (make sure to allow macros!)
2) If you have your own logo, please replace the default with it, and make sure it is named logo.png.  This logo is used for the desktop shortcuts and on the scoring report, and is an easy way to personalize USELESS
3) Move the useless directory onto the purposefully vulnerable linux image that needs to be scored (recomended in /etc/)
4) cd into the useless folder on the image and run ‘sudo python initialize.py’
5) Answer the prompts
6) Shut down the image, and distribute it to competitors.  The scoring engine will start on next boot.

What the competitor/aspiring cyber security professional will have to do:
1) Once the image is started and they log in, they double click the "Set ID" file on the desktop to set their unique ID.  You will receive this ID and the image ID you set during initialization in the email. This is so that if you have several duplicate images, you can tell them apart.
2) Try to secure the image, gaining points by what was set in the elements file.
3) The scoring report will refresh every time a file is changed and once every minute.  If this is not often enough or this does not seem to be working, they can type 'sudo refresh' into a terminal to reload the score manually

Modifiying the engine to make new categories to score:
If the 8 provided categories aren't enough, you can always add more yourself.  It is a fairly simple process
1) Add a function in analyze.py that can take in the extras as parameters and return True or False as to whether that item should be marked complete according to those parameters
2) Near the bottom of the analyze.py file, where the recording file is read, add your category beneath all of the others, with the same syntax, but use function = myNewFunction(extras...)
3) In initialize.py, add your new category to line 104 where it checks each type for validity.
4) That's it! Add your category in the elements.csv file with the needed extras, and start using it.  Contact me with any questions.

Here is a breakdown of each of the files:           (** indicates a file that you should provide)

//// These are the python files that do all of the grunt work ////
initialize.py is what sets up the scoring engine to run, and puts everything in motion.
analyze.py is called every minute from a crontab and every time a file that is scored changes.  It parses through what should be scored and determines what score the user of the image has achieved, then writes that back to recording.json.
restart.py sets up the file watches and does several other tasks that must be run on boot.   It is called from se.bash

//// These are the files that are referenced/used by initialize.py ////
cron.bash is called in initialize.py to setup the cron job that calls analyze.py.  It is only ever called once.
cse.bash is moved into /etc/init.d from initialize.py and set to run at boot.  It simply calls restart.py when run.
** elements.csv is the user-generated comma-separated-value file that contains what should be scored and what should be penalized.

//// These elements in the ScoringEngine folder make up the UI ////
ScoringReport.html is the wrapper file for the front end.
main.js is the heart of what powers the UI.  It is loaded from ScoringReport.html, which is opened when the user double clicks on it from their desktop.
jquery.js is used in main.js to power the ajax calls that retrieves recording.json and settings.json in javascript to do some calculations on and display to the user.
transform.js is what powers the use of JSX in main.js.  See https://facebook.github.io/react/docs/tooling-integration.html for more information.
logo.png is exactly what it sounds like.
react.js powers the react code in main.js.
** logo.png is the image that is used on the scoring report and on the desktop images

//// These store data to be used by the main three python scripts above ////
recording stores all of the user-imported elements from elements.csv but in a more computer friendly format, also adding a field for whether each item is completed.
settings.json contains some user-generated settings that were entered during initialization.


A Few Notes
* feel free to read through all of my code, I have tried to comment it as much as needed.  If you know any amount of python it should be fairly easy to understand and modify to fit your needs.
* main.js is written in javascript using a framework called React, which was created by Facebook in 2013.  Feel free to research and learn it, but I have to warn you that just messing with it as plain javascript may not work that well.
* you can reach me for contact at contact@nsccmanager.com with any questions, concerns, etc
* Forensics questions are in the CyberPatriot model; only checks the text after “ANSWER: “ (can support multiple answers.
