# Install Numera Core Platform v0.3

1. Stop the server with `CTRL + C`.

2. Replace your old `backend` folder with this new `backend` folder.

3. Run:

```cmd
cd backend
.venv\Scripts\activate
py -m pip install -e .[dev]
uvicorn numera.main:app --reload --reload-dir src
```

4. Open:

```text
http://127.0.0.1:8000/docs
```

New endpoint:

```text
POST /documents/upload
```

Use:
- `company_id`
- `file`

This version creates:
- `backend/numera.db`
- `backend/uploads/<company_id>/<filename>`
