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
                <div class="mobile-img_pic config-container__pic">
                    <input id="upload-input" style="width: 100%; height: 100%;" type="file" name="profileImage" hidden>
                    <img id="profile-pic" class="user-image" src="../static/uploads/perfil.jpg" alt="">
                </div>
                <div class="container-input">
                    <label for="username">Username</label>
                    <div id="mobile-username" class="editEnable">
                        <span name="username" class="spanText">${dataUser['username']}</span>
                        <input maxlength="15" class="config-inputs" type="text" name="usernameInput" style="display: none;" value="${dataUser['username']}">
                        <i class="fa-solid fa-pen-to-square editIcon"></i>
                    </div>
                </div>
            </div>
            <div style="width: 70%;" class="configUser_grid--perfil">
                <div style="display: flex;">
                    <div class="container-input" style="width: 50%;">
                        <label for="FirstName">First Name</label>
                        <div class="editEnable">
                            <span name="FirstName" class="spanText">${dataUser['firstname']}</span>
                            <input maxlength="15" class="config-inputs" type="text" name="firstNameInput" style="display: none;" value="${dataUser['firstname']}">
                            <i class="fa-solid fa-pen-to-square editIcon"></i>
                        </div>
                    </div>
                    <div class="container-input" style="width: 50%;">
                        <label for="lastName">Last Name</label>
                        <div class="editEnable">
                            <span name="lastName" class="spanText">${dataUser['lastname']}</span>
                            <input maxlength="15" class="config-inputs" type="text" name="lastNameInput" style="display: none;" value="${dataUser['lastname']}">
                            <i class="fa-solid fa-pen-to-square editIcon"></i>
                        </div>
                    </div>
                </div>
                <div class="container-input" style="width: 100%;">
                    <label for="bio">Edit your Bio</label>
                    <div>
                        <textarea id="mobile-size" wrap="hard" rows="3" cols="50" maxlength="500" name="bio">${dataUser['bio']}</textarea>
                    </div>
                </div>
                <div class="container-input">
                    <label for="email">E-mail</label>
                    <div class="editEnable">
                        <span name="email" class="spanText">${dataUser['email']}</span>
                        <input maxlength="30" class="config-inputs" type="email" name="emailInput" style="display: none;" value="${dataUser['email']}">
                        <i class="fa-solid fa-pen-to-square editIcon"></i>
                    </div>
                </div>
                <div class="container-input">
                    <label for="Senha">Senha</label>
                    <div class="editEnable">
                        <span class="spanText">Change your password</span>
                        <input class="config-inputs" type="password" name="Senha" style="display: none;">
                        <i class="fa-solid fa-pen-to-square editIcon" onclick="window.location.href='/dashboard/change_password'"></i>
                    </div>
                </div>
            </div>
        </div>
        <div class="configButton">
            <button id="configUser_button" type="submit">Edit</button>
        </div>
    </form>
    `

    const image = document.getElementById("profile-pic")
    const inputUploadPic = document.getElementById("upload-input")
    image.addEventListener('click', () => {
        inputUploadPic.click()
    })

    inputUploadPic.addEventListener('change', () => {
        const file = inputUploadPic.files[0]
        if (!file) return

        if (!file.type.startsWith('image/')) {
            alert('Por favor, selecione um arquivo de imagem válido (jpg, png, etc).')
            inputUploadPic.value = ''
            return
        }

        const reader = new FileReader()
        reader.onload = () => {
            image.src = reader.result
        }
        reader.readAsDataURL(file)
    })

    formConfigNav.style.display = "flex"

    const span = document.querySelectorAll(".spanText")
    const input = document.querySelectorAll(".config-inputs")
    const icon = document.querySelectorAll(".editIcon")
    const containerEdit = document.querySelectorAll(".editEnable")

    for (let i = 0; i < span.length; i++) {
        icon[i].addEventListener("click", () => {
            let displayInput = window.getComputedStyle(input[i]).display
            if (displayInput == "none") {
                if (input[i].type != "password") {
                    input[i].value = span[i].textContent
                    containerEdit[i].classList.add("applyStyles")
                    span[i].style.display = "none"
                    input[i].style.display = "block"
                    input[i].focus()
                    icon[i].classList.remove('fa-pen-to-square')
                    icon[i].classList.add('fa-check')
                }
            } else {
                if (input[i].type != "password") {
                    span[i].textContent = input[i].value
                    containerEdit[i].classList.remove("applyStyles")
                    span[i].style.display = 'block'
                    input[i].style.display = 'none'
                    icon[i].classList.remove('fa-check')
                    icon[i].classList.add('fa-pen-to-square')
                }
            }
        })
    }

    setupSubmitConfigUser()
}

function closeConfigWindow() {
    formConfigNav.style.display = "none"
    let childRemoved = document.querySelector(".configUser_grid")
    if (childRemoved) {
        formConfigNav.removeChild(childRemoved)
    }
}

function setupSubmitConfigUser() {
    let form = document.querySelector(".configUser_grid")

    form.addEventListener("submit", (event) => {
        event.preventDefault()

        const formData = new FormData()

        formData.append("username", form.usernameInput.value)
        formData.append("firstName", form.firstNameInput.value)
        formData.append("lastName", form.lastNameInput.value)
        formData.append("bio", form.bio.value)
        formData.append("email", form.emailInput.value)

        const fileInput = form.querySelector('input[type="file"]')
        if (fileInput.files.length) {
            formData.append("profileImage", fileInput.files[0])
        }

        fetch("/dashboard/config_user", {
            method: "POST",
            body: formData,
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.reload()
                } else {
                    alert("Erro ao salvar os dados")
                }
            })
            .catch((error) => {
                console.error("Erro ao enviar dados:", error)
                alert("Erro na requisição")
            })
    })
}
