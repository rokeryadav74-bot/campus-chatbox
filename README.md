# Campus Chatbox
A student-community chat web app built with Python, Flask, SQLite, HTML, CSS and JavaScript.

## Deploy on Render
1. Upload this project folder to a GitHub repository.
2. On Render, create a new Web Service and connect that repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Set an environment variable `SECRET_KEY` to a long random value.
6. Deploy and open the generated URL.

## Important limitation
This starter uses SQLite. Render's free web-service filesystem is ephemeral, so database contents may be lost on restart, redeploy, or spin-down. Use a persistent database such as PostgreSQL before relying on the site for real users.

## Local run (optional)
`python app.py`
