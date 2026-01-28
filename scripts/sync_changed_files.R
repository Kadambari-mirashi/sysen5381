#!/usr/bin/env Rscript
# Sync Changed Files to Canvas
# 
# This script syncs changed assignment files to Canvas using the canvastest module.
# It reads a list of changed files and only syncs those with github_path mappings
# in assignments_metadata.json.
#
# Usage:
#   Rscript sync_changed_files.R <changed_files.txt> [config_file] [metadata_file]
#
# Arguments:
#   changed_files.txt - Path to file containing list of changed files (one per line)
#   config_file - Optional path to course_config.json (default: ../../course_config.json)
#   metadata_file - Optional path to assignments_metadata.json (default: ../assignments_metadata.json)

# Get command line arguments
args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 1) {
  stop("Usage: Rscript sync_changed_files.R <changed_files.txt> [config_file] [metadata_file]")
}

changed_files_path <- args[1]
config_file <- if (length(args) >= 2) args[2] else "course_config.json"
metadata_file <- if (length(args) >= 3) args[3] else "canvastest/assignments_metadata.json"

# Store original working directory (should be repo root)
repo_root <- getwd()

# Set working directory to canvastest/R
# Script should be run from repository root
if (file.exists("canvastest/R")) {
  setwd("canvastest/R")
} else if (file.exists("../canvastest/R")) {
  setwd("../canvastest/R")
  repo_root <- normalizePath(file.path("..", ".."))
} else {
  stop("Cannot find canvastest/R directory. Please run from repository root.")
}

# Resolve paths relative to repo root (make absolute for file.exists checks)
# All paths passed to script are relative to repo root
if (!startsWith(changed_files_path, "/")) {
  changed_files_path <- file.path(repo_root, changed_files_path)
}
if (!startsWith(metadata_file, "/")) {
  metadata_file <- file.path(repo_root, metadata_file)
}
# Store original config_file for path adjustment
config_file_orig <- config_file

# Load required scripts
message("Loading canvastest module...")
source("config.R")
source("sync_single_page.R")
library(jsonlite)

# Load changed files list
if (!file.exists(changed_files_path)) {
  stop(paste("Changed files list not found:", changed_files_path))
}

changed_files <- readLines(changed_files_path, warn = FALSE)
changed_files <- changed_files[changed_files != ""]

if (length(changed_files) == 0) {
  message("No changed files to process")
  quit(status = 0)
}

message(paste("Found", length(changed_files), "changed file(s)"))

# Load assignments metadata
if (!file.exists(metadata_file)) {
  stop(paste("assignments_metadata.json not found:", metadata_file))
}

metadata <- fromJSON(metadata_file, simplifyDataFrame = FALSE)

# Filter to files with github_path mappings
files_to_sync <- c()
for (file in changed_files) {
  # Check if this file has a github_path mapping
  found <- FALSE
  for (assignment in metadata) {
    if (!is.null(assignment$github_path) && assignment$github_path == file) {
      files_to_sync <- c(files_to_sync, file)
      found <- TRUE
      message(paste("Found mapping for:", file, "-> Assignment ID:", assignment$id))
      break
    }
  }
  if (!found) {
    message(paste("Skipping", file, "- no github_path mapping found in metadata"))
  }
}

if (length(files_to_sync) == 0) {
  message("No changed files have github_path mappings. Nothing to sync.")
  quit(status = 0)
}

message(paste("\n=== Syncing", length(files_to_sync), "file(s) to Canvas ==="))

# Sync each file
results <- list()
for (file in files_to_sync) {
  message(paste("\n", "=", rep("=", 50), sep = ""))
  message(paste("Syncing:", file))
  message(paste(rep("=", 52), sep = ""))
  
  tryCatch({
    # config_file_orig is relative to repo root (e.g., "course_config.json")
    # sync_single_page runs from canvastest/R, so we need relative path from here
    # From canvastest/R, repo root is ../../
    config_rel <- file.path("..", "..", config_file_orig)
    
    result <- sync_single_page(
      github_path = file,
      config_file = config_rel,
      metadata_file = metadata_file,
      dry_run = FALSE,
      verify = FALSE
    )
    results[[file]] <- list(success = TRUE, result = result)
    message(paste("✓ Successfully synced:", file))
  }, error = function(e) {
    results[[file]] <<- list(success = FALSE, error = e$message)
    message(paste("✗ Failed to sync", file, ":", e$message))
  })
}

# Summary
message(paste("\n", "=", rep("=", 50), sep = ""))
message("SYNC SUMMARY")
message(paste(rep("=", 52), sep = ""))

success_count <- sum(sapply(results, function(r) r$success))
total_count <- length(results)

for (file in names(results)) {
  if (results[[file]]$success) {
    message(paste("✓", file))
  } else {
    message(paste("✗", file, "-", results[[file]]$error))
  }
}

message(paste("\nSynced", success_count, "of", total_count, "file(s)"))

# Exit with error if any failed
if (success_count < total_count) {
  quit(status = 1)
} else {
  quit(status = 0)
}
