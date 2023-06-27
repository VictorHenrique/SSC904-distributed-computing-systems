import os
import sys
import rpyc
import logging

logging.basicConfig(level=logging.DEBUG)

def get(proxy, file):
    f = proxy.read(file)
    if not f:
        logging.info("File not found")
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

def _help():
    help_str = """
        Avaiable commands:
            - put <src> <dest>: stores <src> as <dest>.
            - get <file>: recovers <file> from storage
    """
    print(help_str)

def main(args):
    connection = rpyc.connect("127.0.0.1", port=2131)
    proxy = connection.root

    if args[0] == 'get':
        get(proxy, args[1])
    elif args[0] == 'put':
        put(proxy, args[1], args[2])
    elif args[0] == 'help':
        _help()
    else:
        logging.error("Unknown command. Use 'help' to see avaiable commands.")
    
if __name__ == "__main__":
    main(sys.argv[1:])
    