# 1EE - Redes de Computadores 1

Projeto de implementação e expansão de um servidor HTTP
a partir do código-base disponibilizado pelo professor.

## Integrantes

- Danielle Stephanie
- Isabella Vitória
- Michely Darquia


## Objetivo

Estudar e implementar conceitos da camada de aplicação,
com foco no protocolo HTTP e em sua comunicação sobre TCP.

O projeto parte do arquivo `TcpServerNew3.py` disponibilizado
pelo professor e será expandido com novas requisições,
tratamentos e um contexto prático.

## Código-base

O servidor original:

- utiliza sockets TCP;
- escuta na porta 8080;
- recebe requisições HTTP;
- reconhece o método GET;
- responde a `GET /`;
- tenta servir arquivos solicitados pelo cliente.

O código original referencia um `index.html`, porém esse
arquivo não foi disponibilizado junto aos arquivos do Classroom.
Por isso, será criado um `index.html` próprio para o projeto.
