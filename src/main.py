import threading
import time

from discovery import responder_descoberta
from transfer import receber_arquivo
from http_server import iniciar_http


def main():
    thread_udp = threading.Thread(target=responder_descoberta, daemon=True)
    thread_tcp = threading.Thread(target=receber_arquivo, daemon=True)

    thread_udp.start()
    thread_tcp.start()

    time.sleep(0.2)

    iniciar_http()


if __name__ == "__main__":
    main()