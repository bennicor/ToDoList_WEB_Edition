// Изменение формата даты, отображаемого в календаре
const dateOptions = {
    year: 'numeric',
    month: 'long',
    day: '2-digit'
};

document.querySelector(".calendar").onchange = function() {
    let currentDate = new Date(this.value);
    let formatedDate = new Intl.DateTimeFormat('en', dateOptions).format(currentDate);
    this.setAttribute("data-date", formatedDate);
};

// Активируем событие, чтобы по умолчанию отображалась сегодняшняя дата
document.querySelector(".calendar").onchange();

// Отключаем флеш уведомления через опредленное количество секунд
window.setTimeout(function() {
    let alert = document.getElementById("alert");
    let bsAlert = new bootstrap.Alert(alert);
    bsAlert.close();
}, 4000);

const cardsColors = { 1: "#E63E22", 2: "#F0EB65", 3: "#66D9B8", 4: "#8965F0" }

// Изменяем цвет карточек в соответсвии со значением приоритетности
function ColorCardsByPriority() {
    document.querySelectorAll(".card").forEach(card => {
        cardPriority = parseInt(card.querySelector("span[name='priority']").innerHTML, 10);
        card.style.backgroundColor = cardsColors[cardPriority];
    });
}

// Фокусируем на поле ввода при открытии формы
let myModal = document.getElementById('AddTaskModal');
let myInput = document.getElementById('taskName');

myModal.addEventListener('shown.bs.modal', function() {
    myInput.focus();
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

// Закрашиваем карточки после загрузки страницы
document.addEventListener('DOMContentLoaded', function() {
    ColorCardsByPriority();
}, false);

// При вводе в поисковое поле вызываем функцию fetchSearch
document.getElementById("search-bar").oninput = function() {
    const textToFind = this.value.trim();

    // Поиск начнется только если в строке есть символы
    if (textToFind.match(/^[a-z0-9а-я]*$/i)) {
        searchData(textToFind, '/search_request');
    }
};