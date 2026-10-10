import socket
import os
import json

from discovery import buscar_dispositivos


HOST = ""
HTTP_PORT = 8080
WEB_DIR = "web"


def iniciar_http():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    servidor.bind((HOST, HTTP_PORT))
    servidor.listen(5)

    print(f"[HTTP] Servidor disponível na porta {HTTP_PORT}...")

    while True:
        conexao, endereco = servidor.accept()

        requisicao = conexao.recv(2000)

        if not requisicao:
            conexao.close()
            continue

        partes = requisicao.split(b" ")

        metodo = partes[0].decode()
        rota = partes[1].decode()

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
                resposta = (
                    "HTTP/1.1 404 Not Found\r\n"
                    "Content-Type: text/plain; charset=utf-8\r\n"
                    "Content-Length: 19\r\n"
                    "\r\n"
                    "Pagina nao encontrada"
                )

                conexao.sendall(resposta.encode())
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


        # POST /buscar - chama a descoberta UDP
        elif metodo == "POST" and rota == "/buscar":

            print("[HTTP] Solicitada busca de dispositivos.")

            dispositivos = buscar_dispositivos()

            corpo = json.dumps(dispositivos).encode() ## de json para bytes

            cabecalho = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json; charset=utf-8\r\n"
                f"Content-Length: {len(corpo)}\r\n"
                "\r\n"
            )

            conexao.sendall(cabecalho.encode())
            conexao.sendall(corpo)


        conexao.close()


if __name__ == "__main__":
    iniciar_http()