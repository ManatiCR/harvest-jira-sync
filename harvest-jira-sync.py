#!/usr/bin/python3

import os
import json
import urllib.request
import urllib.parse
import sqlite3
import re
import logging
import base64
from datetime import date
from datetime import datetime
from urllib.error import URLError, HTTPError

# Logging configuration.
logger = logging.getLogger('harvest-jira-sync')
loggingHanlder = logging.FileHandler('harvest-jira-sync.log')
loggingFormatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
loggingHanlder.setFormatter(loggingFormatter)
logger.addHandler(loggingHanlder)
logger.setLevel(logging.WARNING)

# Database connection with the sqlite file.
databaseConnection = sqlite3.connect('harvest-jira-sync.db')
databaseConnection.row_factory = sqlite3.Row
databaseCursor = databaseConnection.cursor()

# Regex to get the Jira ID in the Harvest entry description.
jiraIdRegex = re.compile('[A-Z]+\-\d+')

# Harvest Time entries requests headers.
harvestBaseUrl = "https://api.harvestapp.com/v2/"
harvestRequestHeaders = {
    "User-Agent": "Harvest-Jira Sync",
    "Authorization": "Bearer " + os.environ.get("HARVEST_ACCESS_TOKEN"),
    "Harvest-Account-ID": os.environ.get("HARVEST_ACCOUNT_ID")
}

# Jira requests Headers.
jiraBaseUrl = "https://" + os.environ.get("JIRA_SITE_DOMAIN") + "/rest/api/2/"
jiraCredentials = os.environ.get("JIRA_USER") + ":" +os.environ.get("JIRA_API_TOKEN")
jiraEncodedCredentials = base64.b64encode(jiraCredentials.encode('utf8'))
jiraRequestGetHeaders = {
    "Authorization": "Basic " + jiraEncodedCredentials.decode(),
    "Accept": "application/json"
}

