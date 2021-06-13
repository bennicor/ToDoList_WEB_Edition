// Обновление статуса поиска
const errorMessage = document.querySelector("#results p");
const form = document.getElementById("add-friend-block")

// Динамический просмотр профилей пользователя
const profile = document.querySelector("#results form");
const img = document.querySelector("#results form img");
const name = document.querySelector("#results form h2");
const email = document.querySelector("#results form h5");
const button = document.querySelector("#results form input[type='submit']");

// Переключение между вкладками
const TabItems = document.querySelectorAll(".friends-nav");
const ContentItems = document.querySelectorAll(".tab-content");

TabItems.forEach(item => item.addEventListener("click", SelectTab));

document.getElementById("friend-code").oninput = function() {
    var friendCode = this.value.trim();

    // Проверяем правильность введенного кода
    if (friendCode.length < 9 && friendCode.length > 0) {
        try {
            if (isNaN(friendCode)) {
                throw Error;
            }

            friendCode = parseInt(friendCode, 10);
            sendFriendRequest(friendCode);
        } catch {
            profile.setAttribute("style", "display: none!important;");
            errorMessage.innerHTML = "Incorrect Friend Code format";
        }
    }
}


function sendFriendRequest(friendCode) {
    fetch(`${request_urls["getFriend"]}`, {
        method: "POST",
        body: JSON.stringify(friendCode),
        headers: {
            "Content-Type": "application/json",
        }
    }).then(function(response) {
        if (!response.ok) {
            throw Error(response.statusText);
        }

        response.json().then(function(data) {
            if (!isDictEmpty(data)) {
                // Заполняем профиль найденного пользователя его данными
                profile.setAttribute("action", `${request_urls["addFriend"]}${data["id"]}`);
                img.setAttribute("src", `${picsPath}${data["image_file"]}`);
                name.innerHTML = `${data["name"]}`;
                email.innerHTML = `${data["email"]}`;

                // Скрываем кнопку, если пользователь нашел сам себя
                if (data["user_id"] === data["id"]) {
                    button.setAttribute("style", "display: none!important;")
                } else {
                    button.removeAttribute("style");
                }

                // Если мы уже отправили заявку
                if (data["outcoming_pending"] === true) {
                    // Добавить возможность отменить заявку
                    button.setAttribute("value", "Request is Sent");
                    button.disabled = true;
                } else if (data["incoming_pending"] === true) {
                    // Если запрос был послан пользователю
                    button.setAttribute("value", "Accept Request");
                    button.disabled = false;
                    button.setAttribute("class", "btn btn-primary");

                    profile.setAttribute("action", `${request_urls["addFriend"]}${data["id"]}`);
                } else if (data["are_friends"] === true) {
                    // Изменить кнопку на кнопку удаления из друзей
                    button.setAttribute("class", "btn btn-danger");
                    button.setAttribute("value", "Remove Friend")
                    button.disabled = false;

                    profile.setAttribute("action", `${request_urls["removeFriend"]}${data["id"]}`);
                } else {
                    button.disabled = false;
                    button.setAttribute("value", "Add Friend");
                    button.setAttribute("class", "btn btn-primary");
                }

                errorMessage.innerHTML = "";
                profile.setAttribute("style", "display: flex!important;");
            } else {
                profile.setAttribute("style", "display: none!important;");
                throw Error;
            }
        }).catch(function() {
            errorMessage.innerHTML = "No users were found";
        });
    }).catch(function(error) {
        errorMessage.innerHTML = `Failed to load.Reason: ${error.message}`;
    });
}


// Изменяем контент вкладвки, в зависимости от выбора пользователя
function SelectTab(e) {
    removeSelection();
    removeContent();

    this.classList.add("select-tab");
    const SelectedTabContent = document.querySelector(`#${this.id}-content`);

    SelectedTabContent.classList.add("d-block");
}


function removeSelection() {
    TabItems.forEach(item => item.classList.remove("select-tab"));
}

function removeContent() {
    ContentItems.forEach(item => item.classList.remove("d-block"));
}