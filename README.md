# What ToDo

### Основная информация
**What ToDo** - проект, выполненный на языке Python, при использовании фреймворка Flask. Представляет из себя удобный способ ведения активности и трудовой деятельности пользователя. Первый шаг к успешному планированию дел и тайм менеджменту - правильная постановка задач и приоритетов, и наш проект способен облегчить эту задачу. Приложение позволяет добавлять задачи на необходимую дату с указанием приоритетности, отслеживать статистику поставленных целей, а также имеет удобный и отзывчивый пользовательский интерфейс.

### Требования
Для успешного запуска проекта необходимо создать виртуальное окружение и выполнить установку модулей из файла requirements.txt при помощи следующей команды:
```python
python -m pip install -r requirements.txt
```
Запуск приложения осуществляется через файл run.py.

### Работа с API
Данный проект обладает собственным **API** (Application Programming Interface), что позволяет взаимодействовать с сервисом при помощи *http*-запросов без использования UI.

Авторизация.

* **What ToDo API** использует систему токенов при авторизации. Перед получением токена необходимо убедиться, что вы зарегистрированы в системе, после чего появится возможность авторизации через API. Чтобы получить токен, следует отправить *GET* запрос по адресу */api/login* и передать email и password, использованные при регистрации. Если был отправлен верный запрос - вам вернется токен, который необходимо поместить в блок **headers**, для использования в последующих запросах.

* Блок headers:   

    ```python
    key: x-access-token, value: токен, полученный при авторизации
    ```
После успешной авторизации у пользователя появляется возможность работы с задачами.

Взаимодействие с задачами.

* **Получение всех или конкретной задачи**:
	* Для получения всех задач нужно отправить *GET* запрос по адресу */api/tasks*. 
	* При указании id конкретной задачи можно получить эту задачу - */api/tasks/id задачи*.

* **Добавление задачи**:
	* Для добавления задачи необходимо отправить *POST* запрос на адрес */api/tasks*. В теле запроса следует указать содержимое задачи в следующем формате:
	
      ```python
      {"title": название задачи, "priority": приоритетность задачи, "scheduled_date": дата, на которую запланирована задача}
      ```
* **Завершение задачи**:
	* Для завершения задачи нужно отправить *PUT* запрос на адрес */api/tasks/task_id*, с указанием id задачи.

* **Удаление задачи**:
	* Удаление задачи осуществляется по средствам отправик *DELETE* запроса по адресу */api/tasks/task_id*.

### Заключение
Проект активно разрабатывается и улучшается. При работе с приложением возможны ошибки или недочеты, но все они будут исправляться по мере осведомления. *Спасибо за пользование!*