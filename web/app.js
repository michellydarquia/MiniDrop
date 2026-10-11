const botaoBuscar = document.getElementById("buscar");
const dispositivosDiv = document.getElementById("dispositivos");

const arquivo = document.getElementById("arquivo");
const nomeArquivo = document.getElementById("nome-arquivo");

const botaoEnviar = document.getElementById("enviar");
const statusDiv = document.getElementById("status");


let dispositivosEncontrados = [];


function atualizarBotaoEnviar() {

    const destino = document.querySelector('input[name="destino"]:checked');

    botaoEnviar.disabled = !(destino && arquivo.files.length > 0);
}


arquivo.addEventListener("change", function () {

    if (arquivo.files.length > 0) {
        nomeArquivo.textContent = arquivo.files[0].name;
    }

    atualizarBotaoEnviar();
});


botaoBuscar.addEventListener("click", async function () {

    dispositivosDiv.innerHTML = '<div class="vazio">Buscando dispositivos...</div>';

    const resposta = await fetch("/buscar", { // await é espere a resposta chegar antes de continuar
        method: "POST"
    });

    dispositivosEncontrados = await resposta.json(); // transforma em estrutua javaschipt

    dispositivosDiv.innerHTML = "";

    if (dispositivosEncontrados.length == 0) {
        dispositivosDiv.innerHTML = '<div class="vazio">Nenhum dispositivo encontrado.</div>';
        return;
    }


    dispositivosEncontrados.forEach(function (dispositivo, indice) {  // percorre cada disp e faz o card

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


        const radio = item.querySelector("input");

        radio.addEventListener("change", atualizarBotaoEnviar);
    });

});


botaoEnviar.addEventListener("click", async function () {

    const destinoSelecionado = document.querySelector('input[name="destino"]:checked');

    if (!destinoSelecionado || arquivo.files.length == 0) {
        return;
    }


    const dispositivo = dispositivosEncontrados[destinoSelecionado.value];

    const arquivoSelecionado = arquivo.files[0];


    statusDiv.textContent = "Enviando arquivo...";

    botaoEnviar.disabled = true;


    const resposta = await fetch("/enviar", {
        method: "POST",

        headers: {
            "Content-Type": "application/octet-stream",
            "X-Filename": encodeURIComponent(arquivoSelecionado.name),
            "X-Destination-IP": dispositivo.ip,
            "X-Destination-Port": dispositivo.porta_tcp
        },

        body: arquivoSelecionado
    });


    const resultado = await resposta.json();

    statusDiv.textContent = resultado.mensagem;

    atualizarBotaoEnviar();

});