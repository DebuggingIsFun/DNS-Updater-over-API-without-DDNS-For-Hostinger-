# DNS Updater over API without DDNS (For Hostinger)

## Reason
This scripts (currently only hostinger) is inspired by this Repo https://github.com/AchuAshwath/ddns_hostinger
The Original was great and documented, but I wanted to learn it for myself.
How to use API's and even how could I make it "more" flexible

## How it works
The script can be used manually or via cronttab.
Example [crontab](./crontab) is provided.
It uses an .env file for variables and tracking the LAST_KNOWN_IP to only make API calls if the IP changed.
Look at the [example.env](./example.env) and enter there your whished values.
The values are currently for the [hostinger_ddns_py](./hostinger_ddns.py)

### example.env explained
- API_TOKEN is for you API Key, this you can genrate in your costumer panel
- DOMAINS if for you domains like example.tld you can add multiple seperated by comma (example.tld,anotherexample.tld)
- SUBDOMAINS you add the subdomain so if you have blog.mydomain.tld you just enter blog for multiple subdomains just add with comma )blog,www,test)
- LAST_KNOWN_IP is your last tracked IP
- TTL whished TTL to set

### crontab explained
- CRON_TZ for setting the Timezone that crontab should track for its timing (exmaple Europe/Paris)
- SHELL in whish shell should this run (example /bin/bash)
- PATH which PATH should be used to look for executbales, since crontab has non normally (example /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin)

- */5 1 * * * cd /app && /usr/local/bin/python /app/hostinger_ddns.py >> /var/log/cron.log 2>&1%
    - */5 1 * * * | is for running every 5 Minutes during the 1 AM (adjust to you needs when you think you IP Changes)
    - cd /app && /usr/local/bin/python /app/hostinger_ddns.py | change in the working directory (so we can use .env file) and run the python script
    - >> /var/log/cron.log 2>&1% | redirect the output for logging into this file (so the script itself does not log, only needs to output something to console)

### Script Function
Work in progress.