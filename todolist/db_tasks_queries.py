from todolist import db_session
from todolist.models import Task
from datetime import datetime
from flask import flash, request
from sqlalchemy import func


def get_task(id, user):
    db_sess = db_session.create_session()
    
    task = db_sess.query(Task).filter(Task.id == id,
                                      Task.user_id == user.id).first()
    
    return task, db_sess


def get_today_tasks(user, searchbox=None):
    db_sess = db_session.create_session()

    # Если пользователь ввел запрос в поисковую строку
    if searchbox:
        # Запрашиваем задачи, название которых входит в поисковую строку
        tasks = db_sess.query(Task).filter(Task.user_id == user.id,
                                           Task.scheduled_date == datetime.now().date(),
                                           Task.title.like(f"%{searchbox}%"),
                                           Task.done == 0).order_by(Task.priority, Task.title).all()
    else:
        # Запрашиваем только задачи, созданные этим пользователем
        # и дата которых совпадает с сегодняшним днем,
        # отсортированные по приоритету и алфавиту
        tasks = db_sess.query(Task).filter(Task.user_id == user.id,
                                        Task.scheduled_date == datetime.now().date(), Task.done == 0).order_by(Task.priority, Task.title).all()

    return tasks


def get_upcoming_tasks(user, searchbox=None):
    db_sess = db_session.create_session()

    if searchbox:
        # Запрашиваем задачи, название которых входит в поисковую строку
        tasks = db_sess.query(Task).filter(Task.user_id == user.id,
                                           Task.title.like(f"%{searchbox}%"),
                                           Task.done == 0).order_by(Task.scheduled_date, Task.priority, Task.title).all()
    else:
        # Запрашиваем все задачи, добавленный этим пользователем,
        # отсортированные по приоритетности, алфавиту и дате
        tasks = db_sess.query(Task).filter(Task.user_id == user.id, Task.done == 0).\
            order_by(Task.scheduled_date, Task.priority, Task.title).all()

    return tasks


def get_weekly_completed_tasks(user, last_week_date):
    db_sess = db_session.create_session()

    # Запрашиваем количество выполненных задач за последнуюю неделю
    tasks = db_sess.query(Task.completed_date, func.count(Task.id)).\
        filter(Task.user_id == user.id,
               Task.completed_date.between(last_week_date, datetime.now().date())).\
        group_by(Task.completed_date).\
        order_by(Task.completed_date.desc()).all()

    return tasks


def get_all_completed(user):
    db_sess = db_session.create_session()

    # Запрашиваем завершенные задачи за все время
    tasks = db_sess.query(func.count(Task.id)).filter(
        Task.user_id == user.id, Task.done == 1).first()[0]

    return tasks

def add_task(form, user):
    db_sess = db_session.create_session()
    # Изменяем дату формы на выбранную в календаре
    date = request.form.get("calendar")
    form.scheduled_date.data = date


    tasks = Task()
    tasks.title = form.title.data.strip()
    tasks.priority = form.priority.data
    tasks.scheduled_date = datetime.strptime(form.scheduled_date.data, "%Y-%m-%d")
    tasks.user_id = user.id
    db_sess.add(tasks)
    db_sess.commit()
    flash("Task has been added!", "success")
