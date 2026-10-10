const botaoBuscar = document.getElementById("buscar");
const dispositivosDiv = document.getElementById("dispositivos");

const arquivo = document.getElementById("arquivo");
const nomeArquivo = document.getElementById("nome-arquivo");

const botaoEnviar = document.getElementById("enviar");


arquivo.addEventListener("change", function () {

    if (arquivo.files.length > 0) {
        nomeArquivo.textContent = arquivo.files[0].name;
    }

});


botaoBuscar.addEventListener("click", async function () {

    dispositivosDiv.innerHTML = '<div class="vazio">Buscando dispositivos...</div>';

    const resposta = await fetch("/buscar", { // await é espere a resposta chegar antes de continuar
        method: "POST"
    });

    const dispositivos = await resposta.json(); // transforma em estrutua javaschipt

    dispositivosDiv.innerHTML = "";

    if (dispositivos.length == 0) {
        dispositivosDiv.innerHTML = '<div class="vazio">Nenhum dispositivo encontrado.</div>';
        return;
    }

    dispositivos.forEach(function (dispositivo, indice) { // percorre cada disp e faz o card

        const item = document.createElement("label");

        item.className = "dispositivo";

        item.innerHTML = `
            <input type="radio" name="destino" value="${indice}">

            <div>
                <strong>${dispositivo.nome}</strong>
                <span>${dispositivo.ip} • TCP ${dispositivo.porta_tcp}</span>
            </div>
        `;

        dispositivosDiv.appendChild(item);
    });

});