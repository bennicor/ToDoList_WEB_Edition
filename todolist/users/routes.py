from datetime import datetime, timedelta
from itertools import groupby
from flask import (Blueprint, Flask, flash, redirect, render_template, request,
                   session, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from todolist import db_session
from todolist.helpers import save_picture, weekdays
from todolist.models import Task, User
from todolist.tasks.forms import TaskForm
from todolist.users.forms import LoginForm, RegistrationForm, UpdateAccountForm
from todolist.db.db_user_queries import create_user, get_user
from todolist.db.db_tasks_queries import (get_today_tasks, get_upcoming_tasks,
                                          get_weekly_completed_tasks, get_all_completed, add_task)


users = Blueprint('users', __name__)


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users.tasks"))

    form = RegistrationForm()

    if form.validate_on_submit():
        # Если пользователь не загрузил собственную фотографию
        # Выбирается фотография по умолчанию
        if form.image_file.data:
            picture_file = save_picture(form.image_file.data)
        else:
            picture_file = "default.jpg"

        user = create_user(name=form.name.data,
                           email=form.email.data,
                           password=form.password.data,
                           profile_image=picture_file)
        return redirect(url_for("users.login"))
    return render_template("register.html", title="Register", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.tasks"))

    form = LoginForm()

    if form.validate_on_submit():
        user, _ = get_user(email=form.email.data)

        # Проверяем если пользователь есть в базе данных и пароли совпадают
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            flash("You have been logged in!", "info")
            return redirect(next_page) if next_page else redirect(url_for("users.tasks"))
        flash("Incorrect email or password!", "danger")
        return render_template("login.html", form=form)
    return render_template('login.html', title='Authorization', form=form)


@users.route("/logout", methods=["GET", "POST"])
def logout():
    flash(f"You have been logged out, {current_user.name}!", "info")
    logout_user()
    return redirect(url_for("main.index"))


@users.route("/projects", methods=["GET", "POST"])
def projects():
    return render_template("projects.html")


@users.route("/tasks/today", methods=["GET", "POST"])
@login_required
def tasks():
    # Сохраняем url страницы
    session["url"] = url_for("users.tasks")

    # Добавляем задачу из modal формы
    form = TaskForm()

    if form.validate_on_submit():
        add_task(form, current_user)
        return redirect(session.get("url"))

    tasks = get_today_tasks(current_user)

    return render_template("index.html", title="Today's Tasks", tasks=tasks, form=form, today=datetime.now().date())


@users.route("/tasks/upcoming", methods=["GET", "POST"])
@login_required
def upcoming_tasks():
    # Сохраняем url страницы
    session["url"] = url_for("users.upcoming_tasks")

    # Добавляем задачу из modal формы
    form = TaskForm()

    if form.validate_on_submit():
        add_task(form, current_user)
        return redirect(session.get("url"))

    tasks = get_upcoming_tasks(current_user)

    # Группируем задачи по дате
    data = {}
    for key, group in groupby(tasks, key=lambda x: x.scheduled_date):
        data[key.strftime("%d.%m.%Y")] = [thing for thing in group]

    return render_template('upcoming_tasks.html', title="Upcoming Tasks", tasks=data, form=form, today=datetime.now().date())


@users.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    # Находим дату недельной давности
    last_week_date = datetime.now().date() - timedelta(6)

    # Запрашиваем количество выполненных задач за последнуюю неделю
    tasks = get_weekly_completed_tasks(current_user, last_week_date)

    # Заполняем статистику пустыми значениями
    data = weekdays(datetime.now().strftime("%A"))
    for group, val in tasks:
        data[group.strftime("%A")] = val

    completed_tasks = get_all_completed(current_user)

    # Загружаем фотографию профиля пользователя
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)

    return render_template('dashboard.html', title="Dashboard", tasks=data, completed=completed_tasks, image_file=image_file)


@users.route("/update_account", methods=["GET", "POST"])
@login_required
def update_account():
    form = UpdateAccountForm()

    # Если пользователь получает данные, то заполняем форму текующими данными о профиле
    if request.method == "GET":
        form.name.data = current_user.name
        form.email.data = current_user.email

    # Если форма готова к отправке, обновляем информацию на актульную
    if form.validate_on_submit():
        user, db_sess = get_user(current_user)

        # Если пользователь заменил фотографию - меняем ее
        if form.image_file.data:
            picture = save_picture(form.image_file.data)
            user.image_file = picture

        user.name = form.name.data.strip()
        user.email = form.email.data.strip()

        db_sess.commit()
        flash("Account info has been successfully changed!", "success")
        # Перенаправляет на странице профиля
        return redirect(url_for("users.dashboard"))
    # Получаем путь к фотографии пользователя
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)

    return render_template('update_account.html', title='Edit Account Info', form=form)
