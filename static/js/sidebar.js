let sidebarButton = document.getElementById("btn-sidebar")
let sidebar = document.getElementById("sidebar")
let text = document.querySelectorAll(".sidebar-text")
let icons = document.querySelectorAll(".sidebar-icons")
let user = document.querySelector(".sidebar-user")

sidebarButton.addEventListener("click", () => {
    let sidebarStatus = sidebar.dataset.status
    if (sidebarStatus == "open") {
        user.style.width = "7rem"
        user.style.height = "7rem"
        text.forEach((elemento) => {
            elemento.style.display = "none"
        })
        for (let i = 0; i < icons.length; i++) {
            icons[i].style.fontSize = "1.8rem"
            icons[i].style.width = "100%"
            icons[i].style.textAlign = "center"
        }
        sidebar.dataset.status = "close"
        sidebar.style.width = "10%"
    } else {
        user.style.width = "10rem"
        user.style.height = "10rem"
        text.forEach((elemento) => {
            elemento.style.display = "block"
        })
        for (let i = 0; i < icons.length; i++) {
            icons[i].style.fontSize = "1.4rem"
            icons[i].style.width = "auto"
            icons[i].style.textAlign = "auto"
        }
        sidebar.dataset.status = "open"
        sidebar.style.width = "20%"
    }

})