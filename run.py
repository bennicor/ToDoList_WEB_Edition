from todolist import create_app, db_session

app = create_app()

if __name__ == '__main__':
    # Необходимо поместить базу данных в данный католог
    db_session.global_init("todolist/db/TDLDataBase.db")
    app.run()
