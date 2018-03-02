# Harvest-Jira Sync

This project is a simple script that help you to Sync your harvest time data with your Jira Worklogs.

# Requirements
- python >= 3
- python lib: datetime
- python lib:

# How to use?
- Go to your harvest account and create a new access token.
- Create the following Env variables with theirs rights values:
 - HARVEST_ACCOUNT_ID
 - HARVEST_ACCESS_TOKEN
- This a simple script, just put it in somewhere in your home directory
- Give execution permissions to the script (`chmod +x harvest-jira-sync.py`)
- Go to your cron file and create a new cron task to execute this script