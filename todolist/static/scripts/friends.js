const errorMessage = document.querySelector("#results p");
const form = document.getElementById("add-friend-block")

document.getElementById("friend-code").oninput = function() {
    var friendCode = this.value.trim();

    // Проверяем правильность введенного кода
    if (friendCode.length < 9 && friendCode.length > 0) {
        try {
            friendCode = parseInt(friendCode, 10);

            if (isNaN(friendCode)) {
                throw Error;
            }

            sendFriendRequest(friendCode);
        } catch {
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
            //Дизайн блока с найденным пользователем
            const profile = document.querySelector("#results form");
            const img = document.querySelector("#results form img");
            const name = document.querySelector("#results form h2");
            const email = document.querySelector("#results form h5");
            const button = document.querySelector("#results form input[type='submit']");

            // Заполняем профиль найденного пользователя его данными
            if (!isDictEmpty(data)) {
                profile.setAttribute("action", `${request_urls["addFriend"]}${data["id"]}`);
                img.setAttribute("src", `${picsPath}${data["image_file"]}`);
                name.innerHTML = `${data["name"]}`;
                email.innerHTML = `${data["email"]}`;

                console.log(data["is_pending"])
                    // Проверяем если найденный пользователь есть
                    // у человека в друзьях
                if (data["are_friends"] === true) {
                    // Изменить кнопку на кнопку удаления из друзей
                    button.setAttribute("class", "btn btn-danger");
                    button.setAttribute("value", "Remove Friend")

                    profile.setAttribute("action", `${request_urls["removeFriend"]}${data["id"]}`);
                }

                // Если мы уже отправили заявку
                if (data["is_pending"] === true) {
                    button.setAttribute("disabled", true);
                    button.setAttribute("value", "Request is Sent");
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