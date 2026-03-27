import csv
from bs4 import BeautifulSoup
import requests
import json
from os import getenv
import google.genai as genai
from google.genai import types

def getParsedHTML(url):
    # Get the response object that contains html
    response = requests.get(url)
    # return parsed html from response
    return BeautifulSoup(response.text, 'html.parser')

def getSchemaJSON(html):
        system_instruction = (
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
        )
        try:
            client = genai.Client(api_key="")
            response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction),
                    contents=str(html)
                ).text
            return json.loads(response)
        except Exception as e:
            print("An error occurred:", str(e))

parsedHTML = getParsedHTML('https://books.toscrape.com/')
schemaJSON = getSchemaJSON(parsedHTML)

print(schemaJSON)


