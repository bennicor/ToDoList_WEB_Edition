import secrets, os
from PIL import Image
from pathlib import Path
from random import randint


# Возвращает список дней за последнюю неделю с заданного дня
def weekdays(day):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    i = days.index(day) + 1
    d1 = list(reversed(days[:i]))
    d1.extend(list(reversed(days[i:])))

    # Создаем словарь из дней со стандартными значениями
    data = {key: 0 for key in d1}
    return data

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

def random_with_N_digits(n):
    range_start = 1
    range_end = 10 ** n - 1
    return randint(range_start, range_end)
