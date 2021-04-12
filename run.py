import os
from todolist import create_app, db_session
from flask_ngrok import run_with_ngrok

app = create_app()
run_with_ngrok(app)

if __name__ == '__main__':
    # Необходимо поместить базу данных в данный католог
    db_session.global_init("todolist/db/TDLDataBase.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
