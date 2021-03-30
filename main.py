from flask import Flask, render_template, redirect, url_for, request, abort, jsonify, session
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from datetime import datetime, timedelta
from sqlalchemy import func
from data import db_session
from data.users import User
from data.tasks import Task
from data.task_schema import TaskSchema
from forms.tasks import TaskForm
from forms.login import LoginForm
from forms.register import RegisterForm
from itertools import groupby
from helpers import weekdays


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Инициализируем декоратор авторизации.
# Пользователь не сможет совершать действия, помеченные декоратором, если он не авторизован


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

# Обработчики ошибок
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(401)
def page_not_found(e):
    return render_template("401.html"), 401


def main():
    db_session.global_init("db/TDLDataBase.db")
    app.run(port=8080, host='127.0.0.1', debug=True)

'''
Надо будет добавить главную страницу, на которой пользователю будет предложено авторизоваться
Или сделать navbar, на котором будет отображаться статус авторизации
'''
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for("tasks"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("tasks"))

    form = LoginForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        # Проверяем если пользователь зарегистрирован в базе данных и пароли совпадают
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("tasks"))
        return render_template("login.html",
                               message="Incorrect email or password",
                               form=form)
    return render_template('login.html', title='Authorization', form=form)


@app.route("/register", methods=["GET", "POST"])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for("tasks"))

    form = RegisterForm()

    if form.validate_on_submit():
        # Проверяем если пароли в форме совпадают
        if form.password.data != form.password_again.data:
            return render_template("register.html", title="Registration", message="Passwords are different", form=form)

        db_sess = db_session.create_session()
        # Проверяем, если почтовый адрес еще не занят
        if db_sess.query(User).filter(form.email.data == User.email).first():
            return render_template("register.html", title="Registration", form=form)

        user = User()
        user.email = form.email.data
        user.set_password(form.password.data)
        user.name = form.name.data
        db_sess.add(user)
        db_sess.commit()
        return redirect(url_for("login"))
    return render_template("register.html", title="Registration", form=form)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/tasks/today", methods=["GET", "POST"])
@login_required
def tasks():
    # Сохраняем url страницы
    session["url"] = url_for("tasks")
    
    db_sess = db_session.create_session()

    # Запрашиваем только задачи, созданные этим пользователем
    # и дата которых совпадает с сегодняшним днем, 
    # отсортированные по приоритету и алфавиту
    tasks = db_sess.query(Task).filter(Task.user_id == current_user.id,
                                        Task.scheduled_date == datetime.now().date()).order_by(Task.priority, Task.title).all()

    return render_template("index.html", title="Today's Tasks", tasks=tasks)

@app.route("/tasks/upcoming", methods=["GET", "POST"])
@login_required
def upcoming_tasks():
    # Сохраняем url страницы
    session["url"] = url_for("upcoming_tasks")

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
    return render_template('upcoming_tasks.html', title="Upcoming Tasks", tasks=data) # tasks заменить на data

# Функция, делающая запросы в базу данных по мере ввода текста в поисковую строку
@app.route("/search_request", methods=["GET", "POST"])
def search_request():
    db_sess = db_session.create_session()
    searchbox = request.form.get("text") # Получаем содержимое строки поиска

    if session["url"] == url_for("tasks"):
        # Запрашиваем задачи, название которых входит в поисковую строку
        tasks = db_sess.query(Task).filter(Task.user_id == current_user.id,
                                           Task.scheduled_date == datetime.now().date(),
                                           Task.title.like(f"%{searchbox}%")).order_by(Task.priority, Task.title).all()
    elif session["url"] == url_for("upcoming_tasks"): # Изменить после создании upcoming_tasks.html
        # Запрашиваем задачи, название которых входит в поисковую строку
        tasks = db_sess.query(Task).filter(Task.user_id == current_user.id,
                                           Task.title.like(f"%{searchbox}%")).order_by(Task.scheduled_date, Task.priority, Task.title).all()

    result = []
    for task in tasks:
        schema = TaskSchema() # Создаем схему
        json_result = schema.dump(task) # Производим сериализацию объекта в JSON формат
        result.append(json_result)

    return jsonify(result)

@app.route("/dashboard", methods=["GET"])
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


@app.route('/add_tasks',  methods=['GET', 'POST'])
@login_required
def add_tasks():
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
        return redirect(session.get("url")) # Перенаправляет на прошлую страницу
    return render_template('add_task.html', title='Add task', form=form)


@app.route('/tasks/<int:task_id>',  methods=['GET', 'POST'])
@login_required
def edit_tasks(task_id):
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
            form.done.data = tasks.done
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
            tasks.done = form.done.data

            if tasks.done:
                tasks.completed_date = datetime.now().date()
            else: # Скорее всего в дальнейшем не понадобится
                tasks.completed_date = None

            db_sess.commit()
            return redirect(session.get("url")) # Перенаправляет на прошлую страницу
        else:
            abort(404)

    return render_template('edit_task.html', title='Edit task', form=form)


@app.route("/tasks_delete/<int:task_id>", methods=["GET", "POST"])
@login_required
def delete_task(task_id):
    db_sess = db_session.create_session()
    task = db_sess.query(Task).filter(
        Task.id == task_id, Task.user_id == current_user.id).first()

    if task:
        db_sess.delete(task)
        db_sess.commit()
        return redirect(session.get("url")) # Перенаправляет на прошлую страницу
    else:
        abort(404)


if __name__ == '__main__':
    main()
