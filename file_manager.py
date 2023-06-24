

import math
CHUNK_SIZE = 2*1024

class Tree_node:
    def __init__(self, value, is_file, parent=None, descendent=None, sibling=None):
        self.value = value
        self.is_file = is_file
        self.parent = parent
        self.descendent = descendent
        self.sibling = sibling
        
class File_manager:
    def __init__(self):
        self.root = Tree_node("/", False)

    def insert_node(self, path, is_file):
        parent, is_found = self.find_node(path)
        if is_found: return False

        node = Tree_node(path, is_file)
        node.parent = parent
        parent_descedent = parent.descendent
        if not parent_descedent:
            parent.descendent = node
        else:
            while parent_descedent.sibling:
                parent_descedent = parent_descedent.sibling
            parent_descedent.sibling = node
        
        while parent_descedent:
            parent_descedent = parent_descedent.sibling
        
        parent_descedent = node
        return True

    def find_node(self, path):
        path_folders = path.split('/')
        node = self.root.descendent
        last_node = self.root
        for folder in path_folders:
            while node and node.value != folder:
                node = node.sibling
            if not node:
                return False
            last_node = node
            node = node.descendent
        return last_node, node.is_file

    def list_nodes(self, node, metadata):
        if node:
            print(f"{node.value}\t{metadata[node.value].first}\t{math.ceil(1.0 * metadata[node.value].second / CHUNK_SIZE)}")
            self.list_nodes(node.descendent, metadata)
            self.list_nodes(node.sibling, metadata)
    
    def list(self, metadata):
        self.list_nodes(self.root, metadata)