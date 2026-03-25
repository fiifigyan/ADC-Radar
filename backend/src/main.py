from flask import Flask, render_template

from src.database.local_db import LocalDB

app = Flask(__name__)

@app.route("/")
def index():
    db = LocalDB()
    opportunities = db.get_all_opportunities()
    return render_template("index.html", opportunities=opportunities)

if __name__ == "__main__":
    app.run(debug=True)
