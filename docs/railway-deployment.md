# Railway deployment

## Deploy the web service

1. Push the project to GitHub and create a Railway project from that repository.
   Railway detects the `Procfile` and starts Flask with Gunicorn.
2. Add a Railway MySQL service to the project.
3. Attach a persistent volume to the web service at `/data`. Set
   `PORTAL_STATE_FILE=/data/portal_state.json`; this file contains user and
   grievance records. Do not copy the local `database/portal_state.json` into
   production when creating a clean instance.
4. Add these variables to the web service, replacing `MySQL` if the database
   service has a different name:

   ```text
   FLASK_SECRET_KEY=<new random secret>
   PORTAL_STATE_FILE=/data/portal_state.json
   MYSQL_HOST=${{MySQL.MYSQLHOST}}
   MYSQL_PORT=${{MySQL.MYSQLPORT}}
   MYSQL_USER=${{MySQL.MYSQLUSER}}
   MYSQL_PASSWORD=${{MySQL.MYSQLPASSWORD}}
   MYSQL_DATABASE=${{MySQL.MYSQLDATABASE}}
   ```

   Generate a unique Flask secret; never reuse the local secret or commit it.
   Railway service-reference variables let the database credentials remain
   private.
5. Deploy. From the running web-service shell, run
   `python scripts/init_database.py` once to create the evidence table.
6. Create the first administrator from that same service shell by running
   `python scripts/create_admin.py`. Enter a unique username, a valid email,
   and a unique password of at least 12 characters when prompted. The password
   is hashed before it is stored. Public registration only creates student
   accounts.
7. Open the generated Railway domain and verify registration, login, and
   grievance submission. The evidence test requires the MySQL service to be
   reachable.

## Optional integrations

- Add the Gmail SMTP settings (`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USERNAME`,
  `EMAIL_PASSWORD`, `EMAIL_FROM`, `EMAIL_USE_TLS=true`, and
  `EMAIL_USE_SSL=false`) as Railway service variables if email notifications
  are needed. Use a Gmail app password, not the account password.
- Set `OLLAMA_BASE_URL` to a reachable hosted Ollama-compatible endpoint if
  open-ended chatbot responses should use a model. The default
  `127.0.0.1:11434` only refers to the web-service container; it does not reach
  a developer's computer. Direct grievance-status lookup and official
  UNIZULU website search do not depend on Ollama.
- The Railway domain uses HTTPS. Keep `FLASK_SECRET_KEY`, database credentials,
  SMTP credentials, and any model endpoint tokens in Railway's variable manager.
