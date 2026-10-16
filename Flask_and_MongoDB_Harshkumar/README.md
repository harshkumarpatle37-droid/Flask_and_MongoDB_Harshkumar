# Flask & MongoDB Assignment

Flask app with a JSON API route (`/api`, data read from `data.json`) and a frontend form that stores
submissions in MongoDB Atlas. Success redirects to `/success` ("Data submitted successfully");
errors are shown on the same page without redirect.

GitHub: https://github.com/harshkumarpatle37-droid/project_using_flask_-_mongodb_REst-API

## Run
```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # then put your Atlas MONGO_URI in .env
python app.py                                        # http://127.0.0.1:5000
```
- `http://127.0.0.1:5000/api` -> JSON list
- `http://127.0.0.1:5000/`    -> form

## Tests
```bash
pip install mongomock pytest && pytest -v
```
