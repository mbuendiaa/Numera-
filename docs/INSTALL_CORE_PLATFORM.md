# Install Numera Core Platform v0.1

Copy the `backend` folder into your Numera repository.

Then run:

```cmd
cd backend
py -m venv .venv
.venv\Scripts\activate
py -m pip install -e .[dev]
uvicorn numera.main:app --reload
```

Test:

```cmd
pytest
```

Open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```
