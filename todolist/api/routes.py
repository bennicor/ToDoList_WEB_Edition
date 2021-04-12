from flask import Flask, Blueprint, request, make_response, jsonify, abort
from todolist import db_session
from todolist.models import User, Task, TaskSchema
import jwt
import datetime
from todolist.config import Config
from functools import wraps
from base64 import b64decode


api = Blueprint('api', __name__)

# Декоратор, проверяющий наличие и правильность токена авторизации
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # При наличии токена в запросе, получаем его
        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]

            if not token:
                return make_response(jsonify({"message": "Token is missing!"}), 401)

        try:
            # Декодируем токен и делаем запрос в базу данных,
            # чтобы получить пользователя с этим id
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            db_sess = db_session.create_session()

            user = db_sess.query(User).filter(User.id == data["id"]).first()

            if not user:
                raise Exception
        except:
            return make_response(jsonify({"message": "Incorrect token!"}), 401)

        # Возвращаем текущего пользователя и аргументы, переданные в функцию
        return f(user, *args, **kwargs)

    return decorated


def abort_if_not_found(user, task_id):
    session = db_session.create_session()
    tasks = session.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    
    if not tasks:
        return abort(404, f"Task with id {task_id} was not found!")


@api.route("/api/login", methods=["GET"])
def login():
    auth = request.authorization
    db_sess = db_session.create_session()

    if not auth or not auth.username or not auth.password:
        return make_response(jsonify({"message": "Could not verify"}), 401)

    user = db_sess.query(User).filter(User.email == auth.username).first()

    if not user:
        return make_response(jsonify({"message": "Could not verify"}), 401)

    # Если пользователь зарегистрирован и ввел правильные данные,
    # генирируем уникальный токен и отправляем в теле ответа
    if user.check_password(auth.password):
        token = jwt.encode({"id": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, Config.SECRET_KEY, algorithm="HS256")

        return jsonify({"token": token})

    return make_response(jsonify({"message": "Could not verify"}), 401)


@api.route("/api/tasks", methods=["GET"])
@token_required
def get_tasks(user):
    session = db_session.create_session()
    tasks = session.query(Task).filter(Task.user_id == user.id).all()

    return jsonify({'tasks': [TaskSchema().dump(item) for item in tasks]})


@api.route("/api/tasks/<int:task_id>", methods=["GET"])
@token_required
def get_task(user, task_id):
    abort_if_not_found(user, task_id)
    session = db_session.create_session()
    task = session.query(Task).filter(Task.user_id == user.id, Task.id == task_id).first()

    return jsonify({'tasks': TaskSchema().dump(task)})


@api.route("/api/tasks", methods=["POST"])
@token_required
def create_task(user):
    session = db_session.create_session()

    data = request.get_json()
    title, priority, date = data["title"], data["priority"], data["scheduled_date"]

    if not isinstance(priority, int) or priority not in range(1, 5):
        return make_response(jsonify({"message": "Priority field must be an integer in range from 1 to 4!"}), 400)

    try:
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    except:
        return make_response(jsonify({"message": "time data do not match format: YYYY-MM-DD"}), 400)

    # Привести к единому формату даты
    task = Task(title=title,
                priority=priority,
                scheduled_date=date,
                user_id=user.id)
    session.add(task)
    session.commit()

    return jsonify({'message' : 'New task created!'})


@api.route('/api/tasks/<int:task_id>', methods=['PUT'])
@token_required
def complete_task(user, task_id):
    abort_if_not_found(user, task_id)
    session = db_session.create_session()
    task = session.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()

    task.done = True
    task.completed_date = datetime.datetime.now().date()
    session.commit()

    return jsonify({"message": "Task has been completed!"})


@api.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@token_required
def delete_task(user, task_id):
    abort_if_not_found(user, task_id)
    session = db_session.create_session()
    task = session.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()

    session.delete(task)
    session.commit()

    return make_response(jsonify({"message": "Task has been deleted!"}), 200)
