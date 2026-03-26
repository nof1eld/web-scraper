from bs4 import BeautifulSoup

soup = BeautifulSoup("<p>Hello imad!</p>", 'html.parser')
print(soup.prettify())
