// Изменение формата даты, отображаемого в календаре
const dateOptions = {
    year: 'numeric',
    month: 'long',
    day: '2-digit'
};

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
const cardsColors = { 1: "#E63E22", 2: "#F0EB65", 3: "#66D9B8", 4: "#8965F0" }

function ColorCardsByPriority() {
    document.querySelectorAll(".card").forEach(card => {
        cardPriority = parseInt(card.querySelector("span[name='priority']").innerHTML, 10);
        card.style.backgroundColor = cardsColors[cardPriority];
    });
}

// Фокусируем на поле ввода при открытии формы
let myModal = document.getElementById('AddTaskModal');

myModal.addEventListener('shown.bs.modal', function() {
    focusCaretAtEnd(document.getElementById("addTaskName"));
})

// Task completion implementation
function completeTask(id) {
    fetch("/complete_task", {
            method: "POST",
            body: JSON.stringify(id),
            headers: {
                "Content-Type": "application/json",
            },
        })
        .then(function(response) {
            response.json().then(function(data) {
                window.location.href = data["url"];
            });
        })
}

function isDictEmpty(obj) {
    return Object.keys(obj).length === 0;
}

function focusCaretAtEnd(elem) {
    let elemLen = elem.value.length;

    elem.selectionStart = elemLen;
    elem.selectionEnd = elemLen;
    elem.focus();
}

// Производим вызов функций после полной загрузки страницы
document.addEventListener('DOMContentLoaded', function() {
    ColorCardsByPriority();
    changeDateFormat("add");
}, false);

// При вводе в поисковое поле вызываем функцию fetchSearch
document.getElementById("search-bar").oninput = function() {
    const textToFind = this.value.trim();

    // Поиск начнется только если в строке есть символы
    if (textToFind.match(/^[a-z0-9а-я]*$/i)) {
        searchData(textToFind, '/search_request');
    }
};

// Создаем форму редактирования задачи
function createEditFormPattern(data) {
    // Создаем сегодняшнюю дату для ограничения в календаре
    let currentDate = new Date();
    let year = currentDate.getFullYear(),
        month = currentDate.getMonth() + 1,
        day = currentDate.getDate();

    if (day < 10) day = '0' + day
    if (month < 10) month = '0' + month

    let today = year + '-' + month + '-' + day

    let pattern = [
        '<div class="modal fade" id="EditTaskModal" tabindex="-1" aria-labelledby="EditTaskModal" aria-hidden="true">',
        '<div class="modal-dialog">',
        '<div class="modal-content">',
        '<div class="modal-header">',
        '<h5 class="modal-title">Edit Task</h5>',
        '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button></div>',
        '<div class="modal-body">',
        '<form action="/tasks/',
        data["id"],
        '" method="post">',
        '<p><label for="title">Title</label>',
        '<input class="form-control" id="editTaskName" name="title" required type="text" value="',
        data["title"],
        '"></p>',
        '<p><label for="priority">Priority</label></p>',
        '<div class="priority-choice">',
        '<div class="priority-unit">',
        '<label class="checkbox">',
        '<input type="radio"name="priority" value="1">',
        '<span class="checkmark">1</span>',
        '</label>',
        '</div>',
        '<div class="priority-unit">',
        '<label class="checkbox">',
        '<input type="radio"name="priority" value="2">',
        '<span class="checkmark">2</span>',
        '</label>',
        '</div>',
        '<div class="priority-unit">',
        '<label class="checkbox">',
        '<input type="radio"name="priority" value="3">',
        '<span class="checkmark">3</span>',
        '</label>',
        '</div>',
        '<div class="priority-unit">',
        '<label class="checkbox">',
        '<input type="radio"name="priority" value="4">',
        '<span class="checkmark">4</span>',
        '</label>',
        '</div>',
        '</div>',
        '<p></p>',
        '<p><label for="scheduled_date">Schedule Task</label></br>',
        '<input id="editTaskCalendar" class="calendar" type="date" name="calendar" value="',
        data["scheduled_date"],
        `" onchange="changeDateFormat('edit')" min="`,
        today,
        '">',
        '</p>',
        '<p class="fload-end">',
        '<input class="btn btn-primary float-end" id="submit" name="submit" type="submit" value="Submit">',
        '</p>',
        '</form>',
        '</div>',
        '</div>',
        '</div>',
        '</div>',
        '</div>'
    ];

    return pattern.join("");
}

// Создаем форму редактирования задачи
function editTask(id) {
    let node = document.querySelector("#editModal");

    // Запрашиваем данные задачи по id
    // и заполняем ими форму
    fetch(`/tasks/${id}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        }
    }).then(function(response) {
        response.json().then(function(data) {
            let form = createEditFormPattern(data);
            node.innerHTML = form;

            // Активируем форму
            let editModal = document.getElementById('EditTaskModal');
            let bsModal = new bootstrap.Modal(editModal);
            changeDateFormat("edit");
            // Выбираем чекбокс в зависимости от заданной приоритетности задачи
            document.querySelector(`div[id="EditTaskModal"] label[class="checkbox"] input[value="${data["priority"]}"]`).checked = true;
            bsModal.show();

            // Фокусируеся на поле редактирования после открытия формы
            editModal.addEventListener('shown.bs.modal', function() {
                focusCaretAtEnd(document.getElementById("editTaskName"))
            })
        });
    });
}