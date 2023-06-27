from argparse import ArgumentParser
import proxy
import socket
import select
import threading

class Proxy:
    def __init__(self, socket_version=5):
        self.username = "uname"
        self.password = "pwd"
        self.SOCKS_VERSION = socket_version 
    
    def handle_client(self, connection):
        version, num_of_methods = connection.recv(2)
        methods = self.get_avaiable_methods(num_of_methods, connection)
        if 2 not in set(methods):
            connection.close()
            return

        connection.sendall(bytes([self.SOCKS_VERSION, 2]))
        if not self.verify_credentials(connection):
            return
        
        version, cmd, _, addr_type = connection.recv(4)
        if addr_type == 1:
            addr = socket.inet_ntoa(connection.recv(4))
        elif addr_type == 3:
            domain_length = connection.recv(1)[0]
            domain = connection.recv(domain_length)
            addr = socket.gethostbyname(addr)
        
        port = int.from_bytes(connection.recv(2), 'big', signed=False)
        try:
            if cmd == 1:
                remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote.connect((addr, port))
                bind_addr = remote.getsockname()
                print(f"* Connected to {addr} on port {port}")
            else:
                connection.close()
            
            addr = int.from_bytes(socket.inet_aton(bind_addr[0], 'big', signed=False))
            port = bind_addr[1]
            reply = b''.join([
                self.SOCKS_VERSION.to_bytes(1, 'big'), 
                int(0).to_bytes(1, 'big'), 
                int(0).to_bytes(1, 'big'), 
                int(1).to_bytes(1, 'big'), 
                addr.to_bytes(4, 'big'), 
                port.to_bytes(2, 'big')
            ])
        except Exception as e:
            reply = self.generate_failed_reply(addr_type, 5)
        
        connection.sendall(reply)
        if reply[1] == 0 and cmd == 1:
            self.exchange_loop(connection, remote)
            
        connection.close()
    
    def exchange_loop(self, client, remote):
        while True:
            r, w, e = select.select([client, remote], [], [])
            if client in r:
                data = client.recv(4096)
                if remote.send(data) <= 0:
                    break
            
            if remote in r:
                data = client.recv(4096)
                if client.send(data) <= 0:
                    break

    def generate_failed_reply(self, addr_type, err):
        return b''.join([
            self.SOCKS_VERSION.to_bytes(1, 'big'),
            err.to_bytes(1, 'big'),
            int(0).to_bytes(1, 'big'),
            addr_type.to_bytes(1, 'big'),
            int(0).to_bytes(4, 'big'),
            int(0).to_bytes(4, 'big')
        ])

    def verify_credentials(self, connection):
        version = ord(connection.recv(1))
        uname_len = ord(connection.recv(1))
        uname = connection.recv(uname_len).decode('utf-8')

        pwd_len = ord(connection.recv(1))
        pwd = connection.recv(pwd_len).decode('utf-8')

        if uname == self.username and pwd == self.password:
            response = bytes([version, 0])
            connection.sendall(response)
            return True

        response = bytes([version, 0xFF])
        connection.sendall(response)
        connection.close()
        return False
            
    def get_avaiable_methods(self, num_of_methods, connection):
        return [ord(connection.recv(1)) for _ in range(num_of_methods)]
    
    def run(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen() 

        print(f"Socket running on {host}, port {port}")
        
        while True:
            conn, addr = s.accept()
            print("* new connection from {addr}")
            t = threading.Thread(target=self.handle_client, args=(conn,))
            t.start()


if __name__ == "__main__":
    proxy = Proxy()
    proxy.run("127.0.0.1", 3000)