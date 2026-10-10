import threading
import time

from discovery import responder_descoberta, buscar_dispositivos
from transfer import receber_arquivo, enviar_arquivo
from http_server import iniciar_http

# threads auxiliares: uma fica ouvindo UDP e outra fica esperando arquivos TCP
thread_udp = threading.Thread(target=responder_descoberta, daemon=True) ## CRIAR A  thread -- target = execute essa função.
thread_tcp = threading.Thread(target=receber_arquivo, daemon=True) # daemon=True significa que são threads auxiliares

thread_udp.start()
thread_tcp.start()
time.sleep(0.2) # só dá tempo das mensagens iniciais das threads aparecerem


def main():
	while True:

		print("\n=== MiniDrop ===")
		print("1 - Buscar dispositivos e enviar arquivo")
		print("0 - Sair")

		opcao = input("Escolha: ")

		if opcao == "1":
			dispositivos = buscar_dispositivos()

			if not dispositivos:
				print("Nenhum dispositivo encontrado.")
				continue

			print("\nDispositivos encontrados:")

			for i, dispositivo in enumerate(dispositivos):
				print(f"{i + 1} - {dispositivo['nome']} - {dispositivo['ip']}:{dispositivo['porta_tcp']}")

			escolha = int(input("Escolha o dispositivo: ")) - 1
			dispositivo = dispositivos[escolha]

			caminho = input("Caminho do arquivo: ").strip().strip('"') # strip espaços extras e depois permite ""

			enviar_arquivo(dispositivo["ip"], dispositivo["porta_tcp"], caminho)

		elif opcao == "0":
			print("MiniDrop encerrado.")
			break

if __name__ == "__main__":
    main()