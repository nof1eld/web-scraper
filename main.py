import csv
from bs4 import BeautifulSoup
import requests
import json
from dotenv import load_dotenv
from os import getenv
import google.genai as genai
from google.genai import types

load_dotenv()
def getParsedHTML(url):
    # Get the response object that contains html
    response = requests.get(url)
    # return parsed html from response
    return BeautifulSoup(response.text, 'html.parser')

def getSchemaJSON(html):
        systemInstruction = (
            "Extract a scraping schema from the HTML.\n"
            "Return ONLY valid JSON in this format:\n"
            '{"row_selector":"...","fields":{"name":"selector"}}\n'
            "Don't use formatters"
            "Rules:\n"
            "- Identify the repeating item (row_selector)\n"
            "- Fields = visible data inside each row\n"
            "- Use short snake_case names\n"
            "- Selectors must be CSS and relative to the row\n"
            "- Prefer classes; avoid deep paths\n"
            "- Do not invent data\n"
            "- Return ONLY raw JSON.\n"
            "- Do NOT use markdown.\n"
            "- Do NOT wrap in ```json.\n"
            #added these prompts to avoid returning pseudo-elements that BS don't support
            "- Do NOT use pseudo-elements like ::text, ::attr, ::before, ::after\n"
            "- Selectors must be valid CSS for BeautifulSoup/soupsieve\n"
        )
        try:
            client = genai.Client(api_key=getenv("API_KEY"))
            response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    config=types.GenerateContentConfig(
                        system_instruction=systemInstruction),
                    contents=str(html)
                ).text
            return json.loads(response)
        except Exception as e:
            print("An error occurred:", str(e))


#new function to scrapedata from parsedhtml
def scrapeData(html, schema):
    rows = html.select(schema["row_selector"])
    scrapedData = []
    for row in rows:
        item = {}
        for f, s in schema["fields"].items():
            element = row.select_one(s)
            item[f] = element.get_text(strip=True)if element else None
        scrapedData.append(item)
    return scrapedData
parsedHTML = getParsedHTML('https://quotes.toscrape.com/')
schemaJSON = getSchemaJSON(parsedHTML)
scrapedData = scrapeData(parsedHTML, schemaJSON)
with open("scrapedInfo.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=scrapedData[0].keys())
    writer.writeheader()
    writer.writerows(scrapedData)
print(scrapedData)





