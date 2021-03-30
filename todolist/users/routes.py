from flask import Flask, render_template, redirect, url_for, request, session, Blueprint, flash
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime, timedelta
from todolist.models import User, Task
from itertools import groupby
from todolist.helpers import weekdays
from todolist.users.forms import RegistrationForm, LoginForm
from todolist import db_session
from sqlalchemy import func

users = Blueprint('users', __name__)


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users.tasks"))

    form = RegistrationForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect(url_for("users.login"))
    return render_template("register.html", title="Register", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.tasks"))

    form = LoginForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        # Проверяем если пользователь есть в базе данных и пароли совпадают
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            flash("You have been logged in!", "info")
            return redirect(next_page) if next_page else redirect(url_for("users.tasks"))
        flash("Incorrect email or password!", "error")
        return render_template("login.html", form=form)
    return render_template('login.html', title='Authorization', form=form)


@users.route("/logout", methods=["GET", "POST"])
def logout():
    flash(f"You have been logged out, {current_user.name}!", "info")
    logout_user()
    return redirect(url_for("main.index"))


@users.route("/tasks/today", methods=["GET", "POST"])
@login_required
def tasks():
    # Сохраняем url страницы
    session["url"] = url_for("users.tasks")

    db_sess = db_session.create_session()
    # Запрашиваем только задачи, созданные этим пользователем
    # и дата которых совпадает с сегодняшним днем, 
    # отсортированные по приоритету и алфавиту
    tasks = db_sess.query(Task).filter(Task.user_id == current_user.id,
                                        Task.scheduled_date == datetime.now().date()).order_by(Task.priority, Task.title).all()

    return render_template("index.html", title="Today's Tasks", tasks=tasks)


@users.route("/tasks/upcoming", methods=["GET", "POST"])
@login_required
def upcoming_tasks():
    # Сохраняем url страницы
    session["url"] = url_for("users.upcoming_tasks")

    db_sess = db_session.create_session()
    # Запрашиваем все задачи, добавленный этим пользователем, 
    # отсортированные по приоритетности, алфавиту и дате
    tasks = db_sess.query(Task).filter(Task.user_id == current_user.id).order_by(Task.scheduled_date, Task.priority, Task.title).all()

    # Группируем задачи по дате
    data = {}
    for key, group in groupby(tasks, key=lambda x: x.scheduled_date):
        data[key] = [thing for thing in group]

    # Для того, чтобы правильно вывести задачи в таблицу посмотри циклы в templates/upcoming_tasks.html
    # Скорее всего придется делать новый template для правильного отображения
    return render_template('index.html', title="Upcoming Tasks", tasks=tasks) # tasks заменить на data


@users.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    db_sess = db_session.create_session()

    # Находим дату недельной давности
    last_week_date = datetime.now().date() - timedelta(7)

    # Запрашиваем количество выполненных задач за последнуюю неделю, 
    # за последнюю неделю 
    tasks = db_sess.query(Task.completed_date, func.count(Task.id)).\
                    filter(Task.user_id == current_user.id,
                           Task.completed_date.between(last_week_date, datetime.now().date())).\
                    group_by(Task.completed_date).\
                    order_by(Task.completed_date.desc()).all()

    # Заполняем статистику пустыми значениями
    weekday = weekdays(datetime.now().strftime("%A"))
    data = {key: 0 for key in weekday}
    for group, val in tasks:
        data[group.strftime("%A")] = val

    # Запрашиваем завершенные задачи за все время
    completed_tasks = db_sess.query(func.count(Task.id)).filter(Task.user_id == current_user.id, Task.done == 1).first()[0]

    return render_template('dashboard.html', title="Dashboard", tasks=data, completed=completed_tasks)
