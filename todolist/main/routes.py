from flask import Flask, render_template, redirect, url_for, Blueprint
from flask_login import current_user

main = Blueprint('main', __name__)


@main.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("users.tasks"))
    return render_template("main.html")
