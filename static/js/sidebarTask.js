let navTaskWindow = document.querySelector(".container-addTaskWindow")
let formTaskNav = document.querySelector(".container-addTaskWindow")

function closeTaskWindow() {
    formTaskNav.style.display = "none"
    let childRemoved = document.querySelector(".addTask-window")
    if (childRemoved) {
        formTaskNav.removeChild(childRemoved)
    }
}

//Função para abrir modal de tarefa
function openTaskWindow(caller, event = null) {
    // Monta HTML do formulário
    formTaskNav.innerHTML = `
    <div class="addTask-window">
        <i onclick="closeTaskWindow()" class="closeButton fa-solid fa-xmark"></i>
        <form class="addTask-form">
            <div>
                <label for="title">Título</label>
                <input type="text" maxlength="20"  name="title" placeholder="Digite o título" required>
            </div>
            <div>
                <label for="description">Descrição</label>
                <textarea name="description" maxlength="500" rows="6" placeholder="Digite a descrição"></textarea>
            </div>
            <div>
                <div id="allDay">
                    <label for="allDay">Tarefa de dia inteiro?</label>
                    <input id="allDayCheckbox" name="allDay" type="checkbox" >
                </div>
                <label for="date">Data limite</label>
                <input id="dateTask" type="datetime-local" name="date">
            </div>
            <div>
                <label for="filetasktype">Status</label>
                <select name="filetasktype" required>
                    <option value="start">Não iniciado</option>
                    <option value="onGoing">Em andamento</option>
                    <option value="finish">Concluída</option>
                </select>
            </div>
            <button type="submit" id="addButton">Add</button>
        </form>
    </div>
    `

    let addButton = document.getElementById("addButton")

    if (caller === "task") {
        addButton.textContent = "Edit"
        fillItems(event)
    } else {
        addButton.textContent = "Add"
        setupSubmit(null)
    }

    navTaskWindow.style.display = "flex"
}

//Setup do submit (criar ou editar)
function setupSubmit(elementId = null, dateNormal, dateNormalValue) {
    let form = document.querySelector(".addTask-form")
    let button = document.getElementById("addButton")
    
    const dateTaskCheckbox = document.getElementById("dateTask")
    const allDayCheckbox = document.getElementById("allDayCheckbox")
    if (dateNormal) {
        allDayCheckbox.checked = true
        dateTaskCheckbox.type = "date"
    } else {
         allDayCheckbox.checked = false
    }
    dateTaskCheckbox.value = dateNormalValue
    allDayCheckbox.addEventListener("change", (event) => {
        if (event.target.checked) {
            dateTaskCheckbox.type = "date"
        } else {
            dateTaskCheckbox.type = "datetime-local"
        }
    })

    form.addEventListener("submit", (event) => {
        event.preventDefault()

        // Monta objeto tarefa
        const tarefa = {
            id: elementId,
            titulo: form.title.value,
            descricao: form.description.value,
            data_local: form.date.value,
            status: form.filetasktype.value
        }

        const route = button.textContent === "Edit" ? "editar_tarefa" : "criar_tarefa"

        // Envia para backend
        fetch(`/dashboard/${route}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(tarefa)
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.reload()
                }
            })
    })
}

function removerTarefa(event) {
    const taskContainer = event.target.closest(".child_task--container")
    const id = taskContainer.dataset.id

    fetch("/dashboard/remover_tarefa", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: id })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                taskContainer.remove()
            } else {
                alert("Erro ao remover tarefa!")
            }
        })
}


document.querySelectorAll(".remove_task").forEach(btn => {
    btn.addEventListener("click", removerTarefa)
})

//Preenche campos para edição
function fillItems(event) {
    const taskContainer = event.target.closest(".child_task--container")
    const id = taskContainer.dataset.id
    let tarefaEl = document.getElementById("tarefa")
    let tarefasLista = JSON.parse(tarefaEl.dataset.tarefas)
    const element = tarefasLista.find(el => el.id == id)
    if (element) {
        document.querySelector(".addTask-form input[name='title']").value = element.titulo
        document.querySelector(".addTask-form textarea[name='description']").value = element.descricao
        document.querySelector(".addTask-form input[name='date']").value = element.data_local
        document.querySelector(".addTask-form select[name='filetasktype']").value = element.status

        let dateNormal = false;
        let dateInput = ""
        if (!element.data_local.includes(":")) {
            dateNormal = true
        }

        if (!dateNormal) {
            const [data, hora] = element.data_local.split(' ')
            const [dia, mes, ano] = data.split('/')
            dateInput = `${ano}-${mes}-${dia}T${hora}`
        } else {
            const [dia, mes, ano] = element.data_local.split('/')
            dateInput = `${ano}-${mes}-${dia}`
        }

        setupSubmit(element.id, dateNormal, dateInput)
    }
}