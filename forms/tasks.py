from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, DateTimeField
from wtforms.validators import DataRequired
import datetime

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    priority = IntegerField("Priority of the task", default=4)
    scheduled_date = DateTimeField("When do you want to complete the problem?(MM/DD/YYYY)", format="%m/%d/%Y", default=datetime.datetime.now)
    done = BooleanField("Is Done?", default=False)
    submit = SubmitField('Submit')
