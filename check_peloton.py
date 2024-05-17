from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

import aiosmtplib
import asyncio
import re
import requests
import os

from bs4 import BeautifulSoup
from email.message import EmailMessage
from sys import argv
from time import sleep

EMAIL_DOMAIN = 'txt.att.net'
HOST = 'smtp.gmail.com'
PELOTON_URL = 'https://schedule.studio.onepeloton.com/p/7248695-peloton-studios-new-york/c/schedule?startdate=2024-05-30&enddate=2024-07-03&date=2024-06-06&venues=&category=&instructors=&offering_types='    
CHECK_DELAY_SEC = 60
TEXT_DELAY_SEC = 10

async def send_txt(number: str, email: str, password: str, subject: str, msg: str):
    # build message
    message = EmailMessage()
    message["From"] = email
    message["To"] = f"{number}@{EMAIL_DOMAIN}"
    message["Subject"] = subject
    message.set_content(msg)

    # send
    send_kws = dict(username=email, password=password, hostname=HOST, port=587, start_tls=True)
    res = await aiosmtplib.send(message, **send_kws)  # type: ignore
    msg = "failed" if not re.search(r"\sOK\s", res[1]) else "succeeded"
    print(msg)
    return res

def get_source_selenium():
    options = Options()
    service = Service('/opt/homebrew/bin/chromedriver')
    options.add_argument("--headless")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(PELOTON_URL)
    
    # Wait for dynamic content to load
    sleep(5)

    page_source = driver.page_source
    driver.quit()
    
    return page_source

def get_source_raw():
    html_doc = ''
    with open('example_source.html', 'r') as f:
        html_doc = ''.join(f.readlines())
        
    r = requests.get(PELOTON_URL)
    r.raise_for_status()
    
    return r.text

def parse_html(html_text):    
    soup = BeautifulSoup(html_text, 'lxml')
    day_events = []

    # Skip the first element, its the name of the program
    for day in argv[1:]:
        # Find the span with the day label
        label = soup.find("span", text=day)

        # Get the parent container
        parent = label.parent

        # Get the sibling element in the dom tree, which contains the events list
        events = parent.next_sibling

        contains_events = 'No Events' not in events.getText()
        if contains_events:
            day_events.append(day)

        print('Day {} -- contains events: {}'.format(day, contains_events))
    return day_events

# Infinite loop babyyyyy
while(True):
    print('CHECKING!!!')
    
    html = get_source_selenium()
    day_events = parse_html(html)

    if len(day_events) > 0:
        day_string = ', '.join(day_events)
        message = 'CLASS ON JUNE {}'.format(day_string)

        txt_event = send_txt(os.environ['PHONE_NUMBER'], os.environ['EMAIL_ADDRESS'], os.environ['EMAIL_PASSWORD'], message, message)
        asyncio.run(txt_event)

        # Wait for a lil for the async text sending to complete
        sleep(TEXT_DELAY_SEC)
        exit(0)

    else:
        print('NO EVENTS')

        # Wait 1 minute before checking again
        sleep(CHECK_DELAY_SEC)