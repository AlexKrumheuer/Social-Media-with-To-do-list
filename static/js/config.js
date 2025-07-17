let formConfigNav = document.querySelector(".container-configUser")

function openConfigWindow() {
    async function loadUser() {
        try {
            const response = await fetch("/dashboard/get_user")
            const data = await response.json()
            openConfigWindowLoaded(data[0])
        } catch (error) {
            console.error("Erro ao buscar dados: ", error)
        }
    }
    loadUser()
}

function openConfigWindowLoaded(dataUser) {
    formConfigNav.innerHTML = `
    <form class="configUser_grid">
                <i onclick="closeConfigWindow()" class="configUser-closeButton fa-solid fa-xmark"></i>
                <div class="configUser-container__grid">
                    <div style="width: 30%;" class="configUser_grid--perfil">
                        <div style="height: 100%; width: 100%; display: flex; justify-content: center;">
                            <input style="display: none;" type="file" name="">
                            <img class="user-image" src="../static/uploads/307ce493-b254-4b2d-8ba4-d12c080d6651.jpg"
                                alt="">
                        </div>
                        <div class="container-input">
                            <label for="username">Username</label>
                            <div class="editEnable">
                                <span name="username" class="spanText">${dataUser['username']}</span>
                                <input maxlength="15" class="config-inputs" type="text" name="usernameInput">
                                <i class="fa-solid fa-pen-to-square editIcon"></i>
                            </div>
                        </div>
                    </div>
                    <div style="width: 70%;" class="configUser_grid--perfil">
                        <div style="display: flex;">
                            <div class="container-input" style="width: 50%;">
                                <label name="FirstName" for="FirstName">First Name</label>
                                <div class="editEnable">
                                    <span name="FirstName" class="spanText">${dataUser['firstname']}</span>
                                    <input maxlength="15" class="config-inputs" type="text" name="firstNameInput">
                                    <i class="fa-solid fa-pen-to-square editIcon"></i>
                                </div>
                            </div>
                            <div class="container-input" style="width: 50%;">
                                <label for="lastName">Last Name</label>
                                <div class="editEnable">
                                    <span  name="lastName" class="spanText">${dataUser['lastname']}</span>
                                    <input maxlength="15" class="config-inputs" type="text" name="lastNameInput">
                                    <i class="fa-solid fa-pen-to-square editIcon"></i>
                                </div>
                            </div>
                        </div>
                        <div class="container-input" style="width: 100%;">
                                <label for="bio">Edit your Bio</label>
                                <div>
                                    <textarea wrap="hard"  rows="3" cols="50" maxlength="500" name="bio" class="fa-solid fa-pen-to-square"></textarea>
                                </div>
                            </div>
                        <div class="container-input">
                            <label for="email">E-mail</label>
                            <div class="editEnable">
                                <span name="email" class="spanText">${dataUser['email']}</span>
                                <input maxlength="30" class="config-inputs" type="email" name="emailInput">
                                <i class="fa-solid fa-pen-to-square editIcon"></i>
                            </div>
                        </div>
                        <div class="container-input">
                            <label for="Senha">Senha</label>
                            <div class="editEnable">
                                <span class="spanText">Change your password</span>
                                <input class="config-inputs" type="password" name="Senha">
                                <i class="fa-solid fa-pen-to-square editIcon"></i>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="configButton">
                    <button id="configUser_button" type="submit">Edit</button>
                </div>
            </form>
    `
    formConfigNav.style.display = "flex"
    //Enable config edit button
    const span = document.querySelectorAll(".spanText")
    const input = document.querySelectorAll(".config-inputs")
    const icon = document.querySelectorAll(".editIcon")
    const containerEdit = document.querySelectorAll(".editEnable")

    for (let i = 0; i < span.length; i++) {
        icon[i].addEventListener("click", () => {
            let displayInput = window.getComputedStyle(input[i]).display
            if (displayInput == "none") {
                console.log(icon[i])
                input[i].value = span[i].textContent
                containerEdit[i].classList.add("applyStyles")
                span[i].style.display = "none"
                input[i].style.display = "block"
                input[i].focus();
                icon[i].classList.remove('fa-pen-to-square');
                icon[i].classList.add('fa-check');
            } else {
                // Salvar e voltar para span
                if (input[i].type != "password") {
                    span[i].textContent = input[i].value;
                } else {
                    span[i].textContent = "Change your password"
                }

                containerEdit[i].classList.remove("applyStyles")
                span[i].style.display = 'block';
                input[i].style.display = 'none';
                icon[i].classList.remove('fa-check');
                icon[i].classList.add('fa-pen-to-square');
            }
        })
    }
    setupSubmitConfigUser()
} 

function closeConfigWindow() {
    formConfigNav.style.display = "none"
    let childRemoved = document.querySelector(".configUser-grid")
    if (childRemoved) {
        formTaskNav.removeChild(childRemoved)
    }
}

function setupSubmitConfigUser() {
    let form = document.querySelector(".configUser_grid")
    let button = document.getElementById("configUser_button")

    form.addEventListener("submit", (event) => {
        event.preventDefault()

        // Monta objeto com userConfigs
        const userConfigs = {
            username: form.usernameInput.value,
            firstName: form.firstNameInput.value,
            lastName: form.lastNameInput.value,
            bio: form.bio.value,
            email: form.emailInput.value,
        }
        console.log(userConfigs)
        // Envia para backend
        fetch("/dashboard/config_user", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(userConfigs)
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.reload()
                }
            })
    })
}