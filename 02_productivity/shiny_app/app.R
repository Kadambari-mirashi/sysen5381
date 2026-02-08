#' @name app.R
#' @title NYT Bestseller Recommendations — Card Dashboard
#' @description
#' Topic: Productivity / Shiny
#'
#' Shiny app using the NYT Books API (same data as 01_query_api/my_good_query.py).
#' Data can be pre-fetched with fetch_bestsellers.py to data/bestsellers.json for full lists.
#' Three panes: title + inputs card, recommendations table card, top-10 weeks-on-list dashboard graph.

# 0. SETUP ##############################################################

## 0.1 Load packages ####################################################

library(shiny)
library(httr2)
library(jsonlite)
library(dplyr)
library(ggplot2)

## 0.2 Load environment ##################################################

env_path = c(
  file.path("..", "..", ".env"),
  file.path("..", ".env"),
  ".env"
)
env_file = env_path[file.exists(env_path)][1]
if (!is.na(env_file)) {
  readRenviron(env_file)
} else {
  warning("No .env found. Set NYT_API_KEY in .env at project root for API access.")
}
API_KEY = Sys.getenv("NYT_API_KEY")
BASE_URL = "https://api.nytimes.com/svc/books/v3"

## 0.3 API helpers ######################################################

nyt_get = function(path, query = list()) {
  query = c(list("api-key" = API_KEY), query)
  url = paste0(BASE_URL, "/", path)
  req = request(url) |>
    req_url_query(!!!query) |>
    req_method("GET")
  resp = req_perform(req)
  if (resp_status(resp) != 200) return(NULL)
  out = resp_body_json(resp)
  if (identical(out$status, "OK")) out else NULL
}

get_list_names = function() {
  out = nyt_get("lists/names.json")
  if (is.null(out) || length(out$results) == 0) return(NULL)
  results = out$results
  data.frame(
    list_name_encoded = vapply(results, function(x) x$list_name_encoded %||% "", ""),
    list_name = vapply(results, function(x) x$list_name %||% x$list_name_encoded %||% "", ""),
    stringsAsFactors = FALSE
  ) |>
    filter(nzchar(list_name_encoded), nzchar(list_name))
}

get_current_list = function(list_name_encoded) {
  if (!nzchar(list_name_encoded)) return(NULL)
  path = paste0("lists/current/", list_name_encoded, ".json")
  out = nyt_get(path)
  if (is.null(out)) return(NULL)
  books = out$results$books %||% list()
  if (length(books) == 0) return(NULL)
  rows = lapply(books, function(b) {
    data.frame(
      rank = as.integer(b$rank %||% NA),
      title = as.character(b$title %||% ""),
      author = as.character(b$author %||% ""),
      weeks_on_list = as.integer(b$weeks_on_list %||% NA),
      description = as.character(b$description %||% ""),
      publisher = as.character(b$publisher %||% ""),
      stringsAsFactors = FALSE
    )
  })
  bind_rows(rows)
}

# Load full data from JSON if available (from fetch_bestsellers.py); else use API
bestsellers_json_path = NULL
for (p in c("data/bestsellers.json", file.path("02_productivity", "shiny_app", "data", "bestsellers.json"))) {
  if (file.exists(p)) { bestsellers_json_path = p; break }
}

load_bestsellers_file = function() {
  if (is.null(bestsellers_json_path)) return(NULL)
  out = tryCatch(jsonlite::read_json(bestsellers_json_path), error = function(e) NULL)
  if (is.null(out) || !is.list(out$lists)) return(NULL)
  out
}

`%||%` = function(x, y) if (is.null(x) || (length(x) == 1 && is.na(x))) y else x

# Convert one book from JSON (full object) to one row for table/graph
book_to_row = function(b) {
  data.frame(
    rank = as.integer(b$rank %||% NA),
    title = as.character(b$title %||% ""),
    author = as.character(b$author %||% ""),
    weeks_on_list = as.integer(b$weeks_on_list %||% NA),
    description = as.character(b$description %||% ""),
    publisher = as.character(b$publisher %||% ""),
    stringsAsFactors = FALSE
  )
}


# 1. UI #################################################################

