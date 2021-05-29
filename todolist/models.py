import datetime
from todolist import login_manager
from flask_login import UserMixin
from marshmallow import Schema, fields
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, String, Date, DateTime, Integer, Boolean, ForeignKey, Table
from .db_session import SqlAlchemyBase
from sqlalchemy.orm import relation, backref
from todolist import db_session
from flask import flash

# Инициализируем декоратор авторизации
# Пользователь не сможет совершать действия, помеченные декоратором, если он не авторизован
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# Association Table для реализации many-to-many связи
friends = Table("friends",
                SqlAlchemyBase.metadata,
                Column('user_id', Integer, ForeignKey('users.id')),
                Column('friend_id', Integer, ForeignKey('users.id'))
)

pending = Table("pending",
                SqlAlchemyBase.metadata,
                Column('user_id', Integer, ForeignKey('users.id')),
                Column('pending_id', Integer, ForeignKey('users.id'))
)


class Task(SqlAlchemyBase):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    done = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    priority = Column(Integer, default=4)
    scheduled_date = Column(Date, default=datetime.datetime.now().date())
    completed_date = Column(Date, nullable=True)

    def __repr__(self):
        return f'<Task> {self.id} {self.title} {self.priority} {self.scheduled_date}'

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
    
    # Список друзей данного пользователя
    friend = relation('User', secondary=friends,
        primaryjoin=(friends.c.user_id == id),
        secondaryjoin=(friends.c.friend_id == id), lazy="dynamic")

    # Список людей, ожадающих добавления в друзья
    pending = relation("User", secondary=pending,
        primaryjoin=(pending.c.user_id == id),
        secondaryjoin=(pending.c.pending_id == id), lazy="dynamic")

    friend_code = Column(Integer, nullable=True)

    def __repr__(self):
        return f'<User> {self.id} {self.name} {self.email} {self.friend_code}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def are_friends(self, user):
        return self.friend.filter(friends.c.friend_id == user.id).count() == 1

    def send_friend_request(self, user):
        user.pending.append(self)

    def add_friend(self, user):
        if not self.are_friends(user):
            self.friend.append(user)
            user.friend.append(self)

    def unfriend(self, user):
        if self.are_friends(user):
            self.friend.remove(user)
            user.friend.remove(self)


class UserSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    email = fields.Str()
    image_file = fields.Str()
    friend_code = fields.Int()
