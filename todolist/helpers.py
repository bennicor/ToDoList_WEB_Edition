import secrets, os
from PIL import Image
from pathlib import Path


# Возвращает список дней за последнюю неделю с заданного дня
def weekdays(day):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    i = days.index(day) + 1
    d1 = list(reversed(days[:i]))
    d1.extend(list(reversed(days[i:])))
    return d1

# Сохраняем картинку, загруженную пользователем
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(Path(__file__).parent.absolute(), 'static/profile_pics', picture_fn)

    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn
