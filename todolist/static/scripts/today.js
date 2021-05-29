// При вводе в поисковое поле вызываем функцию searchData
document.getElementById("search-bar").oninput = function() {
    const textToFind = this.value;

    searchData(textToFind, request_urls["search"]);
};


// Отправляем HTTP запрос в python функцию
// и получаем оттуда информацию из базы данных
// В теле запроса передаем содержимое поисковой строки
function searchData(text, url) {
    const tasks = document.querySelector("#tasks");
    const errorMessage = document.createElement("p");

    fetch(url, {
        method: "POST",
        body: JSON.stringify(text),
        headers: {
            "Content-Type": "application/json",
        }
    }).then(function(response) {
        if (!response.ok) {
            throw Error(response.statusText);
        }

        response.json().then(function(data) {
            let pattern = "",
                nodes = document.createElement("div");

            if (data.length > 0) {
                data.forEach((element) => {
                    pattern = createTaskPattern(element);
                    nodes.appendChild(pattern);
                });
            } else {
                errorMessage.innerHTML = "Nothing found";
                nodes.appendChild(errorMessage);
            }

            tasks.innerHTML = nodes.innerHTML;
            ColorCardsByPriority();
        });
    }).catch(function(error) {
        errorMessage.innerHTML = `Failed to load. Reason: ${error.message}`;
        tasks.innerHTML = errorMessage.innerHTML;
    });
}


// Фокусируем на поле ввода при открытии формы
let addModal = document.getElementById('AddTaskModal');

addModal.addEventListener('shown.bs.modal', function() {
    focusCaretAtEnd(document.getElementById("addTaskName"));
})

// Ожидаем завершения анимации и скрываем форму после закрытия
addModal.addEventListener("hidden.bs.modal", function() {
    setTimeout(() => afterModalTransition(this), 400);
})

// Производим вызов функций после полной загрузки страницы
document.addEventListener('DOMContentLoaded', function() {
    ColorCardsByPriority();
    changeDateFormat("add");
});