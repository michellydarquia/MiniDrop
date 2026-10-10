import socket

h = open('index.html', 'r') ## O PROGRAMA APENAS ABRE O ARQUIVO INDEX EM MODO LEITURA `R`
homepage = h.read() ## GUARDA TUDO NESSA VAR


## AF_INET = utilize a família de endereços IPv4.
## SOCK_STREAM = crie um socket orientado a fluxo. Na prática, SOCK_STREAM é utilizado com TCP.


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # crie um socket que irá realizar uma comunicação TCP utilizando IPv4.
print(s)
print(hex(id(s))) ## PRINTA O identificador EM HEXADECIMAL daquele objeto dentro do Python.

s.bind(('', 8080)) #  associa o socket a um endereço local e a uma porta.
# O '' significa que ele aceita conexões através dos endereços/interfaces locais disponíveis naquela máquina. 

# '' = binds to all interfaces
# Binding to port 0 --> bind to a OS-assigned random port

s.listen(5) # passa a ficar esperando pedidos de conexão.
# O 5 está relacionado à fila de conexões pendentes que podem aguardar atendimento.


try:
	while True: # faz o servidor continuar rodando indefinidamente.
		ws, addr = s.accept() # aceita essa conexão e devolve duas coisas:
		# addr - contém informações sobre quem se conectou, como o endereço IP e a porta do cliente.
		# ws - é um novo socket, criado especificamente para conversar com aquele cliente.

		print('newsock', ws)
		print('add', addr, '\n')
		data = ws.recv(2000) # recv - “Agora que existe uma conexão com o cliente, espere o cliente me enviar dados.”
		
		P = data.split(b' ') #GET / HTTP/1.0 -> [GET, /, HTTP/1.0]
		# P[0] = b'GET'
		# P[1] = b'/'
		# P[2] = b'HTTP/1.1...'
		# O b aparece porque os dados recebidos pelo socket chegam como bytes, e não como uma string Python comum.

		#print(P)


		if P[0] == b'GET':
		#print(P[0])
			if P[1] == b'/': ##    O / representa a raiz do site.
				#print(P[1])
				
				# Aqui o servidor está montando manualmente uma mensagem HTTP de resposta.
				# 200 significa que a requisição foi atendida com sucesso.
				resp = ('HTTP/1.0 200 OK\r\n' + 'Content-Type: text/html\r\n' + 'Content-Length: ' + str(len(homepage)) + '\r\n\r\n' + (homepage))
				resp = str.encode(resp) # Até aqui resp era uma string Python. Só que o socket não envia uma string diretamente; ele trabalha com bytes. 
				ws.sendall(resp) # envia a resposta através dessa conexão ws.
			elif P[1] == b'/sobre':
				# envia página sobre.html
				body = '<html><body><h1>Sobre</h1><p>Projeto de servidor HTTP da disciplina de Redes de Computadores 1.</p></body></html>'
				response = (
					'HTTP/1.0 200 OK\r\n'
					+ 'Content-Type: text/html\r\n'
					+ 'Content-Length: ' + str(len(body.encode())) + '\r\n\r\n'
					+ body
				)

				print(response)
				ws.sendall(response.encode())
				ws.close()
			else:
				ext = P[1].rpartition(b'.')[-1]
				#print(ext, type(ext)) # b'jpg' <class 'bytes'>
				ext = ext.decode()

				if ext == 'html':
					content_type = 'text/html'
				elif ext == 'css':
					content_type = 'text/css'
				elif ext == 'txt':
					content_type = 'text/plain'
				elif ext == 'png':
					content_type = 'image/png'
				elif ext == 'jpg' or ext == 'jpeg':
					content_type = 'image/jpeg'
				else:
					content_type = 'application/octet-stream'
				
				try:
					#print(ext, type(ext)) # jpg <class 'str'>
					f = open(P[1][1:], 'rb')
					figure = f.read()
					
					response = (
						'HTTP/1.0 200 OK\r\n'
					  + 'Content-Type: ' + content_type + '\r\n'
					  + 'Content-Length: ' + str(len(figure)) + '\r\n\r\n'
					)					
					print(response)
					ws.sendall(response.encode())
					ws.sendall(figure)
				except FileNotFoundError:
					body = '<html><body><h1>404 Not Found</h1></body></html>'
					response = (
						'HTTP/1.0 404 Not Found\r\n'
						+ 'Content-Type: text/html\r\n'
						+ 'Content-Length: ' + str(len(body.encode())) + '\r\n\r\n'
						+ body
					)
					print(response)
					ws.sendall(response.encode())
					ws.close()

					
except KeyboardInterrupt:
	print(" terminado pelo usuario")
ws.close()
s.close()

# sudo fuser -i -k 8080/tcp
# roda Wireshark (loopback:lo), roda Server, roda browser (127.0.0.1:8080), compara com index.htm
# roda TcpServerNew3.py
# aponta browser para localhost:8080
# examinar Wireshark
# examina Terminal que roda Server
