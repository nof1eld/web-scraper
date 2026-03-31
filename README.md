# Web Scraper API

This project is a generic scraping API that turns a web page into structured CSV data.

> Note: the API layer is simple. The real focus of this project is the scraping functionality and the extraction workflow, not the API design itself.

Instead of hardcoding selectors for one specific website, it tries to understand the page structure dynamically. The idea is simple:

- a user provides a URL
- the page is loaded in a real browser
- the visible HTML is cleaned up
- an AI model suggests a scraping schema
- the schema is used to extract repeated items
- the result is returned as a CSV file

## How It Works

The scraper is built around the idea of schema generation rather than website-specific rules.

For each request, the system:

1. opens the target page in a browser environment so JavaScript-driven websites can render
2. removes noisy parts of the page such as scripts and styles
3. sends the cleaned HTML to a model that tries to identify:
   - the repeating row container
   - the fields inside each row
4. applies those selectors to extract structured data
5. returns the extracted rows as CSV

This makes the project more flexible than a scraper written for only one site, but it also means output quality depends on how clearly the page exposes repeated content.


## Current Limits

Because the scraper is generic, some pages are naturally harder than others.

Common challenges include:

- pages that are still showing loading placeholders or skeleton UI
- websites whose main content appears late or progressively
- pages with very noisy or highly dynamic DOM structures
- AI-generated selectors that are syntactically valid but not meaningful for the actual content

In other words, the system works best when a page has a clear repeated structure and the final rendered HTML actually contains that structure at capture time.

## API Idea

The API is intentionally simple:

- a URL goes in
- a CSV file comes out

The current interface is just a simple GET endpoint that accepts a target URL and returns the extracted result as a downloadable CSV response.

## Demo

Live frontend demo:

- https://web-scraper-frontend-eta.vercel.app/
- Frontend repository: https://github.com/mendas-cpu/web-scraper-frontend

## Configuration

The application uses NVIDIA's hosted models API and an environment variable:

- `NVIDIA_API_KEY`

## Running and Deploying

Locally, the app can be run as a small Flask service.

In deployment, it is intended to run as a web API service, for example on Render, where:

- Python dependencies are installed from `requirements.txt`
- Playwright’s Chromium browser is installed during build
- the app is served through Gunicorn

## Summary

This project is a browser-backed, AI-assisted scraping API.

Its main goal is not to scrape one site perfectly, but to explore a more general workflow:

- render the page
- understand its repeating structure
- extract rows
- return CSV

That makes it more adaptable, but also more dependent on page timing, DOM quality, and schema generation accuracy.
