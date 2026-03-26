from bs4 import BeautifulSoup
import requests

def getHTML(url):
    # Get the response object that contains html
    response = requests.get(url)
    # return the html from response
    return response.text

html = getHTML('https://ai-house-website.vercel.app/')
# parse html
soup = BeautifulSoup(html, 'html.parser')

print(soup.prettify())
