from todolist import create_app, db_session

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
    db_session.global_init("db/TDLDataBase.db")
