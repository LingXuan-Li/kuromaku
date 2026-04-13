from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("dashboard.html")

@app.route("/exit")
def appexit():
    os.exit(0)


if __name__ == "__main__":
    app.run(debug=True)