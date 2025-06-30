let sidebarButton = document.getElementById("btn-sidebar")
let sidebar = document.getElementById("sidebar")
let text = document.querySelectorAll(".sidebar-text")
let icons = document.querySelectorAll(".sidebar-icons")
let user = document.querySelector(".sidebar-user")
let containerGrid = document.querySelector(".container-grid")

sidebarButton.addEventListener("click", ()=>{
    let sidebarStatus = sidebar.dataset.status
    if(sidebarStatus == "open") {
        containerGrid.style.width = "90%"
        text.forEach((elemento) =>{
            elemento.style.display = "none"
            })
        for(let i = 0; i < icons.length; i++) {
            if(i == 0) {
                icons[0].removeAttribute("class")
                icons[0].classList.add("fa-solid")
                icons[0].classList.add("fa-thumbtack-slash")
                icons[0].classList.add("sidebar-icons")
            } 
            icons[i].style.fontSize = "1.8rem"
        }
        sidebar.dataset.status = "close"
        sidebar.style.width = "10%"
    } else {
        containerGrid.style.width = "80%:"
        text.forEach((elemento) =>{
            user.style.fontSize = "10rem"
            elemento.style.display = "block"
            })
        for(let i = 0; i < icons.length; i++) {
            if(i == 0) {
                icons[0].removeAttribute("class")
                icons[0].classList.add("fa-solid")
                icons[0].classList.add("fa-thumbtack")
                icons[0].classList.add("sidebar-icons")
                icons[i].style.fontSize = "1.4rem"
            }
            if(i == 1) {
                icons[i].style.fontSize = "10rem"
            } else {
                icons[i].style.fontSize = "1.4rem"
            }
        }
        sidebar.dataset.status = "open"
        sidebar.style.width = "20%"
    }
    
})