from flask import Flask, render_template, redirect, url_for, request, session, Blueprint, flash
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime, timedelta
from todolist.models import User, Task
from itertools import groupby
from todolist.helpers import weekdays
from todolist.users.forms import RegistrationForm, LoginForm, UpdateAccountForm
from todolist import db_session
from sqlalchemy import func
from todolist.helpers import save_picture
from todolist.tasks.routes import add_task
from todolist.tasks.forms import TaskForm


users = Blueprint('users', __name__)


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users.tasks"))

    form = RegistrationForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        # Если пользователь не загрузил собственную фотографию
        # Выбирается фотография по умолчанию
        if form.image_file.data:
            picture_file = save_picture(form.image_file.data)
        else:
            picture_file = "default.jpg"

        user = User(name=form.name.data, email=form.email.data,
                    image_file=picture_file)
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
        user = db_sess.query(User).filter(
            User.email == form.email.data).first()

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

    form = add_task(True)

    db_sess = db_session.create_session()
    # Запрашиваем только задачи, созданные этим пользователем
    # и дата которых совпадает с сегодняшним днем,
    # отсортированные по приоритету и алфавиту
    tasks = db_sess.query(Task).filter(Task.user_id == current_user.id,
                                       Task.scheduled_date == datetime.now().date(), Task.done == 0).order_by(Task.priority, Task.title).all()

    return render_template("index.html", title="Today's Tasks", tasks=tasks, form=form)


@users.route("/tasks/upcoming", methods=["GET", "POST"])
@login_required
def upcoming_tasks():
    # Сохраняем url страницы
    session["url"] = url_for("users.upcoming_tasks")

    db_sess = db_session.create_session()
    # Запрашиваем все задачи, добавленный этим пользователем,
    # отсортированные по приоритетности, алфавиту и дате
    tasks = db_sess.query(Task).filter(Task.user_id == current_user.id, Task.done == 0).\
        order_by(Task.scheduled_date, Task.priority, Task.title).all()

    # Группируем задачи по дате
    data = {}
    for key, group in groupby(tasks, key=lambda x: x.scheduled_date):
        data[key.strftime("%d.%m.%Y")] = [thing for thing in group]

    # Для того, чтобы правильно вывести задачи в таблицу посмотри циклы в templates/upcoming_tasks.html
    # Скорее всего придется делать новый template для правильного отображения
    # tasks заменить на data
    return render_template('upcoming_tasks.html', title="Upcoming Tasks", tasks=data)


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
    completed_tasks = db_sess.query(func.count(Task.id)).filter(
        Task.user_id == current_user.id, Task.done == 1).first()[0]
    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)

    return render_template('dashboard.html', title="Dashboard", tasks=data, completed=completed_tasks, image_file=image_file)


@users.route("/update_account", methods=["GET", "POST"])
@login_required
def update_account():
    form = UpdateAccountForm()

    # Если пользователь получает данные, то заполняем форму текующими данными о профиле
    if request.method == "GET":
        form.name.data = current_user.name
        form.email.data = current_user.email

    # Если форма готова к отправке, обновляем информацию на более актульную
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()

        # Если пользователь заменил фотографию - меняем ее
        if form.image_file.data:
            picture = save_picture(form.image_file.data)
            user.image_file = picture

        user.name = form.name.data.strip()
        user.email = form.email.data.strip()

        db_sess.commit()
        flash("Account info has been successfully changed!", "info")
        # Перенаправляет на странице профиля
        return redirect(url_for("users.dashboard"))
    # Получаем путь к фотографии пользователя
    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)

    return render_template('update_account.html', title='Edit Account Info', form=form)
