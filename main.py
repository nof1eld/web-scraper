from bs4 import BeautifulSoup
import requests

# get r object that contains html
r = requests.get('https://ai-house-website.vercel.app/')
# get the html from r object
htmlCode = r.text

# parse and print html
soup = BeautifulSoup(htmlCode, 'html.parser')
print(soup.prettify())
