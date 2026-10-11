import socket

HOST = ""
UDP_PORT = 5000

NOME = socket.gethostname()
TCP_PORT = 5001

# Durante teste no mesmo computador:
#BROADCAST_IP = "127.0.0.1"

# PCs diferentes:
BROADCAST_IP = "255.255.255.255"


def responder_descoberta():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))

    print(f"[UDP] Ouvindo porta {UDP_PORT}...")

    while True:
        data, address = udp_socket.recvfrom(1024)

        mensagem = data.decode()

        if mensagem == "DISCOVER":
            resposta = f"HERE|{NOME}|{TCP_PORT}"

            udp_socket.sendto(
                resposta.encode(),
                address
            )

        print(f"[UDP] Respondi descoberta para {address[0]}:{address[1]}")

def buscar_dispositivos():
    busca_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    busca_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)

    busca_socket.settimeout(2)

    busca_socket.sendto(b"DISCOVER",(BROADCAST_IP, UDP_PORT))

    dispositivos = []

    print("[UDP] Buscando dispositivos...")

    while True:
        try:
            data, address = busca_socket.recvfrom(1024)

            mensagem = data.decode()

            partes = mensagem.split("|")

            if len(partes) == 3 and partes[0] == "HERE":
                nome = partes[1]
                porta_tcp = int(partes[2])
                ip = address[0]

                dispositivo = {
                    "nome": nome,
                    "ip": ip,
                    "porta_tcp": porta_tcp
                }

                dispositivos.append(dispositivo)

        except socket.timeout:
            break

    busca_socket.close()

    return dispositivos





if __name__ == "__main__":
    modo = input("1 = responder | 2 = buscar: ")

    if modo == "1":
        responder_descoberta()

    elif modo == "2":
        encontrados = buscar_dispositivos()

        if encontrados:
            print("\nDispositivos encontrados:")

            for dispositivo in encontrados:
                print(dispositivo)

        else:
            print("Nenhum dispositivo encontrado.")