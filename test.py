from todolist import db_session
from todolist.db_user_queries import create_user, get_pending
from todolist.models import User


db_session.global_init("todolist/db/TDLDataBase.db")
db_sess = db_session.create_session()

# print(db_sess.query(User.friend_code).all())
user1 = db_sess.query(User).filter(User.id==1).first()
user2 = db_sess.query(User).filter(User.id==2).first()

# print(user1.are_friends(user2))
# print(user1.are_friends(user2))
user2.add_friend(user1)
db_sess.commit()