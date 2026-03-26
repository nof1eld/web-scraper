from bs4 import BeautifulSoup
import requests

def getHTML(url):
    # Get the response object that contains html
    response = requests.get(url)
    # return the html from response
    return response.text

# parse and print html
soup = BeautifulSoup(htmlCode, 'html.parser')
print(soup.prettify())
