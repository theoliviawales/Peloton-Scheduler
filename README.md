# Peloton-Scheduler

Set env-vars with your phone number, email address, and a password (preferably an app specific password). I store mine in secret_keys.txt, but they aren't committed. SORRY!!

e.g,
export PHONE_NUMBER="<phone_number>"
export EMAIL_ADDRESS="<email_address>"
export EMAIL_PASSWORD="<password>"
export CHROME_DRIVER_PATH="<path>"

Run the python script and provide args for the individual days you wanna check
```
python check_peloton.py 7 8 9
```

This is all cobbled together and pretty trash. Its a one-off project (probably) for my sisters to check for peloton classes for 2 days in June.

Don't expect much :)