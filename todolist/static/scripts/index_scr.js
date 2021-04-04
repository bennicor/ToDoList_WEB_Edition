function PriorityColor() {
    var priority = document.querySelectorAll("priority");
    for (let i = 0; i < priority.length; i++) {
        console.log(Number(priority[i].innerHTML));
        if (Number(priority[i].innerHTML) == 1) {
            priority[i].style.backgroundColor = prompt(
                "background color?",
                "red"
            );
        } else if (Number(priority[i].innerHTML) == 2) {
            priority[i].style.backgroundColor = prompt(
                "background color?",
                "yellow"
            );
        } else if (Number(priority[i].innerHTML) == 3) {
            priority[i].style.backgroundColor = prompt(
                "background color?",
                "blue"
            );
        } else if (Number(priority[i].innerHTML) == 4) {
            priority[i].style.backgroundColor = prompt(
                "background color?",
                "green"
            );
        }
    }
}
PriorityColor();
// Создаем HTML pattern для элемента, который будет отображаться
function createTaskPattern(data) {
    var pattern = [
        '<div class="card text-center" style="width: 18rem">',
        '<div class="card-body">',
        '<h5 class="card-title">',
        data["title"],
        "</h5>",
        '<p class="card-text">Priority: <a class="priority">',
        data["priority"],
        "</a></p>",
        '<div class="card_buttons">',
        '<input type="checkbox" id="completed" name="',
        data["id"],
        '" onclick="completeTask(this.name)">',
        '<a href="/tasks/',
        data["id"],
        '" class="btn btn-info">Edit</a>',
        '<a href="/tasks_delete/',
        data["id"],
        '" class="btn btn-danger">Delete</a>',
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
        .then(function (response) {
            if (!response.ok) {
                throw Error(response.statusText);
            }

            response.json().then(function (data) {
                let pattern,
                    nodes = "";

                data.forEach((element) => {
                    pattern = createTaskPattern(element);
                    nodes += pattern;
                });

                tasks.innerHTML = nodes;
            });
            PriorityColor();
        })
        .catch(function (error) {
            tasks.innerHTML = "Failed to load";
        });
}

// При вводе в поисковое поле вызываем функцию fetchSearch
document.getElementById("finder").oninput = function () {
    const textToFind = this.value.trim();

    fetchData(textToFind, '{{ url_for("tasks.search_request") }}');
};

// Task completion implementation
// id передается при нажатии на конкретный checkbox
function completeTask(id) {
    const checkbox = document.getElementsByName(id)[0].checked;

    // Проверяем если checkbox активен
    if (checkbox) {
        fetchData(id, '{{ url_for("tasks.complete_task") }}');
    }
}
