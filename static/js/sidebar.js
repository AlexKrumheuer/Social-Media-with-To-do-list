let sidebarButton = document.getElementById("btn-sidebar")
let sidebar = document.getElementById("sidebar")
let text = document.querySelectorAll(".sidebar-text")
let icons = document.querySelectorAll(".sidebar-icons")
let user = document.querySelector(".sidebar-user")

if (sidebarButton && sidebar && user) {
    sidebarButton.addEventListener("click", () => {
        let sidebarStatus = sidebar.dataset.status

        if (sidebarStatus === "open") {
            user.style.width = "7rem"
            user.style.height = "7rem"

            text.forEach((elemento) => {
                elemento.style.display = "none"
            })

            icons.forEach((icon) => {
                icon.style.fontSize = "1.8rem"
                icon.style.width = "100%"
                icon.style.textAlign = "center"
            })

            sidebar.dataset.status = "close"
            sidebar.style.width = "10%"

        } else {
            user.style.width = "10rem"
            user.style.height = "10rem"

            text.forEach((elemento) => {
                elemento.style.display = "block"
            })

            icons.forEach((icon) => {
                icon.style.fontSize = "1.4rem"
                icon.style.width = "auto"
                icon.style.textAlign = "auto"
            })

            sidebar.dataset.status = "open"
            sidebar.style.width = "20%"
        }
        const usernameMobile = document.getElementById("username-mobile")
        usernameMobile.style.display = "none"
    })
}
