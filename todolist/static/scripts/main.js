const dateOptions = {
    year: 'numeric',
    month: 'long',
    day: '2-digit'
}

const picsPath = "/static/profile_pics/";

const cardsColors = {
    1: "#E63E22",
    2: "#F0EB65",
    3: "#66D9B8",
    4: "#8965F0"
}
const request_urls = {
    "search": "/search_request",
    "task": "/tasks/",
    "deleteTask": "/tasks_delete/",
    "completeTask": "/complete_task",
    "addFriend": "/add_friend/",
    "removeFriend": "/remove_friend/",
    "getFriend": "/show_friend"
}

// Изменение формата даты, отображаемого в календаре
function changeDateFormat(type) {
    // Изменяем формат даты в календаре в зависимости от выбранной формы
    if (type == "add") {
        var calendar = document.getElementById("addTaskCalendar");
    } else if (type == "edit") {
        var calendar = document.getElementById("editTaskCalendar");
    }

    let currentDate = new Date(calendar.value);
    let formatedDate = new Intl.DateTimeFormat('en', dateOptions).format(currentDate);
    calendar.setAttribute("data-date", formatedDate);
}


// Отключаем флеш уведомления через опредленное количество секунд
window.setTimeout(function() {
    let alert = document.getElementById("alert");
    let bsAlert = new bootstrap.Alert(alert);
    bsAlert.close();
}, 4000);


// Изменяем цвет карточек в соответсвии со значением приоритетности
function ColorCardsByPriority() {
    document.querySelectorAll(".card").forEach(card => {
        cardPriority = parseInt(card.querySelector("span[id='priority']").innerHTML, 10);
        card.style.backgroundColor = cardsColors[cardPriority];
    });
}

// Декоративные действия с модальными формами
function afterModalTransition(element) {
    element.setAttribute("style", "display: none !important;");
}

function focusCaretAtEnd(elem) {
    let elemLength = elem.value.length;

    elem.selectionStart = elemLength;
    elem.selectionEnd = elemLength;
    elem.focus();
}

function isDictEmpty(obj) {
    return Object.keys(obj).length === 0;
}

// Task completion implementation
function completeTask(id) {
    fetch(`${request_urls["completeTask"]}`, {
        method: "POST",
        body: JSON.stringify(id),
        headers: {
            "Content-Type": "application/json",
        },
    }).then(function(response) {
        response.json().then(function(data) {
            // Перенаправляем пользователя на другую страницу для корректного отображения уведомлений
            window.location.href = data["url"];
        });
    });
}

// Создаем форму редактирования задачи
function editTask(id) {
    fetch(`${request_urls["task"]}${id}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    }).then(function(response) {
        response.json().then(function(data) {
            // Заполняем форму данными 
            const editModal = document.getElementById("EditTaskModal");

            form = editModal.querySelector("form");
            form.setAttribute("action", `${request_urls["task"]}${data["id"]}`);

            input = editModal.querySelector("#editTaskName");
            input.setAttribute("value", `${data["title"]}`);

            date = editModal.querySelector("#editTaskCalendar");
            date.setAttribute("value", `${data["scheduled_date"]}`);

            // Активируем форму
            let bsModal = new bootstrap.Modal(editModal);
            changeDateFormat("edit");
            // Выбираем чекбокс в зависимости от заданной приоритетности задачи
            document.querySelector(`div[id="EditTaskModal"] label[class="checkbox"] input[value="${data["priority"]}"]`).checked = true;
            bsModal.show();

            // Фокусируеся на поле редактирования после открытия формы
            editModal.addEventListener('show.bs.modal', function() {
                focusCaretAtEnd(document.getElementById("editTaskName"));
            })

            // Ожидаем завершения анимации и скрываем форму после закрытия
            editModal.addEventListener("hidden.bs.modal", function() {
                setTimeout(() => afterModalTransition(this), 400);
            })
        });
    });
}

// Вызываем форму подтверждения при удалении
function deleteTask(id) {
    fetch(`${request_urls["task"]}${id}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    }).then(function(response) {
        response.json().then(function(data) {
            const deleteModal = document.getElementById("deleteTaskModal");

            textBody = deleteModal.querySelector("#deleteText");
            // Вставляем в тело формы название задачи
            textBody.innerHTML = `${data["title"]}`;

            button = deleteModal.querySelector(".btn-danger");
            button.setAttribute("onclick", `location.href="${request_urls["deleteTask"]}${data["id"]}"`);

            // Активируем форму
            let bsModal = new bootstrap.Modal(deleteModal);
            bsModal.show();

            // Ожидаем завершения анимации и скрываем форму после закрытия
            deleteModal.addEventListener("hidden.bs.modal", function() {
                setTimeout(() => afterModalTransition(this), 400);
            })
        });
    });
}