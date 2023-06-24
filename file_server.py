import os

CHUNK_SIZE = 2 * 1024

class File_server:
    def __init__(self, server_name):
        self.server_name = server_name
        self.server_size = 0
        self.buffer = ""
        self.finished = False
        self.data_server = None
        self.cmd = ""
        self.fid = None

    def setup(self):
        try:
            os.mkdir(self.server_name)
        except:
            print("Error: failure creating file server directory")
            exit()

    def insert(self):
        start = 0
        while start < len(self.buffer):
            offset = start / CHUNK_SIZE
            filepath = f"{self.name}/{self.fid}"""

    def read(self):
        pass

    def search(self):
        pass

    def size(self):
        return self.server_size

    def run(self, cmd):
        self.setup()

        while True:
            match self.cmd:
                case "insert":
                    self.server_size += len(self.buffer) / 1024 / 1024
                    self.insert()
                
                case "read":
                    self.read()
                
                case "search":
                    self.search()
                
                case _:
                    pass

            self.finished = True


    