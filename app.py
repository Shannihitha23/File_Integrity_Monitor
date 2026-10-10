
from flask import Flask, render_template, redirect, url_for, flash
from integrity import create_baseline, check_integrity

app = Flask(__name__)
app.secret_key = "change-this-to-a-random-secret-for-local-use"


@app.route("/")
def home():
    report = check_integrity()
    return render_template("index.html", report=report)


@app.route("/baseline", methods=["POST"])
def baseline():
    count = create_baseline()
    flash(f"Baseline created successfully for {count} file(s).")
    return redirect(url_for("home"))


@app.route("/check", methods=["POST"])
def check():
    report = check_integrity()

    if report is None:
        flash("Create a baseline before checking file integrity.")
    else:
        flash("Integrity check completed.")

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
