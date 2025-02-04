from flask import Flask, render_template, redirect, url_for, request, abort, jsonify, session, make_response, Blueprint, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from datetime import datetime
from .forms import TaskForm
from todolist.models import Task, TaskSchema
from itertools import groupby
from todolist.db_tasks_queries import get_today_tasks, get_upcoming_tasks, get_task
from todolist import db_session


tasks = Blueprint("tasks", __name__)

# Функция, делающая запросы в базу данных по мере ввода текста в поисковую строку
@tasks.route("/search_request", methods=["POST"])
@login_required
def search_request():
    searchbox = request.get_json()  # Получаем содержимое строки поиска

    if session["url"] == url_for("users.tasks"):
        tasks = get_today_tasks(current_user, searchbox)

        result = []
        if tasks:
            for task in tasks:
                schema = TaskSchema()  # Создаем схему
                # Производим сериализацию объекта в JSON формат
                json_result = schema.dump(task)
                result.append(json_result)

        return make_response(jsonify(result), 200)
    elif session["url"] == url_for("users.upcoming_tasks"):
        tasks = get_upcoming_tasks(current_user, searchbox)

        data = {}
        if tasks:
            # Группируем задачи по дате
            for key, group in groupby(tasks, key=lambda x: x.scheduled_date):
                data[str(key)] = [TaskSchema().dump(thing) for thing in group]

        return make_response(jsonify(data), 200)


@tasks.route("/complete_task", methods=["POST"])
@login_required
def complete_task():
    task_id = int(request.get_json())  # Получаем id, выполненной задачи

    db_sess = db_session.create_session()
    task = get_task(task_id, current_user)

    task.done = True
    task.completed_date = datetime.now().date()
    db_sess.commit()

    # Возвращаем адрес страницы, на которую надо будет отправить пользователя
    response = {"url": session["url"]}
    flash("Task has been completed!", "success")
    return make_response(jsonify(response), 200)


@tasks.route('/tasks/<int:task_id>',  methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    # Если пользователь получает данные, то заполняем форму текующими данными о задаче
    if request.method == "GET":
        task = get_task(task_id, current_user)

        return make_response(jsonify(TaskSchema().dump(task)), 200)

    # Если пользователь отправил обновленные данные
    if request.method == "POST":
        data = request.form
        db_sess = db_session.create_session()
        task = get_task(task_id, current_user)
        
        if task:
            task.title = data.get("title")
            task.priority = data.get("priority")
            task.scheduled_date = datetime.strptime(data.get("calendar"), "%Y-%m-%d")
            db_sess.commit()
            flash("Task has been successfully edited!", "success")
            return redirect(session["url"])
        else:
            abort(404)


@tasks.route("/tasks_delete/<int:task_id>", methods=["GET", "POST"])
@login_required
def delete_task(task_id):
    db_sess = db_session.create_session()
    task = get_task(task_id, current_user)

    db_sess.delete(task)
    db_sess.commit()
    flash("Task has been deleted!", "danger")
    # Перенаправляет на прошлую страницу
    return redirect(session["url"])
