function addFriend(usuarioId) {
    fetch("/dashboard/add_friend", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ amigo_id: usuarioId }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log("bem sucedido");
            location.reload();
        } else {
            alert("Erro ao adicionar amigo.");
        }
    })
    .catch(error => {
        console.error("Erro na requisição:", error);
        alert("Falha ao se conectar ao servidor.");
    });
}

function acceptRequest(usuarioId) {
    fetch("/dashboard/accept_request", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ amigo_id: usuarioId }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert("Erro ao aceitar solicitação.");
        }
    })
    .catch(error => {
        console.error("Erro na requisição:", error);
        alert("Falha ao se conectar ao servidor.");
    });
}
