import datetime
from todolist import login_manager
from flask_login import UserMixin
from marshmallow import Schema, fields
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, String, Date, DateTime, Integer, Boolean, ForeignKey
from .db_session import SqlAlchemyBase
from sqlalchemy.orm import relation
from todolist import db_session

# Инициализируем декоратор авторизации.
# Пользователь не сможет совершать действия, помеченные декоратором, если он не авторизован
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


class Task(SqlAlchemyBase):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    done = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relation('User')
    priority = Column(Integer, default=4)
    scheduled_date = Column(Date, default=datetime.datetime.now().date())
    completed_date = Column(Date, nullable=True)

# Схема для сериализации запросов из строки поиска
class TaskSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    done = fields.Bool()
    priority = fields.Int()
    scheduled_date = fields.Str()


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    email = Column(String, index=True, unique=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    image_file = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    tasks = relation("Task", back_populates='user')
    
    def __repr__(self):
        return f'<User> {self.id} {self.name} {self.email}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
