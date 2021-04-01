let condition = { true: "Done!", false: "In progress" };

function createTaskPattern(data) {
    var pattern = [
        '<div class="card text-center" style="width: 18rem">',
        '<div class="card-body">',
        '<h5 class="card-title">',
        data["title"],
        " - ",
        condition[data["done"]],
        "</h5>",
        '<p class="card-text">Priority:',
        data["priority"],
        "</p>",
        "<div>",
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

function ready(fn) {
    if (document.readyState != "loading") {
        fn();
    } else {
        document.addEventListener("DOMContentLoaded", fn);
    }
}

function fetchData(text) {
    let tasks = document.querySelector("#tasks");

    fetch("{{ url_for('tasks.search_request') }}", {
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
        })
        .catch(function (error) {
            tasks.innerHTML = "Failed to load";
        });
}

ready(() => {
    document.querySelector("#finder").addEventListener("input", (event) => {
        let text = { search: document.querySelector("#finder").value };

        fetchData(text);
    });
});
