import socket

h = open('index.html', 'r')
homepage = h.read()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(s)
print(hex(id(s)))

s.bind(('', 8080))
# '' = binds to all interfaces
# Binding to port 0 --> bind to a OS-assigned random port
s.listen(5)

try:
	while True:
		ws, addr = s.accept()
		print('newsock', ws)
		print('add', addr, '\n')
		data = ws.recv(2000)
		
		P = data.split(b' ') #GET / HTTP/1.0 -> [GET, /, HTTP/1.0]
		#print(P)
		if P[0] == b'GET':
		#print(P[0])
			if P[1] == b'/':
				#print(P[1])
				resp = ('HTTP/1.0 200 OK\r\n' + 'Content-Type: text/html\r\n' + 'Content-Length: ' + str(len(homepage)) + '\r\n\r\n' + (homepage))
				resp = str.encode(resp)
				ws.sendall(resp)
			else:
				ext = P[1].rpartition(b'.')[-1]
				#print(ext, type(ext)) # b'jpg' <class 'bytes'>
				ext = ext.decode()
				#print(ext, type(ext)) # jpg <class 'str'>
				f = open(P[1][1:], 'rb')
				figure = f.read()
				response = 'HTTP/1.01 200 OK\r\n' + 'Content-Type: image/' + ext + '\r\n' + 'Content-Length: ' + str(len(figure)) + '\r\n\r\n'
				print(response)
				ws.sendall(response.encode())
				ws.sendall(figure)
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
