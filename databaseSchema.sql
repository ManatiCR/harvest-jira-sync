CREATE TABLE harvest_entries_jira_task_map (
  jira_task_id varchar(30),
  harvest_entry_id varchar(30),
  PRIMARY KEY (harvest_entry_id)
);
