from playwright.sync_api import sync_playwright
import os
import csv
from bs4 import BeautifulSoup
import json
import io
import google.genai as genai
from google.genai import types
from flask import Flask, request, Response
from flask_cors import CORS



app = Flask("__name__")
CORS(app, origins="*")
api_key = os.environ["GEMINI_API_KEY"]

def getParsedHTML(url):
    # open new chromium window and fetch the html from url
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        html = page.content()
        browser.close()
    # return parsed html from response
    return BeautifulSoup(html, 'html.parser')

def getSchemaJSON(html):
    systemInstruction = (
        "Extract a scraping schema from the HTML.\n"
        "Return ONLY valid JSON in this exact format:\n"
        '{"row_selector":"CSS selector","fields":{"field_name":"relative CSS selector"}}\n'
        "Your entire response must begin with { and end with }.\n"
        "Rules:\n"
        "- Choose the repeating container used for the main list items, not a wrapper around the whole page and not a single highlighted card.\n"
        "- The row_selector must match multiple similar items whenever the page is a listing page.\n"
        "- Include only visible text fields inside each row.\n"
        "- Use short snake_case field names.\n"
        "- Each field selector must be valid CSS and relative to the row.\n"
        "- Prefer stable semantic selectors.\n"
        "- Avoid brittle generated classes that look hashed or auto-generated unless no better selector exists.\n"
        "- Avoid deep descendant chains when a shorter selector works.\n"
        "- Each field selector should target the smallest element that contains only that field's text.\n"
        "- Do not use one selector for multiple fields if that selector returns concatenated text from several data points.\n"
        "- Avoid selectors that capture long rich-text descriptions, HTML fragments, hidden content, scripts, or JSON blobs.\n"
        "- If a field is not clearly available as its own text element, omit it instead of guessing.\n"
        "- Do not invent fields or values.\n"
        "- Do NOT use pseudo-elements like ::text, ::attr, ::before, ::after or any other pseudo-element.\n"
        "- Selectors must be valid CSS for BeautifulSoup/soupsieve.\n"
        "- Return ONLY raw JSON.\n"
        "- Do NOT include markdown, comments, or explanations.\n"
        "- Do NOT wrap the JSON in triple backticks.\n"
        "- Do NOT start the response with ```json.\n"
        "- Output exactly one JSON object and nothing else.\n"
    )

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=systemInstruction
        ),
        contents=str(html)
    ).text
    return json.loads(response)


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

@app.route("/scrape")
def scrape():
    url = request.args.get("url")
    parsedHTML = getParsedHTML(url)
    schemaJSON = getSchemaJSON(parsedHTML)
    scrapedData = scrapeData(parsedHTML, schemaJSON)

    csvFile = io.StringIO()
    writer = csv.DictWriter(csvFile, fieldnames=scrapedData[0].keys())
    writer.writeheader()
    writer.writerows(scrapedData)
    return Response(
        csvFile.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=data.csv"}
    )

if __name__ == "__main__":
    app.run(debug=True)