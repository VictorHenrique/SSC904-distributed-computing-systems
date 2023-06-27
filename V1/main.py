from server import *
from file_server import *
from threading import Thread

n_replicates = 3

def main():
    server = Server(n_replicates)
    
    file_servers = [File_server(f"node_0{i}") for i in range(4)] 
    
    for file_server in file_servers:
        server.add_file_server(file_server)

    threads = []
    for file_server in file_servers:
        threads.append(Thread(target=file_server.run()))

    server.run()


if __name__ == "__main__":
    main()