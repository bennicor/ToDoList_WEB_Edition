from todolist import create_app, db_session

app = create_app()

if __name__ == '__main__':
    db_session.global_init("todolist/db/TDLDataBase.db")
    app.run(debug=True)