jiraRequestPostHeaders = {
    "Authorization": "Basic " + jiraEncodedCredentials.decode(),
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def getHarvestEntryJiraWorklogRelation(harvestEntryId):
    """Helper function get the relation between the Harvest entry and the Jira worklog"""
    harvestEntryId = str(harvestEntryId)
    databaseCursor.execute("SELECT jira_worklog_id, harvest_entry_id FROM harvest_entries_jira_worklog_map WHERE harvest_entry_id=?", [harvestEntryId])
    result = databaseCursor.fetchone()
    if not result:
        result = False
    else:
        return result

def getJiraWorklogById(jiraId, worklogId):
    """Check if already exist a jira worklog with this id"""
    jiraIssueUrl = jiraBaseUrl + "issue/" + jiraId + "/worklog/" + worklogId
    jiraIssueRequest = urllib.request.Request(url=jiraIssueUrl, headers=jiraRequestGetHeaders)
    try:
        jiraIssuesResponse = urllib.request.urlopen(jiraIssueRequest, timeout=5)
    except HTTPError as error:
        logger.error("In getJiraWorklogById() function, description: " + str(error))
        return False
    else:
        jiraIssueResponseBody = jiraIssuesResponse.read().decode("utf-8")
        jiraIssueJsonResponse = json.loads(jiraIssueResponseBody)
        return jiraIssueJsonResponse['id']

def getJiraIssueById(jiraId):
    """Check if already exist a jira issue with this id"""
    jiraIssueUrl = jiraBaseUrl + "issue/" + jiraId
    jiraIssueRequest = urllib.request.Request(url=jiraIssueUrl, headers=jiraRequestGetHeaders)
    try:
        jiraIssuesResponse = urllib.request.urlopen(jiraIssueRequest, timeout=5)
    except HTTPError as error:
        logger.error("In getJiraIssueById() function, description: " + str(error))
        return False
    else:
        jiraIssueResponseBody = jiraIssuesResponse.read().decode("utf-8")
        jiraIssueJsonResponse = json.loads(jiraIssueResponseBody)
        return jiraIssueJsonResponse['id']

def createJiraWorklog(harvestEntry, jiraIssueId):
    """Helper functon to create a new worklog in one specific Jira issue"""
    worklogDescription = "author: " + harvestEntry['user']['name'] + " "
    worklogDescription += "hours: " + str(harvestEntry['hours']) +  " "
    worklogDescription += "Description: " + str(harvestEntry['notes'])
    worklog = {
    'comment': worklogDescription,
    'issueId': jiraIssueId,
    'timeSpentSeconds': harvestEntry['hours']*3600
    }
    jiraWorklogUrl = jiraBaseUrl + "issue/" + str(jiraIssueId) + "/worklog"
    encodedData = json.dumps(worklog).encode('utf8')
    jiraWorklogRequest = urllib.request.Request(url=jiraWorklogUrl, data=encodedData, headers=jiraRequestPostHeaders, origin_req_host=None, unverifiable=False, method='POST')
    try:
        jiraWorklogResponse = urllib.request.urlopen(jiraWorklogRequest, timeout=5)
    except HTTPError as error:
        logger.error("In request, createJiraWorklog function " + str(error))
        return False
    else:
        jiraWorklogResponseBody = jiraWorklogResponse.read().decode("utf-8")
        jiraWorklogJsonResponse = json.loads(jiraWorklogResponseBody)
        harvestJiraRelation = [jiraWorklogJsonResponse['id'], harvestEntry['id']]
        try:
            databaseCursor.execute("INSERT INTO harvest_entries_jira_worklog_map VALUES (?,?)", harvestJiraRelation)
            databaseConnection.commit()
        except sqlite3.Error as error:
            logger.error("In sqlite INSERT in createJiraWorklog() function, description: " + str(error))
        else:
            return jiraWorklogJsonResponse['id']


def updateJiraWorklog(harvestEntry, jiraIssueId, jiraWorklogId):
    """Helper function to Update a specific Jira Worklog"""
    jiraWorklogId = str(jiraWorklogId)
    worklogDescription = "author: " + str(harvestEntry['user']['name']) + " "
    worklogDescription += "hours: " + str(harvestEntry['hours']) +  " "
    worklogDescription += "Description: " + str(harvestEntry['notes'])
    worklog = {
    'id': jiraWorklogId,
    'comment': worklogDescription,
    'issueId': jiraIssueId,
    'timeSpentSeconds': harvestEntry['hours']*3600
    }
    jiraWorklogUpdateUrl = jiraBaseUrl + "issue/" + str(jiraIssueId) + "/worklog/" + jiraWorklogId
    encodedData = json.dumps(worklog).encode('utf8')
    jiraWorklogUpdateRequest = urllib.request.Request(url=jiraWorklogUpdateUrl, data=encodedData, headers=jiraRequestPostHeaders, origin_req_host=None, unverifiable=False, method='PUT')
    try:
        jiraWorklogUpdateResponse = urllib.request.urlopen(jiraWorklogUpdateRequest, timeout=5)
    except HTTPError as error:
        logger.error("In updateJiraWorklog() function, description: " + str(error))
        return False
    else:
        jiraWorklogUpdateResponseBody = jiraWorklogUpdateResponse.read().decode("utf-8")
        jiraWorklogUpdateJsonResponse = json.loads(jiraWorklogUpdateResponseBody)
        return  jiraWorklogUpdateJsonResponse['id']

# Processing the Harvest time entries and creating the Jira Worklogs.
timeEntriesUrlParam = urllib.parse.urlencode({'updated_since': date.today()})
timeEntriesUrl = harvestBaseUrl + "time_entries?%s" % timeEntriesUrlParam
timeEntriesRequest = urllib.request.Request(url=timeEntriesUrl, headers=harvestRequestHeaders)
try:
    timeEntriesResponse = urllib.request.urlopen(timeEntriesRequest, timeout=5)
except HTTPError as error:
    logger.error("Getting the harvest time entries, description: " + str(error))
else:
    timeEntriesResponseBody = timeEntriesResponse.read().decode("utf-8")
    timeEntriesJsonResponse = json.loads(timeEntriesResponseBody)
    for entry in timeEntriesJsonResponse['time_entries']:
        if 'notes' in entry and isinstance(entry['notes'], str):
            jiraIdMatch = jiraIdRegex.match(entry['notes'])
            if jiraIdMatch:
                jiraId = jiraIdMatch.group()
                jiraIssueId = getJiraIssueById(jiraId)
                if jiraIssueId:
                    relation = getHarvestEntryJiraWorklogRelation(entry['id']);
                    if relation:
                        updatedWorlog = updateJiraWorklog(entry, jiraIssueId, relation['jira_worklog_id'])
                    else:
                        jiraWorklogId = createJiraWorklog(entry, jiraIssueId)

databaseConnection.close()
