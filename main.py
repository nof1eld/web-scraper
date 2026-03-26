import csv
from bs4 import BeautifulSoup
import requests

def getHTML(url):
    # Get the response object that contains html
    response = requests.get(url)
    # return the html from response
    return response.text

html = getHTML('https://books.toscrape.com/')
# parse html
soup = BeautifulSoup(html, 'html.parser')

scrapedPrices=[]
scrapedNames=[]
scrapedInstock=[]
for stats in soup.find_all('p', attrs={'class': 'price_color'}):
    scrapedPrices.append(stats.text)
for stats in soup.find_all('h3'):
    scrapedNames.append(stats.text)
for stats in soup.find_all('p', attrs={'class': 'instock availability'}):
    scrapedInstock.append(stats.text.strip())
#write html in a txt file
with open('htmltext.txt','w')as f:
    f.write(requests.get("https://ai-house-website.vercel.app/sections/projects.html").text)


with open('scrapedInfo.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(scrapedNames)
    writer.writerow(scrapedPrices)
    writer.writerow(scrapedInstock)
    f.close()
