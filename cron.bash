#write out current crontab
crontab -l > mycron
#echo new cron into cron file # refresh calls analyze.py (setup in initialize.py)
echo "*/1 * * * * sudo refresh" >> mycron
#install new cron file
crontab mycron
rm mycron
