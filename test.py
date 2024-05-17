from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

import aiosmtplib
import asyncio
import re
import requests

from bs4 import BeautifulSoup
from email.message import EmailMessage
from sys import argv
from time import sleep

EMAIL_DOMAIN = 'txt.att.net'
HOST = 'smtp.gmail.com'
PELOTON_URL = 'https://schedule.studio.onepeloton.com/p/7248695-peloton-studios-new-york/c/schedule?startdate=2024-05-30&enddate=2024-07-03&date=2024-06-06&venues=&category=&instructors=&offering_types='    

async def send_txt(number: str, email: str, password: str):
    # build message
    message = EmailMessage()
    message["From"] = email
    message["To"] = f"{number}@{EMAIL_DOMAIN}"
    message["Subject"] = subj
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

    for day in argv[1:]:
        # Find the span with the day label
        label = soup.find("span", text=day)

        # Get the parent container
        parent = label.parent

        # Get the sibling element in the dom tree, which contains the events list
        events = parent.next_sibling

        contains_events = 'No Events' not in events.getText()
        print('Day {} -- contains events: {}'.format(day, contains_events))

html = get_source_selenium()
parse_html(html)