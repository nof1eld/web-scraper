import csv
import time

from bs4 import BeautifulSoup
import requests

def getHTML(url):
    # Get the response object that contains html
    #i'm limiting the requests to 2 seconds
    time.sleep(2)
    response = requests.get(url)
    # return the html from response
    return response.text

html = getHTML('https://ai-house-website.vercel.app/sections/projects.html')
# parse html
soup = BeautifulSoup(html, 'html.parser')

scrapedInfo=[]

for stats in soup.find_all('div', attrs={'class': 'stat'}):
    scrapedInfo.append(stats.text)

with open('scrapedInfo.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(scrapedInfo)
    f.close()
