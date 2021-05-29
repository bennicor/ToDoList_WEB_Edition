from todolist import db_session
from todolist.models import User
from todolist.helpers import random_with_N_digits


def create_user(name, email, password, profile_image):
    db_sess = db_session.create_session()

    # Генерируем уникальный код пользователя для добавления в друзья 
    code, user_friend_codes = random_with_N_digits(8), db_sess.query(User.friend_code).all()
    codes = [int(code[0]) for code in user_friend_codes] if user_friend_codes else []

    while code in codes:
        code = random_with_N_digits(8)

    user = User(name=name, 
                email=email,
                image_file=profile_image,
                friend_code=code)
    user.set_password(password)
    db_sess.add(user)
    user.add_friend(user)
    db_sess.commit()


def get_user(user_id=None, email=None, friend_code=None):
    db_sess = db_session.create_session()

    if email:
        user = db_sess.query(User).filter(User.email == email).first()
    elif friend_code:
        user = db_sess.query(User).filter(User.friend_code == friend_code).first()
    else:
        user = db_sess.query(User).filter(User.id == user_id).first()

    return user
