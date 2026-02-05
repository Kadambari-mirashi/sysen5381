# test_requests.py
# Test HTTP Requests
# Tim Fraser

# Brief 2-3 sentence description of what this script teaches.
# What will students learn? Why is it useful?

# 0. Setup #################################

## 0.1 Load Packages ############################

# import requests  # for making HTTP requests
# import json  # for working with JSON data

## 0.2 Configuration ############################

# Add any configuration variables here

# 1. Main Code ###################################


import requests

url = "https://httpbin.org/post"
data = {"name": "test"}

response = requests.post(url, json=data)

print(response.status_code)
print(response.json())
