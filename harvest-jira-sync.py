#!/usr/bin/python3

import os
import json
import urllib.request
import urllib.parse
import sqlite3
import re
import base64
from datetime import date
from datetime import datetime
from urllib.error import URLError, HTTPError

# Database connection with the sqlite file.
databaseConnection = sqlite3.connect('harvest-jira-sync.db')
databaseCursor = databaseConnection.cursor()

# Regex to get the Jira ID in the Harvest entry description.
jiraIdRegex = re.compile('^[A-Z]+\-\d+')

# Harvest Time entries request params.
harvestBaseUrl = "https://api.harvestapp.com/v2/"
harvestRequestHeaders = {
    "User-Agent": "Harvest-Jira Sync",
    "Authorization": "Bearer " + os.environ.get("HARVEST_ACCESS_TOKEN"),
    "Harvest-Account-ID": os.environ.get("HARVEST_ACCOUNT_ID")
}
timeEntriesUrlParam = urllib.parse.urlencode({'updated_since': date.today()})
timeEntriesUrl = harvestBaseUrl + "time_entries?%s" % timeEntriesUrlParam
timeEntriesRequest = urllib.request.Request(url=timeEntriesUrl, headers=harvestRequestHeaders)
timeEntriesResponse = urllib.request.urlopen(timeEntriesRequest, timeout=5)
timeEntriesResponseBody = timeEntriesResponse.read().decode("utf-8")
timeEntriesJsonResponse = json.loads(timeEntriesResponseBody)

# Jira request params.
jiraBaseUrl = "https://manati.atlassian.net/rest/api/2/"
jiraCredentials = os.environ.get("JIRA_USER") + ":" +os.environ.get("JIRA_API_TOKEN")
jira_encoded_credentials = base64.b64encode(jiraCredentials.encode('utf8'))
jiraRequestHeaders = {
    "Authorization": "Basic " + jira_encoded_credentials.decode(),
    "Accept": "application/json"
}

def getHarvestEntryJiraWorklogRelation(harvestEntryId):
    """Helper function get the relation between the Harvest entry and the Jira worklog"""
    harvestEntryId = str(harvestEntryId)
    print(harvestEntryId)
    databaseCursor.execute("SELECT jira_worklog_id, harvest_entry_id FROM harvest_entries_jira_worklog_map WHERE harvest_entry_id=?", [harvestEntryId])
    result = databaseCursor.fetchone()
    if not result:
        result = False
    return result

def getJiraWorklogById(jiraId, worklogId):
    """Check already exist a jira worklog with this id"""
    jiraIssueUrl = jiraBaseUrl + "issue/" + jiraId + "/worklog/" + worklogId
    jiraIssueRequest = urllib.request.Request(url=jiraIssueUrl, headers=jiraRequestHeaders)
    try:
        jiraIssuesResponse = urllib.request.urlopen(jiraIssueRequest, timeout=5)
    except HTTPError as error:
        return False
    else:
        jiraIssueResponseBody = jiraIssuesResponse.read().decode("utf-8")
        jiraIssueJsonResponse = json.loads(jiraIssueResponseBody)
        return jiraIssueJsonResponse['id']

def getJiraIssueById(jiraId):
    """Check already exist a jira issue with this id"""
    jiraIssueUrl = jiraBaseUrl + "issue/" + jiraId
    jiraIssueRequest = urllib.request.Request(url=jiraIssueUrl, headers=jiraRequestHeaders)
    try:
        jiraIssuesResponse = urllib.request.urlopen(jiraIssueRequest, timeout=5)
    except HTTPError as error:
        return False
    else:
        jiraIssueResponseBody = jiraIssuesResponse.read().decode("utf-8")
        jiraIssueJsonResponse = json.loads(jiraIssueResponseBody)
        return jiraIssueJsonResponse['id']

def createJiraWorklog():
    """Helper functon to create a new worklog in one specific Jira issue"""


for entry in timeEntriesJsonResponse['time_entries']:
    if 'notes' in entry and isinstance(entry['notes'], str):
        jiraIdMatch = jiraIdRegex.match(entry['notes'])
        if jiraIdMatch:
            jiraId = jiraIdMatch.group()
            jiraIssueId = getJiraIssueById(jiraId)
            if jiraIssueId:
                relation = getHarvestEntryJiraWorklogRelation(entry['id']);
                if relation:
                    print(relation)
                else:
                    print('not related')
                    jiraWorklogId = createJiraWorklog(entry[''])

databaseConnection.close()
