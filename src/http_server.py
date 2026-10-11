import socket
import os
import json

from urllib.parse import unquote

from discovery import buscar_dispositivos
from transfer import enviar_arquivo


HOST = ""
HTTP_PORT = 8080
WEB_DIR = "web"
TEMP_DIR = "temp"


def receber_requisicao(conexao):
    dados = b""

    # primeiro recebe até terminar o cabeçalho HTTP
    while b"\r\n\r\n" not in dados:
        parte = conexao.recv(4096)

        if not parte:
            return None

        dados += parte

    cabecalho_bytes, corpo = dados.split(b"\r\n\r\n", 1)

    linhas = cabecalho_bytes.decode().split("\r\n")

    metodo, rota, versao = linhas[0].split(" ")

    cabecalhos = {}

    for linha in linhas[1:]:
        if ":" in linha:
            chave, valor = linha.split(":", 1)
            cabecalhos[chave.strip().lower()] = valor.strip()

    tamanho_corpo = int(cabecalhos.get("content-length", 0))

    # caso o corpo ainda não tenha chegado inteiro
    while len(corpo) < tamanho_corpo:
        parte = conexao.recv(min(4096, tamanho_corpo - len(corpo)))

        if not parte:
            break

        corpo += parte

    return metodo, rota, cabecalhos, corpo


def iniciar_http():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    servidor.bind((HOST, HTTP_PORT))
    servidor.listen(5)

    print(f"[HTTP] Servidor disponível na porta {HTTP_PORT}...")

    while True:
        conexao, endereco = servidor.accept()

        requisicao = receber_requisicao(conexao)

        if not requisicao:
            conexao.close()
            continue

        metodo, rota, cabecalhos, corpo = requisicao

        print(f"[HTTP] {metodo} {rota} - {endereco[0]}")


        # GET - arquivos da interface
        if metodo == "GET":

            if rota == "/":
                caminho = os.path.join(WEB_DIR, "index.html")
                tipo = "text/html"

            elif rota == "/style.css":
                caminho = os.path.join(WEB_DIR, "style.css")
                tipo = "text/css"

            elif rota == "/app.js":
                caminho = os.path.join(WEB_DIR, "app.js")
                tipo = "application/javascript"

            else:
                corpo_resposta = b"Pagina nao encontrada"

                cabecalho = (
                    "HTTP/1.1 404 Not Found\r\n"
                    "Content-Type: text/plain; charset=utf-8\r\n"
                    f"Content-Length: {len(corpo_resposta)}\r\n"
                    "\r\n"
                )

                conexao.sendall(cabecalho.encode())
                conexao.sendall(corpo_resposta)

                conexao.close()
                continue


            with open(caminho, "rb") as arquivo:
                conteudo = arquivo.read()

            cabecalho = (
                "HTTP/1.1 200 OK\r\n"
                f"Content-Type: {tipo}; charset=utf-8\r\n"
                f"Content-Length: {len(conteudo)}\r\n"
                "\r\n"
            )

            conexao.sendall(cabecalho.encode())
            conexao.sendall(conteudo)


        # POST /buscar - descoberta UDP
        elif metodo == "POST" and rota == "/buscar":

            print("[HTTP] Solicitada busca de dispositivos.")

            dispositivos = buscar_dispositivos()

            corpo_resposta = json.dumps(dispositivos).encode()

            cabecalho = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json; charset=utf-8\r\n"
                f"Content-Length: {len(corpo_resposta)}\r\n"
                "\r\n"
            )

            conexao.sendall(cabecalho.encode())
            conexao.sendall(corpo_resposta)


        # POST /enviar - recebe arquivo do navegador e envia via TCP
        elif metodo == "POST" and rota == "/enviar":

            nome = unquote(cabecalhos["x-filename"])
            nome = os.path.basename(nome)

            ip_destino = cabecalhos["x-destination-ip"]
            porta_destino = int(cabecalhos["x-destination-port"])

            print(f"[HTTP] Arquivo recebido do navegador: {nome}")
            print(f"[HTTP] Destino: {ip_destino}:{porta_destino}")

            os.makedirs(TEMP_DIR, exist_ok=True)

            caminho_temp = os.path.join(TEMP_DIR, nome)

            with open(caminho_temp, "wb") as arquivo:
                arquivo.write(corpo)

            sucesso = enviar_arquivo(ip_destino, porta_destino, caminho_temp)

            os.remove(caminho_temp)

            if sucesso:
                resposta = {
                    "ok": True,
                    "mensagem": "Arquivo enviado com sucesso."
                }

            else:
                resposta = {
                    "ok": False,
                    "mensagem": "Erro ao enviar arquivo."
                }

            corpo_resposta = json.dumps(resposta).encode() # de json p bytes

            cabecalho = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json; charset=utf-8\r\n"
                f"Content-Length: {len(corpo_resposta)}\r\n"
                "\r\n"
            )

            conexao.sendall(cabecalho.encode())
            conexao.sendall(corpo_resposta)


        conexao.close()


if __name__ == "__main__":
    iniciar_http()