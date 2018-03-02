#!/usr/bin/python3

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

baseUrl = "https://api.harvestapp.com/v2/"

requestHeaders = {
    "User-Agent": "Harvest-Jira Sync",
    "Authorization": "Bearer " + os.environ.get("HARVEST_ACCESS_TOKEN"),
    "Harvest-Account-ID": os.environ.get("HARVEST_ACCOUNT_ID")
}
currentDay = datetime.today()
print(currentDay)
timeEntriesUrlParam = urllib.parse.urlencode({'from': '2018-03-01'})
timeEntriesUrl = baseUrl + "time_entries?%s" % timeEntriesUrlParam

timeEntriesRequest = urllib.request.Request(url=timeEntriesUrl, headers=requestHeaders)
timeEntriesResponse = urllib.request.urlopen(timeEntriesRequest, timeout=5)
timeEntriesResponseBody = timeEntriesResponse.read().decode("utf-8")
timeEntriesJsonResponse = json.loads(timeEntriesResponseBody)

print(json.dumps(timeEntriesJsonResponse, sort_keys=True, indent=4))
