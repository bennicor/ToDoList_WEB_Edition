from datetime import datetime, timedelta
from itertools import groupby
from flask import (Blueprint, Flask, flash, redirect, render_template, request,
                   session, url_for, make_response, jsonify)
from flask_login import current_user, login_required, login_user, logout_user
from todolist.helpers import save_picture, weekdays
from todolist.models import Task, User, UserSchema
from todolist import db_session
from todolist.tasks.forms import TaskForm
from todolist.users.forms import LoginForm, RegistrationForm, UpdateAccountForm
from todolist.db_user_queries import create_user, get_user, get_pending
from todolist.db_tasks_queries import (get_today_tasks, get_upcoming_tasks,
                                          get_weekly_completed_tasks, get_all_completed, add_task)
from todolist import db_session


users = Blueprint('users', __name__)


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users.tasks"))

    form = RegistrationForm()

    if form.validate_on_submit():
        # Если пользователь не загрузил собственную фотографию
        # Выбирается фотография по умолчанию
        picture_file = "default.jpg"
        if form.image_file.data:
            picture_file = save_picture(form.image_file.data)

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
        user = get_user(email=form.email.data)

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


# Перенести в каталог с задачами
@users.route("/tasks/today", methods=["GET", "POST"])
@login_required
def tasks():
    # Сохраняем url страницы
    session["url"] = url_for("users.tasks")

    # Добавляем задачу из modal формы
    form = TaskForm()

    if form.validate_on_submit():
        add_task(form, current_user)
        flash("Task has been added!", "success")
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
    session["url"] = url_for("users.dashboard")

    # Запрашиваем количество выполненных задач за последнуюю неделю
    tasks = get_weekly_completed_tasks(current_user, last_week_date)

    # Заполняем статистику пустыми значениями
    data = weekdays(datetime.now().strftime("%A"))
    for group, val in tasks:
        data[group.strftime("%A")] = val

    completed_tasks = get_all_completed(current_user)

    return render_template('dashboard.html', title="Dashboard", tasks=data, completed=completed_tasks)


@users.route("/update_account", methods=["GET", "POST"])
@login_required
def update_account():
    form = UpdateAccountForm()
    session["url"] = url_for("users.update_account")

    # Если пользователь получает данные, то заполняем форму текующими данными о профиле
    if request.method == "GET":
        form.name.data = current_user.name
        form.email.data = current_user.email

    # Если форма готова к отправке, обновляем информацию на актульную
    if form.validate_on_submit():
        user = get_user(user_id=current_user.id)
        db_sess = db_session.create_session()

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


@users.route("/friends", methods=["GET", "POST"])
@login_required
def friends():
    session["url"] = url_for("users.friends")
    code = current_user.friend_code
    # Отображаем всех друзей, кроме самого пользователя
    friends = list(filter(lambda user: user.friend_code != code and user.are_friends(current_user), current_user.friends.all()))
    return render_template("friends.html", title="Your Friends",user_code=code, friends=friends)


@users.route("/show_friend", methods=["POST"])
@login_required
def show_friend():
    friend_code = request.get_json()
    
    # Сериализируем объект пользователя перед отправкой
    friend, result = get_user(friend_code=friend_code), {}

    if friend:
        # Проверяем если этот пользователь находится у нас в друзьях
        user = get_user(user_id=current_user.id)
    
        result = UserSchema().dump(friend)
        result["are_friends"] = user.are_friends(friend)
        # Проверяем если уже отправили запрос
        result["is_pending"] = user in get_pending(friend)
    return make_response(jsonify(result), 200)


# Добавляем найденного по коду пользователя в друзья
@users.route("/add_friend/<int:friend_id>", methods=["GET"])
@login_required
def add_friend(friend_id):
    db_sess = db_session.create_session()
    friend = get_user(user_id=friend_id)
    user = get_user(user_id=current_user.id)

    user.add_friend(friend)
    db_sess.commit()
    flash("Request has been sent!", "success")
    return redirect(session["url"])


@users.route("/remove_friend/<int:friend_id>", methods=["GET"])
@login_required
def remove_friend(friend_id):
    db_sess = db_session.create_session()
    friend = get_user(user_id=friend_id)
    user = get_user(user_id=current_user.id)

    user.unfriend(friend)
    db_sess.commit()
    flash("Friend deleted!", "success")

    return redirect(session["url"])
