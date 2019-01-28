

USER=$(whoami)
SCRIPT_PATH=/spider_code/schedule/schedule.sh
CRONTAB_PATH=/spider_code/schedule/schedule.crontab
CRONTAB_LOG=/spider_code/log/crontag.log

# generate crontag file, log file shows if there is error while generating
# */10 9-18 * * * SCRIPT_PATH >> CRONTAB_LOG 2>&1
# run SCRIPT_PATH every ten minute from 09:00 to 18:00 everyday and redirect stdin and stderr to CRONTAB_LOG
echo '*/10 9-18 * * * '$SCRIPT_PATH' >> '$CRONTAB_LOG' 2>&1' > $CRONTAB_PATH

# remove and asign new crontab job file
crontab -r >/dev/null 2>&1
crontab -u $USER $CRONTAB_PATH 2>&1
crontab -l