# Walnut brown + Cinnamon brown theme, cursive font
ui = fluidPage(
  title = "NYTimes Bestseller Recommendations",
  theme = bslib::bs_theme(
    bootswatch = "flatly",
    base_font = bslib::font_google("Dancing Script"),
    heading_font = bslib::font_google("Dancing Script"),
    bg = "#F5EDE4",
    fg = "#3E2723",
    primary = "#5C4033",
    secondary = "#8B6914"
  ),
  tags$head(
    tags$style(HTML("
      body { font-family: 'Dancing Script', cursive; }
      .screen { height: 100vh; display: flex; flex-direction: column; overflow: hidden; box-sizing: border-box; background: #F5EDE4; }
      .screen * { box-sizing: border-box; }
      .screen-top { flex: 2 1 0; min-height: 0; display: flex; flex-direction: row; overflow: hidden; padding: 0.5rem 0; }
      .screen-bottom { flex: 1 1 0; min-height: 0; overflow: hidden; padding: 0.5rem 0; }
      .left-section { flex: 0 0 36%; display: flex; flex-direction: column; gap: 0.5rem; padding-right: 0.5rem; min-height: 0; overflow: hidden; }
      .right-section { flex: 1 1 0; display: flex; flex-direction: column; min-height: 0; padding-left: 0.5rem; overflow: hidden; }
      .card-title { flex: 0 0 150px; height: 150px; min-height: 150px; justify-content: center; align-items: center; text-align: center; padding: 1.5rem 1rem !important; }
      .card-title h2 { margin: 0; color: #5C4033; font-weight: 700; font-size: 1.5rem; font-family: 'Dancing Script', cursive; }
      .card-filter { flex: 1 1 0; min-height: 0; padding: 1.25rem !important; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; overflow: hidden; }
      .card-filter .filters-stack { width: 100%; max-width: 280px; }
      .card-filter .filters-stack .form-group { margin-bottom: 1rem; text-align: left; }
      .card-filter .filters-stack label { font-weight: 600; font-size: 0.95rem; font-family: 'Dancing Script', cursive; color: #3E2723; }
      .selectize-dropdown, .selectize-dropdown-content { max-height: 280px !important; overflow-y: auto !important; }
      .card-table { flex: 1 1 0; min-height: 0; display: flex; flex-direction: column; overflow: hidden; padding: 0.75rem 0.5rem; }
      .card-table h5 { font-family: 'Dancing Script', cursive; color: #5C4033; }
      .table-scroll-wrapper { flex: 1; min-height: 100px; overflow-y: auto; overflow-x: auto; -webkit-overflow-scrolling: touch; }
      .card-table table { width: 100%; margin: 0; table-layout: fixed; box-sizing: border-box; font-family: 'Dancing Script', cursive; }
      .card-table table thead th { background: #4A3528 !important; color: #FDF8F3 !important; font-weight: 700; padding: 0.6rem 0.75rem; border-color: #5C4033; }
      .card-table table thead th:nth-child(1), .card-table table tbody td:nth-child(1) { width: 8%; }
      .card-table table thead th:nth-child(2), .card-table table tbody td:nth-child(2) { width: 30%; }
      .card-table table thead th:nth-child(3), .card-table table tbody td:nth-child(3) { width: 25%; }
      .card-table table thead th:nth-child(4), .card-table table tbody td:nth-child(4) { width: 10%; }
      .card-table table thead th:nth-child(5), .card-table table tbody td:nth-child(5) { width: 27%; }
      .card-table table tbody td { border-color: #E8DED5; color: #3E2723; }
      .card-graph { height: 100%; min-height: 0; padding: 1rem; overflow: hidden; display: flex; flex-direction: column; }
      .card-graph h5 { font-family: 'Dancing Script', cursive; color: #5C4033; }
      .card-graph > div { flex: 1; min-height: 0; }
      .app-card { background: #FDF8F3; border-radius: 10px; box-shadow: 0 2px 8px rgba(92,64,51,0.12); border: 1px solid #D4C4B0; display: flex; flex-direction: column; }
    "))
  ),
  tags$div(
    class = "screen",
    tags$div(
      class = "screen-top",
      tags$div(
        class = "left-section",
        tags$div(class = "app-card card-title", tags$h2("NYTimes Bestseller Recommendations")),
        tags$div(
          class = "app-card card-filter",
          tags$h5("Filters", class = "mt-0 mb-3 text-muted"),
          tags$div(
            class = "filters-stack",
            selectInput("genre", "Bestseller list", choices = c("Choose a list..." = ""), selected = "", width = "100%"),
            selectInput("filterby", "Sort by", choices = c("Rank (1–15)" = "rank_asc", "Weeks on list (most first)" = "weeks_desc", "Weeks on list (least first)" = "weeks_asc", "Title A–Z" = "title_asc", "Author A–Z" = "author_asc"), selected = "rank_asc", width = "100%")
          )
        )
      ),
      tags$div(
        class = "right-section",
        tags$div(
          class = "app-card card-table",
          tags$h5("Recommendations", class = "mt-0 mb-3"),
          tags$div(class = "table-scroll-wrapper", tableOutput("table_out"))
        )
      )
    ),
    tags$div(
      class = "screen-bottom",
      tags$div(
        class = "app-card card-graph",
        tags$h5("Top 10 — Weeks on list (this list)", class = "mt-0 mb-3"),
        plotOutput("plot_out", height = "280px")
      )
    )
  )
)


# 2. SERVER #############################################################

server = function(input, output, session) {

  # Prefer data/bestsellers.json (from fetch_bestsellers.py); else use API
  bestsellers_cached = reactiveVal(load_bestsellers_file())

  list_options = reactiveVal(NULL)

  load_lists = function() {
    cached = bestsellers_cached()
    if (!is.null(cached) && length(cached$lists) > 0) {
      opts = do.call(rbind, lapply(cached$lists, function(l) {
        data.frame(
          list_name_encoded = as.character(l$list_name_encoded %||% ""),
          list_name = as.character(l$list_name %||% ""),
          stringsAsFactors = FALSE
        )
      }))
      opts = opts %>% filter(nzchar(list_name_encoded), nzchar(list_name))
      list_options(opts)
    } else {
      list_options(get_list_names())
    }
  }

  observe({ load_lists() })

  observeEvent(list_options(), {
    opts = list_options()
    if (is.null(opts) || nrow(opts) == 0) {
      updateSelectInput(session, "genre", choices = c("(No lists — run fetch_bestsellers.py or set NYT_API_KEY)" = ""))
      return(invisible())
    }
    ch = setNames(opts$list_name_encoded, opts$list_name)
    updateSelectInput(session, "genre", choices = ch, selected = ch[1])
  }, ignoreNULL = TRUE)

  # Book data for selected genre: from cache or API
  rec_raw = reactive({
    enc = input$genre
    if (is.null(enc) || !nzchar(enc)) return(NULL)
    cached = bestsellers_cached()
    if (!is.null(cached) && length(cached$lists) > 0) {
      lst = Find(function(l) identical(l$list_name_encoded, enc), cached$lists)
      if (is.null(lst)) return(NULL)
      books = lst$books %||% list()
      if (length(books) == 0) {
        return(data.frame(rank = integer(), title = character(), author = character(), weeks_on_list = integer(), description = character(), publisher = character(), stringsAsFactors = FALSE))
      }
      do.call(rbind, lapply(books, book_to_row))
    } else {
      get_current_list(enc)
    }
  })

  # Sorted/filtered data for table and graph (depends on filterby)
  rec_sorted = reactive({
    data = rec_raw()
    if (is.null(data)) return(NULL)
    fb = input$filterby
    if (is.null(fb) || !nzchar(fb)) fb = "rank_asc"
    out = switch(
      fb,
      rank_asc    = data %>% arrange(rank),
      weeks_desc  = data %>% arrange(desc(weeks_on_list), rank),
      weeks_asc   = data %>% arrange(weeks_on_list, rank),
      title_asc   = data %>% arrange(title),
      author_asc  = data %>% arrange(author),
      data %>% arrange(rank)
    )
    out
  })

  output$table_out = renderTable(
    {
      data = rec_sorted()
      if (is.null(data)) {
        return(data.frame(Message = "Select a bestseller list above. If the dropdown is empty, set NYT_API_KEY in .env at project root."))
      }
      if (nrow(data) == 0) {
        return(data.frame(Message = "No bestsellers in this category this month."))
      }
      data %>%
        select(rank, title, author, weeks_on_list, publisher) %>%
        rename(Rank = rank, Title = title, Author = author, `Weeks on list` = weeks_on_list, Publisher = publisher)
    },
    striped = TRUE,
    hover = TRUE,
    bordered = TRUE
  )

  output$plot_out = renderPlot({
    data = rec_sorted()
    if (is.null(data)) {
      plot(1, type = "n", axes = FALSE, xlab = "", ylab = "")
      text(1, 1, "Select a bestseller list above.", cex = 1.1)
      return(invisible())
    }
    if (nrow(data) == 0) {
      plot(1, type = "n", axes = FALSE, xlab = "", ylab = "")
      text(1, 1, "No bestsellers in this category this month.", cex = 1.1)
      return(invisible())
    }
    top10 = data %>% slice_head(n = 10)
    top10 = top10 %>% mutate(title_short = if (n() > 0) substr(title, 1, 40) else title)
    ggplot(top10, aes(x = reorder(title_short, weeks_on_list), y = weeks_on_list, fill = weeks_on_list)) +
      geom_col(width = 0.7) +
      scale_fill_gradient(low = "#D4C4B0", high = "#5C4033") +
      coord_flip() +
      labs(x = NULL, y = "Weeks on list", title = NULL) +
      theme_minimal(base_size = 12) +
      theme(
        legend.position = "none",
        panel.grid.major.y = element_blank(),
        text = element_text(color = "#3E2723"),
        axis.text = element_text(color = "#5C4033")
      )
  })
}


# 3. RUN ################################################################

shinyApp(ui = ui, server = server)
