import json
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
DATA_FILE = Path(__file__).parent / "books.json"

SEED = [
    {"id": 1, "title": "Dune", "author": "Frank Herbert", "pages": 412, "current": 412},
    {"id": 2, "title": "The Hobbit", "author": "J.R.R. Tolkien", "pages": 310, "current": 145},
    {"id": 3, "title": "Atomic Habits", "author": "James Clear", "pages": 320, "current": 0},
]


def load_books():
    if not DATA_FILE.exists():
        save_books(SEED)
    return json.loads(DATA_FILE.read_text())


def save_books(books):
    DATA_FILE.write_text(json.dumps(books, indent=2))


def find_book(books, book_id):
    return next((b for b in books if b["id"] == book_id), None)


@app.route("/")
def index():
    books = load_books()
    for b in books:
        b["progress"] = round(b["current"] / b["pages"] * 100) if b["pages"] else 0
    reading = [b for b in books if b["current"] < b["pages"]]
    finished = [b for b in books if b["current"] >= b["pages"]]
    stats = {
        "total": len(books),
        "finished": len(finished),
        "pages_read": sum(b["current"] for b in books),
    }
    return render_template("index.html", reading=reading, finished=finished, stats=stats)


@app.route("/add", methods=["POST"])
def add_book():
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    try:
        pages = max(1, int(request.form.get("pages", 1)))
    except ValueError:
        pages = 1
    if title:
        books = load_books()
        new_id = max((b["id"] for b in books), default=0) + 1
        books.append({"id": new_id, "title": title, "author": author or "Unknown",
                      "pages": pages, "current": 0})
        save_books(books)
    return redirect(url_for("index"))


@app.route("/update/<int:book_id>", methods=["POST"])
def update_progress(book_id):
    books = load_books()
    book = find_book(books, book_id)
    if book:
        try:
            current = int(request.form.get("current", book["current"]))
        except ValueError:
            current = book["current"]
        book["current"] = min(max(0, current), book["pages"])
        save_books(books)
    return redirect(url_for("index"))


@app.route("/finish/<int:book_id>", methods=["POST"])
def finish(book_id):
    books = load_books()
    book = find_book(books, book_id)
    if book:
        book["current"] = book["pages"]
        save_books(books)
    return redirect(url_for("index"))


@app.route("/delete/<int:book_id>", methods=["POST"])
def delete(book_id):
    books = [b for b in load_books() if b["id"] != book_id]
    save_books(books)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
