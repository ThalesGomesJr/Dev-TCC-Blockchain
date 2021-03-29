import socket 

#realiza o controle de conexão entre os nós
HOST = ''
PORT = 12000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(4)

nodes_ip = []
while True:
    print("Aguardando conexão")
    
    #Conecta o nó ao socket
    conn, address_ip = server.accept()
    
    #Recebe o token do socket
    token = conn.recv(1024).decode()
    print(token)

    if token == 'node0':
        ip = str("http://" + address_ip[0]) + ":5000"
        if ip not in nodes_ip:
            nodes_ip.append(ip)
        
        response = str(nodes_ip)
        conn.sendto(str.encode(response), address_ip)
    

    if token == 'node1':
        ip = str("http://" + address_ip[0]) + ":5001"
        if ip not in nodes_ip:
            nodes_ip.append(ip)
        
        response = str(nodes_ip)
        conn.sendto(str.encode(response), address_ip)

    if token == 'node2':
        ip = str("http://" + address_ip[0]) + ":5002"
        if ip not in nodes_ip:
            nodes_ip.append(ip)
        
        response = str(nodes_ip)
        conn.sendto(str.encode(response), address_ip)
    
    if token == 'node3':
        ip = str("http://" + address_ip[0]) + ":5003"
        if ip not in nodes_ip:
            nodes_ip.append(ip)
        
        response = str(nodes_ip)
        conn.sendto(str.encode(response), address_ip)