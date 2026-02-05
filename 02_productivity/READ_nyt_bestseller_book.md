# <span style="color: #FF69B4">📌</span> READ

## **<u>NYT Bestseller Books</u>**

<span style="color: #FF69B4">🕒</span> *Estimated Time: 8 minutes*

---

The **New York Times Best Sellers** lists rank the top-selling books in the United States. They are widely used by readers, publishers, and retailers as a signal of popular and influential titles. Understanding how these lists work helps when you query the **NYT Books API** (e.g., from the scripts in `01_query_api`) or build tools that use bestseller data.

---

## What the lists are

- **Fiction** and **Nonfiction** (combined print and e-book)
- **Advice, How-To & Miscellaneous**
- **Children’s** (picture books, middle grade, young adult)
- **Graphic Novels and Manga**
- **Series** (fiction and nonfiction)

Lists are published weekly. Each list shows a fixed number of titles (often 10 or 15) with **rank**, **title**, **author**, **weeks on list**, and sometimes a short description or cover image, depending on the endpoint.

---

## How the lists are built

The Times does not disclose exact methodology, but it has stated that the lists reflect **sales** from a variety of reporting retailers (chains, independents, online). They are **curated**: the Times applies its own rules and checks, so the lists are editorial products, not raw sales feeds. That makes them useful for “what’s selling and being talked about” rather than precise market share.

---

## Using the NYT Books API for bestsellers

In this course you can use the **NYT Books API** (see [The New York Times API](https://developer.nytimes.com/apis)) to fetch bestseller data programmatically. Typical use cases:

- **Productivity / automation**: Pull current lists into a script or app instead of checking the website.
- **Analysis**: Track how long titles stay on the list, compare lists over time, or combine with other data.
- **Integration**: Feed bestseller data into a Shiny app, report, or dashboard (e.g., in the productivity and deployment modules).

The Books API includes endpoints for **lists** (e.g., combined print and e-book fiction), **list names** (available lists and slugs), and **reviews**. You will need an **API key** from the NYT developer portal; the `01_query_api` folder has examples (e.g. [`03_nyt_books_query.py`](../01_query_api/03_nyt_books_query.py)) that show how to call these endpoints.

---

## Takeaways

- **NYT bestseller lists** are weekly, curated rankings based on reported sales.
- They are useful for understanding **popular books** and for **automating** or **analyzing** that data via the **NYT Books API**.
- In this repo, use the scripts and patterns in `01_query_api` and your productivity tools to work with bestseller data in a repeatable way.

---

![](../docs/images/icons.png)

---

<span style="color: #FF69B4">←</span> <span style="color: #FF69B4">🏠</span> [Back to Top](#READ)
