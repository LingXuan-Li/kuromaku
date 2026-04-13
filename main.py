from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/exit")
def appexit():
    os._exit(0)

@app.route("/edit")
def edit():
    return render_template("edit.html")

if __name__ == "__main__":
    app.run(debug=True)