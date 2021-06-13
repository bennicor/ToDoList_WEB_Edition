from todolist import db_session
from todolist.db_user_queries import create_user, get_user, get_pending
from todolist.models import User, friendship


db_session.global_init("todolist/db/TDLDataBase.db")
db_sess = db_session.create_session()

print(db_sess.query(User).all())
user1 = db_sess.query(User).filter(User.id==1).first()
user2 = db_sess.query(User).filter(User.id==2).first()
user3 = db_sess.query(User).filter(User.id==3).first()
user4 = db_sess.query(User).filter(User.id==4).first()

# print(get_pending(user4))
user3.add_friend(user1)
db_sess.commit()
