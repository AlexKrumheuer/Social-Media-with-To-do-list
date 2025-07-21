function resetPassword() {
    let form = document.getElementById("reset_your_password-form")

    form.addEventListener("submit", (event) => {
        event.preventDefault()

        const formData = new FormData()
    
        formData.append("currentPassword", form.currentPassword.value)
        formData.append("newPassword", form.newPassword.value)
        formData.append("confirmNewPassword", form.confirmNewPassword.value)
        
        // Envia para backend
        fetch("/dashboard/reset_password", {
            method: "POST",
            body: formData,
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.reload()
                } else {
                    alert("Erro ao salvar os dados")
                    window.location.reload()
                }
            })
            .catch((error)=> {
                console.error("Erro ao enviar dados:", error)
                alert("Erro na requisição")
                window.location.reload()
            })
    })
}