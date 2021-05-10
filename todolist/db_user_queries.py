from todolist import db_session
from todolist.models import User


def create_user(name, email, password, profile_image):
    db_sess = db_session.create_session()

    user = User(name=name, email=email, image_file=profile_image)
    user.set_password(password)
    db_sess.add(user)
    db_sess.commit()


def get_user(user=None, email=None):
    db_sess = db_session.create_session()

    if email:
        user = db_sess.query(User).filter(User.email == email).first()
    else:
        user = db_sess.query(User).filter(User.id == user.id).first()

    return user, db_sess
