from bs4 import BeautifulSoup
import requests

r = requests.get('https://ai-house-website.vercel.app/')
htmlCode = r.text

soup = BeautifulSoup(htmlCode, 'html.parser')
print(soup.prettify())
