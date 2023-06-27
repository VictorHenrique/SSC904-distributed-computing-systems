import os
from file_manager import File_manager

class Server:
    def __init__(self, n_replicates=3):
        self.n_replicates = n_replicates
        self.file_servers = []
        self.file_manager = File_manager()
        self.num_replicates = 0
        self.id_count = 0
        self.metadata = {}

    def parse_command(self):
        return input(">> ").split(' ')

    def add_file_server(self, server):
        self.file_servers.append(server)

    def usage(self):
        pass 
    
    def list_usage(self):
        pass

    def insert_usage(self):
        pass
    
    def run(self):
        while True:
            args = self.parse_cmd()
            
            match args[0]:
                case '':
                    print("Blank input")
                    self.usage()
                    continue
                
                case "quit":
                    print("Ending program")
                    exit()

                case "ls":
                    if len(args) > 1:
                        self.list_usage()
                    else:
                        print("file\tFileID\tChuckNumber")
                        self.file_manager.list(self.metadata)
                
                case "insert":
                    if len(args) != 3:
                        self.insert_usage()
                        continue
                    
                    file = None
                    try:
                        file = open(f"{args[1]}", "ab")
                    except:
                        print("Error openining the file")
                        continue
                        
                    if not self.file_manager.insert_node(args[2], is_file=True):
                        print("Error creating file. Maybe it already exists in the file system")
                        continue
                    
                    buffer = file.read()
                    ordered_file_servers = sorted(self.file_servers, key = lambda x: x.size())
                    
                    self.id_count += 1
                    for i in range(self.n_replicates):
                        self.metadata[args[2]] = (self.id_count, file.tell())
                        ordered_file_servers[i].cmd = 'insert'
                        ordered_file_servers[i].fid = self.id_count
                        ordered_file_servers[i].buffer = buffer
                        ordered_file_servers[i].finished = False
                
                case "read":
                    if len(args) not in [3,4]:
                        self.read_usage()
                        continue
                    
                    if args[1] not in self.metadata:
                        print("Error: no such file in distributed file system")
                        continue
                        
                    for i in range(len(self.file_servers)):
                        self.file_manager[i].cmd = args[0]
                        tmp_metadata = self.metadata[args[1]]
                        self.file_servers[i].fid = tmp_metadata.first
                        self.file_servers[i].finished = False
                
                case "search":
                    if len(args) != 3:
                        self.search_usage()
                        continue
                    
                    for i in range(len(self.file_servers)):
                        self.file_servers[i].cmd = "search"
                        self.file_servers[i].fid = int(args[1])
                        self.file_servers[i].offset = int(args[2])
                        self.file_servers[i].finished = False
                case _:
                    print("Error: unknown command")
            