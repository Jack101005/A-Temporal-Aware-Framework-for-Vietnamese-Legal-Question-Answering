# Setup Guide (macOS) — Get PostgreSQL + pgvector running

Follow these steps in order. Each step is one command.

## 1. Install PostgreSQL (via Homebrew)

```bash
brew install postgresql@16
brew services start postgresql@16
```

Check it works:
```bash
psql --version
```

## 2. Install pgvector (the vector-search extension)

```bash
brew install pgvector
```

(If brew can't find it, you can build from source — but on recent Homebrew
`brew install pgvector` works.)

## 3. Create your database

```bash
createdb vn_legal
```

## 4. Set up the Python environment

In the project folder:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 5. Tell the code how to reach the database

The default connection in `configs/settings.py` is:
```
postgresql://localhost/vn_legal
```
On most Mac Homebrew installs this works as-is. If your Postgres needs a
username, set it instead:
```bash
export DATABASE_URL="postgresql://YOUR_MAC_USERNAME@localhost/vn_legal"
```

## 6. Run the setup + sanity check

```bash
python scripts/setup_db.py
```

EXPECTED OUTPUT:
```
2021-05-01: ['ND_90_2019']
2023-03-01: ['ND_38_2022']
2026-06-08: ['ND_74_2024']
```

If you see exactly one decree per date, the core temporal logic works.
That is the foundation of the entire thesis — you can show this to Dr. Tam.

## 7. (Later) Add embeddings

Once the above works, the next step is embedding the documents with PhoBERT
so we can search by meaning. We'll write that script together next.


## 8. How can we run it

~/Desktop/vn-legal-rag/start_all.sh

it will run 3 files 

1) Ollama
2) The uvicorn
3) The UI

=> They will all run at the same time 
