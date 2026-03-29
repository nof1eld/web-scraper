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



app = Flask(__name__)
CORS(app, origins="*")
api_key = os.environ["GEMINI_API_KEY"]

playwright_instance = None
browser = None

# open new chromium browser (if there isn't)
def get_browser():
    global playwright_instance, browser
    if browser is None:
        playwright_instance = sync_playwright().start()
        browser = playwright_instance.chromium.launch()
    return browser


def getParsedHTML(url):
    # open browser window 
    browser = get_browser()
    context = browser.new_context()
    page = context.new_page()
    # prevent unnecessary resources from being fetched
    page.route(
        "**/*",
        lambda route: route.abort()
        if route.request.resource_type in ["image", "media", "font"]
        else route.continue_()
    )
    # open url and fetch the html from it
    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(8000)
    html = page.content()
    context.close()
    # return parsed & cleaned html from response
    parsedHTML = BeautifulSoup(html, 'html.parser')
    for tag in parsedHTML(["script", "style", "noscript", "svg"]):
        tag.decompose()
    body = parsedHTML.body 
    return body if body else parsedHTML

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
        "- Each selector must be valid CSS, and field selectors must be relative to the row.\n"
        "- If an element is identified by class, prefix the class with a dot.\n"
        "- Do not write class names as tag names. For example, if an element has class 'v-card', use '.v-card', not 'v-card'.\n"
        "- If multiple classes are on the same element, combine them like '.class1.class2'.\n"
        "- Only use a tag selector like 'div' or 'article' when that is the actual HTML tag.\n"
        "- Prefer stable semantic selectors.\n"
        "- Prefer selectors that are likely to match real elements in the provided HTML.\n"
        "- Avoid brittle generated classes that look hashed or auto-generated unless no better selector exists.\n"
        "- Avoid deep descendant chains when a shorter selector works.\n"
        "- Each field selector should target the smallest element that contains only that field's text.\n"
        "- Do not use one selector for multiple fields if that selector returns concatenated text from several data points.\n"
        "- Avoid selectors that capture long rich-text descriptions, hidden content, scripts, styles, or JSON blobs.\n"
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
    print("SCHEMA_JSON_RESPONSE_START")
    print(response)
    print("SCHEMA_JSON_RESPONSE_END")
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
    print("PARSED_HTML_START")
    print(parsedHTML)
    print("PARSED_HTML_END")
    schemaJSON = getSchemaJSON(parsedHTML)
    print("PARSED_SCHEMA_JSON_START")
    print(schemaJSON)
    print("PARSED_SCHEMA_JSON_END")
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
