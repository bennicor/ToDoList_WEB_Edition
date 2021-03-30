from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)

# Обработчики ошибок
@errors.errorhandler(404)
def error_404(e):
    return render_template("errors/404.html"), 404

@errors.errorhandler(401)
def error_401(e):
    return render_template("errors/401.html"), 401
