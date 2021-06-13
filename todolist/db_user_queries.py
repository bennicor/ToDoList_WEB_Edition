from todolist import db_session
from todolist.models import User, friendship
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


def get_pending(user):
    db_sess = db_session.create_session()
    result = {"incoming": [], "outcoming": []}

    # Возвращает список отношений, в которых пользователю была отправлена заявка
    incoming = db_sess.query(friendship.c.user_id).filter(friendship.c.friend_id==user.id).all()

    # Список пользователей, которым пользователь отправил заявку
    outcoming = db_sess.query(friendship.c.friend_id).filter(friendship.c.user_id==user.id).all()

    for i in outcoming:
        # Получаем обьект отправителя
        friend = get_user(user_id=i[0])

        # Проверяем, если они друзья
        if not user.are_friends(friend):
            result["outcoming"].append(friend)

    for i in incoming:
        # Получаем обьект отправителя
        friend = get_user(user_id=i[0])

        # Проверяем, если они друзья
        if not user.are_friends(friend):
            result["incoming"].append(friend)

    return result