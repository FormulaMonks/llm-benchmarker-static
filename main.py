import sys
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import json

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# SQLite database connection
conn = sqlite3.connect("leaderboard.db")
cursor = conn.cursor()

# Create the leaderboard table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS leaderboard (
        rank INTEGER,
        language_model TEXT,
        knowledge FLOAT,
        reasoning FLOAT,
        discipline FLOAT,
        understanding FLOAT
    )
""")
conn.commit()

# Routes
@app.get("/", response_class=HTMLResponse)
def get_leaderboard(request: Request):
    return templates.TemplateResponse("leaderboard.html", {"request": request})

@app.get("/api/leaderboard")
def get_leaderboard_data():
    cursor.execute("SELECT * FROM leaderboard ORDER BY rank")
    data = cursor.fetchall()
    leaderboard = []
    for row in data:
        leaderboard.append({
            "rank": row[0],
            "languageModel": row[1],
            "knowledge": row[2],
            "reasoning": row[3],
            "discipline": row[4],
            "understanding": row[5]
        })
    return leaderboard

# Add sample data to the leaderboard table
sample_data = [
    (1, "GPT-3.5", 9.5, 9.2, 9.3, 9.4),
    (2, "GPT-3", 9.2, 9.1, 9.2, 9.3),
    (3, "GPT-2", 8.8, 8.7, 8.9, 8.8)
]
cursor.executemany("INSERT INTO leaderboard VALUES (?, ?, ?, ?, ?, ?)", sample_data)
conn.commit()
cursor.close()
conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8000

    uvicorn.run("main:app", host="0.0.0.0", port=port)
