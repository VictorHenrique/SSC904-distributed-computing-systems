import math
import rpyc
from rpyc.utils.server import ThreadedServer
import random
import uuid

BLOCK_SIZE = 100
REPLICATION_FACTOR = 3
MINIONS = {"1": ("127.0.0.1", 8000),
           "2": ("127.0.0.1", 8500),
           "3": ("127.0.0.1", 9000),
           "4": ("127.0.0.1", 9500)}

class MainService(rpyc.Service):
    def __init__(self) -> None:
        self.file_block = {}
        self.block_minion = {}
        self.minions = MINIONS

        self.block_size = BLOCK_SIZE
        self.replication_factor = REPLICATION_FACTOR

    def read(self, file):
        mapping = []
        for blk in self.file_block[file]:
            minion_addr = []
            for m_id in self.block_minion[blk]:
                minion_addr.append(self.minions[m_id])

            mapping.append({"block_id": blk, "block_addr": minion_addr})
        return mapping

    def write(self, file, size):
        self.file_block[file] = []
        num_blocks = int(math.ceil(float(size) / self.block_size))
        return self.alloc_blocks(file, num_blocks)

    def alloc_blocks(self, file, num_blocks):
        return_blocks = []
        for _ in range(num_blocks):
            block_id = str(uuid.uuid1()) 
            minion_ids = random.sample(list(self.minions.keys()), self.replication_factor)
            minion_addr = [self.minions[m] for m in minion_ids]
            self.block_minion[block_id] = minion_ids
            self.file_block[file].append(block_id)

            return_blocks.append({"block_id": block_id, "block_addr": minion_addr})
        return return_blocks

if __name__ == "__main__":
    t = ThreadedServer(MainService(), port=2131, protocol_config={'allow_public_attrs': True})
    t.start()
