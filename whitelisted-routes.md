Whitelist of endpoints we need:

- ("GET", ("/contacts",)), # For the "me" check, query param handles the logic
- ("GET", ("/folders",)),
- ("GET", ("/spaces", "{spaceId}")),
- ("GET", ("/contacts", "{contactIds}")),
- ("GET", ("/folders", "{folderId}", "tasks")),
- ("GET", ("/tasks", "{taskId}", "attachments")),
- ("GET", ("/folders", "{folderId}", "attachments")),
- ("GET", ("/attachments", "{attachmentId}", "download", "{fileName}")),
