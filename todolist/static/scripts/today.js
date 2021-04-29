// Закрашивание карточек в соответсвии с приоритетностью
let cardsColors = { 1: "#E63E22", 2: "#F0EB65", 3: "#66D9B8", 4: "#8965F0" }

function PriorityColor() {
    let priorities = document.querySelectorAll('span[name="priorities"]');
    let cards = document.querySelectorAll(".card");

    for (let i = 0; i < priorities.length; i++) {
        let priority = Number(priorities[i].innerHTML);

        cards[i].style.backgroundColor = cardsColors[priority];
    }
}

// Создаем HTML pattern для элемента, который будет отображаться
function createTaskPattern(data) {
    var pattern = [
        '<div class="card">',
        '<div class="card-body">',
        '<h5 class="card-title">',
        data["title"],
        '</h5>',
        '<p class="card-text">Priority: <span name="priorities">',
        data["priority"],
        '</span></p>',
        '<div class="btn-group">',
        '<button type="button" class="btn btn-success" data-toggle="button" autocomplete="off" onclick=completeTask(',
        data["id"],
        ')>Done</button>',
        '<button class="btn btn-info" onclick=location.href="/tasks/',
        data["id"],
        '"> Edit </button>',
        '<button class="btn btn-danger" onclick=location.href="/tasks_delete/',
        data["id"],
        '">Delete</button>',
        "</div>",
        "</div>",
        "</div>",
    ];

    return pattern.join("");
}

// Search Implementation
// Отправляем HTTP запрос в python функцию
// и получаем оттуда информацию из базы данных
// В теле запроса передаем содержимое поисковой строки
function fetchData(text, url) {
    const tasks = document.querySelector("#tasks");

    fetch(url, {
            method: "POST",
            body: JSON.stringify(text),
            headers: {
                "Content-Type": "application/json",
            },
        })
        .then(function(response) {
            if (!response.ok) {
                throw Error(response.statusText);
            }

            response.json().then(function(data) {
                let pattern,
                    nodes = "";

                if (!isDictEmpty(data)) {
                    data.forEach((element) => {
                        pattern = createTaskPattern(element);
                        nodes += pattern;
                    });
                } else {
                    nodes = `<div class='help-text'><p>You don 't have any tasks for today<br>Add a task by clicking the "Add Task" button!</p></div>`;
                }

                tasks.innerHTML = nodes;
                PriorityColor();
            });
        })
        .catch(function(error) {
            tasks.innerHTML = `Failed to load. Reason: ${error.message}`;
        });
}

function isDictEmpty(obj) {
    return Object.keys(obj).length === 0;
}

// При вводе в поисковое поле вызываем функцию fetchSearch
document.getElementById("search-bar").oninput = function() {
    const textToFind = this.value.trim();

    // Поиск начнется только если в строке есть символы
    if (textToFind.match(/^[a-z0-9а-я]*$/i)) {
        fetchData(textToFind, '/search_request');
    }
};

// При полной загрузке страницы вызываем скрипты
document.addEventListener('DOMContentLoaded', function() {
    PriorityColor();
}, false);

// Task completion implementation
function completeTask(id) {
    fetchData(id, '/complete_task');
}