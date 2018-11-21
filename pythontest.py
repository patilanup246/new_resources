import os
import traceback
import logging
import facebook
import requests
import pandas as pd
import json
import time
import numpy as np
from pandas.io.json import json_normalize

# This Gist provides code to search the Facebook Graph API for Facebook pages and groups
# that match a specific query list, get the details for each and output the results to CSV.


# ------------------------------------------------------------------------------
## SET DEVELOPER TOKENS

# Note: It's best practice to load api keys from a config file (such as ./bash_profile) to avoid inadvertently
# sharing them to github or making them public.
# See: http://stackoverflow.com/questions/14786072/keep-secret-keys-out-with-environment-variables

# Obtained from https://developers.facebook.com/tools/accesstoken/ == NOTE USE 'USER TOKEN' not APP TOKEN
FB_USER_TOKEN = "EAADLTD5pUYsBAAL8TagaGrTeTfk3IeNbxD3QIlTay859BL7qvd4VFfuxarTtRBZACcMrzXSNo1zFqk2pZCen7gVY2yQmYE8xN0FNZBC92LnTPHzfKAv74mMfP3E5ZC1OZAUYcWO5xms170YfZBZCw2yB9JasWFkoswaNEcxisnltzasUrHSHSgBZAeueQVZAjZBHMZD"

# Obtained from https://developers.facebook.com/
FB_APP_ID = "223528325042571"

# Obtained from https://developers.facebook.com/
FB_APP_SECRET = "3dafdc1bdfcb57d518173cf905e265e2"

# Extend the expiration time of a valid OAuth access token.
# Note: If you are only doing a quick query, you can simply use the short-term token you got above (FB_USER_TOKEN), # and ignore this code. However, it is recommended to get an extended token.
graph = facebook.GraphAPI(FB_USER_TOKEN)
extended_token = graph.extend_access_token(FB_APP_ID, FB_APP_SECRET)
access_token = extended_token['access_token']
print(extended_token)  # verify that it expires in 60 days

# ------------------------------------------------------------------------------
## SET QUERY
# sample url: https://www.facebook.com/search/groups/?q=for%20hillary
# sample api query search?q=for%20hillary&type=group&limit=5000

# In this case, we are querying groups related to the 2016 presidential elections. Each candidate's name, popular slogan and PAC is checked against Facebook's API explorer before running the query to refine the query list. Queries that resulted in empty or innacurate data are removed.

query_list = ['for Hillary', 'Hillary Clinton', 'Priorities USA Action',
              'Donald Trump', 'Trump', 'Make America Great Again', 'OurPrinciplesNeverTrump',
              'Our Principles - For The People'
              'Feel the Bern', 'Bernie', 'Bernie Sanders',
              'Ted Cruz', 'Cruz Crew', 'Courageous Conservatives', 'Club for Growth Action',
              'John Kasich', 'Kasich', 'Marco Rubio', 'A New American Century']


# ------------------------------------------------------------------------------
##  GET GROUPS
# Function to search for all group id's matching a query from Facebook Graph API

def getGroupIds(query):
    graph = facebook.GraphAPI(access_token)
    graph.timeout = 30
    limit = 5000
    result = graph.request("search", {'type': 'group', 'q': query, 'limit': 5000})
    objIds = result['data']
    while 'next' in result.get('paging', {}) and len(result['data']) <= limit:
        result = requests.get(result['paging']['next']).json()
        objIds.extend(result['data'])
    for group in objIds:
        group['query'] = query  # adds query to data returned to allow for tracking
    return (objIds)


# Calling query list on getGroupIds function
all_groups = []
for query in query_list:
    response = getGroupIds(query)
    all_groups.extend(response)
# len(all_groups)

# Convert to dataframe
# group_map = pd.DataFrame(all_groups)
# group_map['type'] = 'group'  # optional: tag as 'page' or 'group'
# group_map.head()
#
# # Check for duplicates
# # Note: Facebook Graph can return duplicates if a query is too similar to another query in a while loop.
# check = group_map[group_map.duplicated()]
# len(check)
#
# # If duplicates...de_dupe
# group_map = group_map.drop_duplicates()
# len(group_map)
#
#
# # Function to get fields associated with object id from Facebook Graph
# def getGroupObject(id):
#     graph = facebook.GraphAPI(access_token)
#     result = graph.get_object(id=id,
#                               fields='name, description, link, owner, parent, privacy, updated_time, icon, cover, members.limit(0).summary(true)')
#     while 'next' in result.get('paging', {}) and len(result['data']) == limit:
#         result = requests.get(result['paging']['next']).json()
#         groups.extend(result['data'])
#     return (result)
#
#
# # Call id list on getGroupObject function
# # Alert: This can be a time consuming query. If you have a large number of id's it is recommended to test this
# # function on a subset of the full list to ensure you get a valid response. (i.e. id_list = group_map['id'][0:5])
# id_list = group_map['id']
# group_info = []
# for id in id_list:
#     response = getGroupObject(id)
#     group_info.append(response)
#
# len(group_info) == len(all_groups)
#
# # Convert to dataframe
# group_dt = json_normalize(group_info)
# drop = ['cover.cover_id', 'cover.offset_x', 'cover.offset_y', 'members.data', ]  # drop unnecessary or duplicate columns
# group_dt = group_dt.drop(drop, axis=1)
# group_dt.head()
#
# # Output to csv
# group_dt.to_csv('INSERT_FILE_NAME.csv', encoding='utf-8')
#
#
# # ------------------------------------------------------------------------------
# ## GET PAGES
#
# # Function to search for all page id's matching a query from Facebook Graph API
# def getPageIds(query):
#     graph = facebook.GraphAPI(access_token)
#     graph.timeout = 30
#     result = graph.request("search", {'type': 'page', 'q': query, 'limit': 5000})
#     objIds = result['data']
#     while 'next' in result.get('paging', {}) and len(result['data']) <= limit:
#         result = requests.get(result['paging']['next']).json()
#         objIds.extend(result['data'])
#     for page in objIds:
#         page['query'] = query
#     return (objIds)
#
#
# # Calling query list on getPageIds function
# all_pages = []
# for query in query_list:
#     response = getPageIds(query)
#     all_pages.extend(response)
# len(all_pages)
#
# # Convert to dataframe to create map between pages and groups
# page_map = pd.DataFrame(all_pages)
# page_map['type'] = 'page'  # optional: tag as 'page' or 'group'
# page_map.head()
#
# # Check for duplicates
# check = page_map[page_map.duplicated()]
# # len(check)
#
# # If duplicates...de_dupe
# page_map = page_map.drop_duplicates()
# # len(page_map)
#
# # Call id list on getPageObject function
# # Alert: This can be a time consuming query. If you have a large number of id's it is recommended to test this
# # function on a subset of the full list to ensure you get a valid response. (i.e. id_list = page_map['id'][0:5])
#
# id_list = page_map['id']
# page_info = []
# for id in id_list:
#     try:
#         response = getPageObject(id)
#         page_info.append(response)
#     except Exception as e:
#         logging.error(traceback.format_exc())
#
# # Test that the API returned details for the full set of ids
# # Note if exceptions or errors were raised, this list may not be complete. Compare sets to identify missing ids
# # len(page_info) == len(all_pages)
#
# # Convert to dataframe
# page_dt = json_normalize(page_info)
# drop = ['cover.cover_id', 'cover.offset_x', 'cover.offset_y']  # drop unnecessary or duplicate columns
# page_dt = page_dt.drop(drop, axis=1)
# page_dt.head()
#
# # Output to csv
# page_dt.to_csv('INSERT_FILE_NAME.csv', encoding='utf-8')