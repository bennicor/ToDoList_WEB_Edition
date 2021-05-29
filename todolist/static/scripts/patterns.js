// Создаем HTML patterns для динамического обновления
// DOM дерева

function createTaskPattern(data) {
    let div = document.createElement("div");
    div.setAttribute("class", "card");

    div.innerHTML = `
        <div class="card-body">
            <h5 class="card-title">${data["title"]}</h5>
            <p class="card-text">
                Priority: <span id="priority">${data["priority"]}</span>
            </p>
            <div class="btn-group">
                <button
                    type="button"
                    class="btn btn-success"
                    data-toggle="button"
                    autocomplete="off"
                    onclick="completeTask('${data["id"]}')"
                >
                Done
                </button>
                <button class="btn btn-info" onclick="editTask('${data["id"]}')">Edit</button>
                <button class="btn btn-danger" onclick="deleteTask('${data["id"]}')">Delete</button>
            </div>
        </div>
`;

    return div;
}

function createTaskDatePattern(date) {
    var div = document.createElement("div");
    div.setAttribute("class", "date-group");
    div.innerHTML = `
        <h1>${date}</h1>
    `;

    return div;
}