import os
import sys
import rpyc
import logging
import argparse

logging.basicConfig(level=logging.DEBUG)

def get(main, file):
    f = main.read(file)
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

def put(main, source, destination):
    size = os.path.getsize(source)
    blocks = main.write(destination, size)

    with open(source) as f:
        for block in blocks:
            data = f.read(main.block_size)
            block_id = block['block_id']
            minions = block['block_addr']

            minion, minions = minions[0], minions[1:]
            host, port = minion

            connection = rpyc.connect(host, port=port)
            connection.root.put(block_id, data, minions)

def help():
    help_str = """
        Usage:
            - put --source_file <src> --dest_file <dest>: stores <src> as <dest>.
            - get --source_file <file>: recovers <file> from storage
    """
    print(help_str)

def main(opt):
    try:
        connection = rpyc.connect("127.0.0.1", port=2131)
        main = connection.root

        if opt.cmd == 'get':
            if opt.source_file:
                get(main, opt.source_file)
            else:
                help()
        elif opt.cmd == 'put':
            if opt.source_file and opt.dest_file:
                put(main, opt.source_file, opt.dest_file)
            else:
                help()
        elif opt.cmd == 'help':
            help()
        else:
            print('Unknown command.')
            help()
    
    except ConnectionRefusedError as e:
        logging.error('Connection refused error. Try again')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--cmd', type=str)
    parser.add_argument('--source_file', type=str)
    parser.add_argument('--dest_file', type=str)
    opt = parser.parse_args()
    
    main(opt)