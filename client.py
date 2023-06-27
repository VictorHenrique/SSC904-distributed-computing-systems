import os
import sys
import rpyc
import logging

logging.basicConfig(level=logging.DEBUG)


def get(proxy, file):
    f = proxy.read(file)
    if not f:
        logging.info("file not found")
        return

    for block in f:
        if len(block['block_addr']) == 0:
            logging.error("No blocks found. Maybe a corrupt file")

        for host, port in block['block_addr']:
            try:
                connection = rpyc.connect(host, port=port).root
                data = connection.get(block['block_id'])
                if data:
                    sys.stdout.write(data)
                    break
            except:
                continue

def put(proxy, source, destination):
    size = os.path.getsize(source)
    blocks = proxy.write(destination, size)

    with open(source) as f:
        for block in blocks:
            data = f.read(proxy.block_size)
            block_id = block['block_id']
            minions = block['block_addr']

            minion, minions = minions[0], minions[1:]
            host, port = minion

            connection = rpyc.connect(host, port=port)
            connection.root.put(block_id, data, minions)

def main(args):
    connection = rpyc.connect("localhost", port=12345)
    proxy = connection.root

    match args[0]:
        case 'get':
            get(proxy, args[1])
        case 'put':
            put(proxy, args[1], args[2])
        case _:
            logging.error("Unkwon command. Possible commands: 'put <src file> <dest file>' and 'get <file>'")

if __name__ == "__main__":
    main(sys.argv[1:])
    