function resetPassword() {
    let form = document.getElementById("reset_your_password-form")
    if (!form) return;

    form.addEventListener("submit", (event) => {
        event.preventDefault()

        const formData = new FormData()
        formData.append("currentPassword", form.currentPassword.value)
        formData.append("newPassword", form.newPassword.value)
        formData.append("confirmNewPassword", form.confirmNewPassword.value)

        fetch("/dashboard/reset_password", {
            method: "POST",
            body: formData,
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert("Senha alterada com sucesso!");
                window.location.reload();
            } else {
                alert(data.message || "Erro ao salvar os dados.");
            }
        })
        .catch((error) => {
            console.error("Erro ao enviar dados:", error)
            alert("Erro na requisição. Tente novamente mais tarde.")
        })
    })
}
