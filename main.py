
from flask import Flask, render_template

app = Flask(__name__, template_folder="template")

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/service")
def service():
    return render_template("service.html")

if __name__ == "__main__":
    app.run(debug=True) 