CREATE TABLE harvest_entries_jira_worklog_map (
  jira_worklog_id varchar(30),
  harvest_entry_id varchar(30),
  PRIMARY KEY (harvest_entry_id)
);
