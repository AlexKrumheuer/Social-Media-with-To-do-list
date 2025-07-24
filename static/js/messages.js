async function loadMessages() {
    const receiver = document.querySelector(".receiverId")
    if (!receiver) return;

    let friendId = receiver.dataset.friendId
    try {
        const response = await fetch(`/dashboard/api/messages/${friendId}`);
        if (!response.ok) throw new Error("Erro ao carregar mensagens");

        const messages = await response.json();

        const container = document.querySelector(".message");
        if (!container) return;

        container.innerHTML = "";

        messages.forEach(msg => {
            const div = document.createElement("div");
            div.style.display = "flex";
            div.style.margin = "5px 0";

            if (msg.sender_id != friendId) {
                div.style.justifyContent = "right";
                div.innerHTML = `
                    <p style="background-color: var(--secondbackground-color); color: #fff; padding: 8px; border-radius: 10px; max-width: 60%;">
                        ${msg.content}
                        <span style="font-size: 0.7rem; margin-left: 10px;">${msg.hora}</span>
                    </p>
                `;
            } else {
                div.style.justifyContent = "left";
                div.innerHTML = `
                    <p style="background-color: #e4e4e4; padding: 8px; border-radius: 10px; max-width: 60%;">
                        ${msg.content}
                        <span style="font-size: 0.7rem; margin-left: 10px;">${msg.hora}</span>
                    </p>
                `;
            }

            container.appendChild(div);
        });

        // Scroll sempre ao fim
        if(firstLoad) {
            container.scrollTop = container.scrollHeight;
        firstLoad = false;
        }
        

    } catch (error) {
        console.error(error);
    }
}

const formSendMessage = document.getElementById("formMessage")
const messageDiv = document.querySelector(".message")
let firstLoad = true

if (formSendMessage) {
    formSendMessage.addEventListener("submit", (event) => {
        event.preventDefault();

        const input = document.getElementById("inputMessage");
        const content = input.value.trim();
        if (content === "") return;

        const receiver = document.querySelector(".receiverId");
        let receiver_id = receiver.dataset.friendId;

        fetch("/dashboard/send_message", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                content: content,
                receiver_id: receiver_id
            })
        })
        .then(response => response.json())
        .then(() => {
            input.value = "";
            loadMessages();
        })
        .catch(error => {
            console.error("Error to send message: ", error)
        })
    })
}

setInterval(loadMessages, 500)
