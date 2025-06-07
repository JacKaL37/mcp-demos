# Web Scraper Demo

This demo shows how to use the Model Context Protocol (MCP) server to create a web scraping agent that can:

1. Retrieve website content and convert it to markdown
2. Extract links from the website
3. Record structured data to CSV files with enhanced location information

## Tools

### `retrieve_site(url)`

Fetches a webpage and returns:
- `markdown`: The markdown version of the site content
- `links`: A list of all anchors (links) detected, including:
  - `url`: The link URL (absolute)
  - `text`: The link text label

### `record_data(csv_file_path, csv_file_header, data, url, source_html)`

Records scraped data to a CSV file with:
- All fields specified in `csv_file_header`
- Three additional columns:
  - `url`: Link to the page with anchor if available
  - `rough_location`: Natural language description of where the data was found
  - `xpath`: Exact XPath location in the HTML

## Running the Demo

```bash
# Basic usage with default settings
python tests/web-scraper-demo.py

# Custom settings
python tests/web-scraper-demo.py \
  --base-url "https://example.com" \
  --csv-header "field1,field2,field3" \
  --csv-output "data/custom_output.csv"
```

## Default Configuration

- Base URL: `https://www.restaurantbusinessonline.com/top-500-2024-ranking`
- CSV Headers: `rank, restaurant_name, segment, 2023_sales_millions, 2023_units, sales_per_unit`
- Output File: `data/restaurant_data.csv`

## Requirements

The demo requires the following dependencies:
- Python 3.10+
- `agents` and `fastmcp` packages
- BeautifulSoup4, html2text, and lxml for HTML processing
- `uv` for running the server