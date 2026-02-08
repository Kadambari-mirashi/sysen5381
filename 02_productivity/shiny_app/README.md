# NYT Bestseller Recommendations — Shiny App

Shiny app that uses the **NYT Books API** (same data source as [`01_query_api/my_good_query.py`](../../01_query_api/my_good_query.py)). Card layout: title + filters, recommendations table, and a **top-10 “weeks on list”** dashboard graph by list.

## Features

- **List & sort** — Dropdowns for bestseller list and sort order (rank, weeks on list, title, author).
- **Recommendations table** — Rank, title, author, weeks on list, publisher.
- **Dashboard graph** — Top 10 books for the selected bestseller list, showing **how many weeks** each was on the list (horizontal bar chart).

## Full data (optional): `fetch_bestsellers.py`

The app can use either live API calls or a **pre-fetched JSON file** with full data for all lists:

1. From the project root, ensure `.env` has `NYT_API_KEY`.
2. Run the Python script (creates `data/bestsellers.json`):

   ```bash
   cd 02_productivity/shiny_app
   python fetch_bestsellers.py
   ```

3. The app will use `data/bestsellers.json` when present (all lists, full book fields); otherwise it falls back to the API.

## Requirements

- **R** packages: `shiny`, `httr2`, `jsonlite`, `dplyr`, `ggplot2`, `bslib`
- **Python** (for fetch script): `requests`, `python-dotenv`
- **NYT API key** in `.env` at project root (`dsai/.env`):

  ```text
  NYT_API_KEY=your_real_nyt_api_key_here
  ```

Install R packages if needed:

```r
install.packages(c("shiny", "httr2", "jsonlite", "dplyr", "ggplot2", "bslib"))
```

## How to run the app

From the project root:

```r
shiny::runApp("02_productivity/shiny_app")
```

Or from inside the app folder:

```r
setwd("02_productivity/shiny_app")
shiny::runApp("app.R")
```

If the list dropdown is empty, run `fetch_bestsellers.py` to generate `data/bestsellers.json`, or set `NYT_API_KEY` in `.env` so the app can call the API directly.

## Data source

- [NYT Books API](https://developer.nytimes.com/docs/books-product/1/overview): `lists/names.json`, `lists/current/{list_name_encoded}.json`
- Same API and key as in [README_my_good_query.md](../../01_query_api/README_my_good_query.md).
