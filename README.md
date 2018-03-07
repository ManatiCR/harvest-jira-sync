# Harvest-Jira Sync

This project is a simple script that help you to Sync your harvest time data with your Jira Worklogs.

# Requirements
- sqlite >= 3
- python >= 3

# How to use?
- Go to your harvest account and create a new access token.
- Go to your Jira Account and generate a new API token.
- Create the environment variables specified in the `.env.example` with theirs rights values or copy to .env and use `source .env` to import it.
- Give execution permissions to the script (`chmod +x harvest-jira-sync.py`).
- Go to the root folder of the `harvest-jira-sync.py` script and execute the following commands to create and import your sqlite database:
   ```
   sqlite3 harvest-jira-sync.db
   sqlite> .read databaseSchema.sql
   ```
   or
   ```
  cat databaseSchema.sql | sqlite3 harvest-jira-sync.db
  ```
- Go to your cron file and create a new cron task to execute this script.
  ```
  0 22 * * * cd $HOME/harvest-jira-integration/ && ./harvest-jira-sync.py
  ```

# Debugging

If you are having some unexpected behaivor you could take a look in the log file for this script, the log file will be created automatically on error in the same root path of the `harvest-jira-sync.py` script.
