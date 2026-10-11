import socket
import os
import json
import hashlib


HOST = ""
TCP_PORT = 5001

CHUNK_SIZE = 4096 ## ler o arquivo por chucks(partes)
DOWNLOAD_DIR = "downloads"


def calcular_hash(caminho):
    hash_sha256 = hashlib.sha256()

    with open(caminho, "rb") as arquivo: # r = read  -  b = binary   ## ABRIR EM BINARIO PARA ENVIAR QQ TIPO DE ARQUIVO
        while True:
            bloco = arquivo.read(CHUNK_SIZE) 

            if not bloco:
                break

            hash_sha256.update(bloco) # quando chegar ao final do arquivo, read() devolve: b""

    return hash_sha256.hexdigest() 



def receber_exatamente(conexao, quantidade):
    dados = b"" # b significa byte , começamos com uma sequência de bytes vazia

    while len(dados) < quantidade:
        parte = conexao.recv(quantidade - len(dados))

        if not parte:
            raise ConnectionError("A conexão foi encerrada antes do esperado.")

        dados += parte

    return dados


def receber_arquivo():
    servidor = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # AF_INET → IPv4   ---- SOCK_STREAM → TCP

    servidor.bind((HOST, TCP_PORT)) ## ASSOCIA SERVIDOR A PORTA
    servidor.listen(1)

    print(f"[TCP] Aguardando arquivos na porta {TCP_PORT}...")


        ### protocolo - regra 
    while True:

        conexao, endereco = servidor.accept() # accept() bloqueia até alguém conectar → ('192.168.1.20', 54321)
         # conexao é o socket específico daquela conexão.
        print(f"[TCP] Conexão recebida de {endereco[0]}:{endereco[1]}")

        
        # os primeiros 4 bytes da conexão representam o tamanho dos metadados
        tamanho_metadata_bytes = receber_exatamente(conexao, 4)

        tamanho_metadata = int.from_bytes(tamanho_metadata_bytes,byteorder="big") # os próximos X bytes pertencem ao metadata

        # Recebe os metadados
        metadata_bytes = receber_exatamente(conexao,tamanho_metadata) # temos algo tipo b'{"nome": "foto.jpg", "tamanho": 5000, "sha256": "..."}' EM BYTES

        metadata = json.loads(metadata_bytes.decode()) ## decode transforma: bytes → string
        # JSON.LOADS transforma a string JSON em py 

        nome = os.path.basename(metadata["nome"]) # pega apenas o nome do arquivo idepentente do diretorio odne tiver
        tamanho = metadata["tamanho"]
        hash_esperado = metadata["sha256"]

        print("[TCP] - Arquivo:", nome)
        print("[TCP] - Tamanho:", tamanho, "bytes")
        print("[TCP] - SHA-256 esperado:", hash_esperado)

        #garantir q a pasta distino existe
        os.makedirs(DOWNLOAD_DIR, exist_ok=True) 
        destino = os.path.join(DOWNLOAD_DIR,nome) # downloads/nome.jpg

        # Diz ao remetente que está pronto
        conexao.sendall(b"READY") # "recebi os metadados, entendi tudo e estou pronto para receber o arquivo"

        hash_recebido = hashlib.sha256() # prepara o hash

        bytes_restantes = tamanho

        ##  a transferência em si
        with open(destino, "wb") as arquivo: ## w = write -- b = binary
            while bytes_restantes > 0:

                bloco = conexao.recv(min(CHUNK_SIZE, bytes_restantes)) 
                # min serve não pedir 4096 se só faltam, por exemplo, 700 bytes.

                if not bloco: # se não vier nada, significa que a conexão acabou antes do arquivo terminar
                    raise ConnectionError(
                        "Conexão encerrada durante a transferência."
                    )

                arquivo.write(bloco) # grava aquele pedaço no arquivo

                hash_recebido.update(bloco) # adiciona esse bloco ao cálculo do SHA-256

                bytes_restantes -= len(bloco)

        hash_final = hash_recebido.hexdigest()

        print("[TCP] SHA-256 recebido:", hash_final)

        if hash_final == hash_esperado:
            print("[TCP] Arquivo recebido corretamente.")
            conexao.sendall(b"OK")

        else:
            print("[TCP] Erro: os hashes são diferentes.")
            conexao.sendall(b"ER")

        conexao.close()


def enviar_arquivo(ip,porta_tcp, caminho):

    if not os.path.isfile(caminho):
        print(f"[ERRO] Arquivo não encontrado: {caminho}")
        return

    nome = os.path.basename(caminho)
    tamanho = os.path.getsize(caminho)
    hash_arquivo = calcular_hash(caminho)

    metadata = {
        "nome": nome,
        "tamanho": tamanho,
        "sha256": hash_arquivo
    }

    # um socket não envia dicionário Python diretamente dicionário Python ->  string JSON
    metadata_bytes = json.dumps(metadata).encode() 

    cliente = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    cliente.connect((ip, porta_tcp)) # Esse é o ponto em que as duas partes do MiniDrop se encontram:  udp descob ip e porta e usamos aq

    # Primeiro enviamos o tamanho dos metadados
    cliente.sendall(
        len(metadata_bytes).to_bytes( 4, byteorder="big")
    )

    # Depois os próprios metadados
    cliente.sendall(metadata_bytes)

    resposta = receber_exatamente(cliente, 5) ## ready tem 5 bytes

    if resposta != b"READY":
        print("[TCP] O receptor não está pronto.")
        cliente.close()
        return

    print("[TCP] Receptor pronto. Enviando arquivo...")

    with open(caminho, "rb") as arquivo: # abre o arquivo para leitura binária.
        while True:

            bloco = arquivo.read(CHUNK_SIZE)

            if not bloco:
                break

            cliente.sendall(bloco)

    resultado = receber_exatamente(cliente, 2) # ok e er tem 2 bytes

    if resultado == b"OK":
        print("[TCP] Transferência concluída e SHA-256 verificado.")
        sucesso = True


    else:
        print("[TCP] O arquivo recebido apresentou erro de integridade.")
        sucesso = False

    cliente.close()
    return sucesso # o hppt precisa saber se o tcp terminou correto

if __name__ == "__main__":
    modo = input("1 = receber arquivo | 2 = enviar arquivo: ")

    if modo == "1":
        receber_arquivo()

    elif modo == "2":
        ip = input("IP do destino: ")
        porta_tcp = int(input("Porta TCP do destino: "))
        caminho = input("Caminho do arquivo: ")

        enviar_arquivo(ip, porta_tcp, caminho)