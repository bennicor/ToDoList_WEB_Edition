from todolist import db_session
from todolist.db_user_queries import create_user
from todolist.models import User


db_session.global_init("todolist/db/TDLDataBase.db")
db_sess = db_session.create_session()


for i in db_sess.query(User).all():
    print(i, i.pending.all())