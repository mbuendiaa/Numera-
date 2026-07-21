# Install Numera Core Platform v0.2

1. Stop the server with `CTRL + C`.

2. Replace your old `backend` folder with this new `backend` folder.

3. Run:

```cmd
cd backend
.venv\Scripts\activate
py -m pip install -e .[dev]
uvicorn numera.main:app --reload --reload-dir src
```

Open:

```text
http://127.0.0.1:8000/docs
```

This version creates:

```text
backend/numera.db
```
