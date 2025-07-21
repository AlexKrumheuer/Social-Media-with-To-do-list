async function loadMessages(){
    const receiver = document.querySelector(".receiverId")
    let friendId = receiver.dataset.friendId
    try {
        const response = await fetch(`/dashboard/api/messages/${friendId}`);
        if (!response.ok) throw new Error("Erro ao carregar mensagens");

        const messages = await response.json();

        const container = document.querySelector(".message");
        container.innerHTML = "";

        messages.forEach(msg => {
            const div = document.createElement("div");
            if(msg.sender_id != friendId) {
                div.style.justifyContent = "right"
                div.innerHTML = `
                <p style="background-color: var(--secondbackground-color); color: #fff;">${msg.content} 
                <span style="font-size: 0.7rem;">${msg.hora}</span>
                </p>
            `;
            } else {
                div.style.justifyContent = "left"
                div.innerHTML = `
                <p>${msg.content} 
                <span style="font-size: 0.7rem;">${msg.hora}</span>
                </p>`
            }
        
            container.appendChild(div);
        });

        if(firstLoad) {
            container.scrollTop = container.scrollHeight; // scroll para o fim
            firstLoad = false
        }
        

    } catch (error) {
        console.error(error);
    }
}

const formSendMessage = document.getElementById("formMessage")
const messageDiv = document.querySelector(".message")
let firstLoad = true

formSendMessage.addEventListener("submit", (event) =>{
    event.preventDefault()
    
    const content = document.getElementById("inputMessage").value
    const receiver = document.querySelector(".receiverId")
    let destinatario_id = receiver.dataset.friendId


    fetch("/dashboard/send_message", {
        method:"POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify ({
            content: content,
            destinatario_id: destinatario_id
        })
    })
    .then(response => response.json())
    .then(()=> {
        document.getElementById("inputMessage").value = ""
        
        loadMessages()
    })
    .catch(error => {
        console.error("Error to send message: ", error)
    })
})

setInterval(loadMessages, 500)
