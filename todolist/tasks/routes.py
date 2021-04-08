from flask import Flask, render_template, redirect, url_for, request, abort, jsonify, session, make_response, Blueprint, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from datetime import datetime
from todolist import db_session
from .forms import TaskForm
from todolist.models import Task, TaskSchema
from itertools import groupby


tasks = Blueprint("tasks", __name__)

# Функция, делающая запросы в базу данных по мере ввода текста в поисковую строку


@tasks.route("/search_request", methods=["POST"])
@login_required
def search_request():
    db_sess = db_session.create_session()
    searchbox = request.get_json()  # Получаем содержимое строки поиска

    if session["url"] == url_for("users.tasks"):
        # Запрашиваем задачи, название которых входит в поисковую строку
        tasks = db_sess.query(Task).filter(Task.user_id == current_user.id,
                                           Task.scheduled_date == datetime.now().date(),
                                           Task.title.like(f"%{searchbox}%"),
                                           Task.done == 0).order_by(Task.priority, Task.title).all()
        result = []
        for task in tasks:
            schema = TaskSchema()  # Создаем схему
            # Производим сериализацию объекта в JSON формат
            json_result = schema.dump(task)
            result.append(json_result)

        return make_response(jsonify(result), 200)
    elif session["url"] == url_for("users.upcoming_tasks"):
        # Запрашиваем задачи, название которых входит в поисковую строку
        tasks = db_sess.query(Task).filter(Task.user_id == current_user.id,
                                           Task.title.like(f"%{searchbox}%"),
                                           Task.done == 0).order_by(Task.scheduled_date, Task.priority, Task.title).all()

        # Группируем задачи по дате
        data = {}
        for key, group in groupby(tasks, key=lambda x: x.scheduled_date):
            data[str(key)] = [TaskSchema().dump(thing) for thing in group]

        return make_response(jsonify(data), 200)


@tasks.route("/complete_task", methods=["POST"])
@login_required
def complete_task():
    task_id = int(request.get_json())  # Получаем id, выполненной задачи

    db_sess = db_session.create_session()
    task = db_sess.query(Task).filter(Task.id == task_id,
                                      Task.user_id == current_user.id).first()

    if task:  # Отмечаем задачу завершенной
        task.done = True
        task.completed_date = datetime.now().date()
        db_sess.commit()

    # Запрашиваем из базы данных задачи, в соответствии с текущей страницей
    if session["url"] == url_for("users.tasks"):
        tasks = db_sess.query(Task).filter(Task.user_id == current_user.id,
                                           Task.scheduled_date == datetime.now().date(),
                                           Task.done == 0).order_by(Task.priority, Task.title).all()

        result = []
        for task in tasks:
            schema = TaskSchema()  # Создаем схему
            # Производим сериализацию объекта в JSON формат
            json_result = schema.dump(task)
            result.append(json_result)

        return make_response(jsonify(result), 200)
    elif session["url"] == url_for("users.upcoming_tasks"):
        tasks = db_sess.query(Task).filter(Task.user_id == current_user.id,
                                           Task.done == 0).order_by(Task.scheduled_date, Task.priority, Task.title).all()

        # Группируем задачи по дате
        data = {}
        for key, group in groupby(tasks, key=lambda x: x.scheduled_date):
            data[str(key)] = [TaskSchema().dump(thing) for thing in group]

        return make_response(jsonify(data), 200)

    flash("Task completed!", "info")


@tasks.route('/add_task',  methods=['GET', 'POST'])
@login_required
def add_task(ForUsers=False):
    form = TaskForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        tasks = Task()
        tasks.title = form.title.data.strip()
        tasks.priority = form.priority.data
        tasks.scheduled_date = form.scheduled_date.data
        tasks.user_id = current_user.id
        db_sess.add(tasks)
        db_sess.commit()
        flash("Task has been added!", "info")
        # Перенаправляет на прошлую страницу
        return redirect(session.get("url"))
    if ForUsers:
        return form
    return render_template('add_task.html', title='Add task', form=form)


@tasks.route('/tasks/<int:task_id>',  methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    form = TaskForm()

    # Если пользователь получает данные, то заполняем форму текующими данными о задаче
    if request.method == "GET":
        db_sess = db_session.create_session()
        tasks = db_sess.query(Task).filter(
            Task.id == task_id, Task.user_id == current_user.id).first()

        if tasks:
            form.title.data = tasks.title
            form.priority.data = tasks.priority
            form.scheduled_date.data = tasks.scheduled_date
        else:
            abort(404)

    # Если форма готова к отправке, обновляем информацию на более актульную
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        tasks = db_sess.query(Task).filter(Task.id == task_id).first()

        if tasks:
            tasks.title = form.title.data.strip()
            tasks.priority = form.priority.data
            tasks.scheduled_date = form.scheduled_date.data

            db_sess.commit()
            flash("Task has been successfully edited!", "info")
            # Перенаправляет на прошлую страницу
            return redirect(session.get("url"))
        else:
            abort(404)

    return render_template('edit_task.html', title='Edit task', form=form)


@tasks.route("/tasks_delete/<int:task_id>", methods=["GET", "POST"])
@login_required
def delete_task(task_id):
    db_sess = db_session.create_session()
    task = db_sess.query(Task).filter(
        Task.id == task_id, Task.user_id == current_user.id).first()

    if task:
        db_sess.delete(task)
        db_sess.commit()
        flash("Task has been deleted!", "info")
        # Перенаправляет на прошлую страницу
        return redirect(session.get("url"))
    else:
        abort(404)
