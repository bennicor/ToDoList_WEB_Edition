    // Закрашивание карточек в соответсвии с приоритетностью
    let cardsColors = { 1: "#f16a6a", 2: "#f5f25d", 3: "#5dd2f5", 4: "#6af55d" }

    function PriorityColor() {
        let priorities = document.querySelectorAll(".priority");
        let cards = document.querySelectorAll(".card");

        for (let i = 0; i < priorities.length; i++) {
            let priority = Number(priorities[i].innerHTML);

            cards[i].style.backgroundColor = cardsColors[priority];
        }
    }

    // Создаем HTML pattern для элемента, который будет отображаться
    function createTaskPattern(data) {
        var pattern = [
            '<div class="card text-center" style="width: 18rem">',
            '<div class="card-body">',
            '<h5 class="card-title">',
            data["title"],
            '</h5>',
            '<p class="card-text">Priority: <span class="priority">',
            data["priority"],
            '</span></p>',
            '<div class="btn-group" style="width: 250px; height: 43px;">',
            '<button type="button" class="btn btn-primary" data-toggle="button" autocomplete="off" onclick=completeTask(',
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

                    data.forEach((element) => {
                        pattern = createTaskPattern(element);
                        nodes += pattern;
                    });

                    tasks.innerHTML = nodes;
                    PriorityColor();
                });
            })
            .catch(function(error) {
                tasks.innerHTML = `Failed to load. Reason: ${error.message}`;
            });
    }

    document.addEventListener('DOMContentLoaded', function() {
        PriorityColor();
    }, false);