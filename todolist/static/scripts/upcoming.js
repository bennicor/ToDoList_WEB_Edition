// Создаем HTML pattern для элемента, который будет отображаться
function createTaskPattern(data) {
    var pattern = [
        '<div class="card">',
        '<div class="card-body">',
        '<h5 class="card-title">',
        data["title"],
        '</h5>',
        '<p class="card-text">Priority: <span name="priority">',
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
        "</div>"
    ];

    return pattern.join("");
}

function createTaskDatePattern(date) {
    var pattern = [
        '<div class="date-group">',
        '<h1>',
        date,
        "</h1>",
        '<div class="cards">'
    ];

    return pattern.join("");
}

// Search Implementation
// Отправляем HTTP запрос в python функцию
// и получаем оттуда информацию из базы данных
// В теле запроса передаем содержимое поисковой строки
function searchData(text, url) {
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
                let date = "",
                    pattern = "",
                    nodes = "";

                if (!isDictEmpty(data)) {
                    for (var key in data) {
                        formatedDate = new Date(key).toLocaleDateString("ru-RU");
                        date = createTaskDatePattern(formatedDate);
                        nodes += date;

                        for (let [_, value] of Object.entries(data[key])) {
                            pattern = createTaskPattern(value);
                            nodes += pattern;
                        }

                        nodes += "</div></div>";
                    }
                } else {
                    nodes = 'Nothing found';
                }

                tasks.innerHTML = nodes;
                ColorCardsByPriority();
            });
        })
        .catch(function(error) {
            tasks.innerHTML = `Failed to load. Reason: ${ error.message }`;
        });
}