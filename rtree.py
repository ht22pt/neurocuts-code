class Node:
    def __init__(self, iid, depth, ranges, points):
        self.id = iid
        self.depth = depth
        self.ranges = ranges
        self.points = points
        self.children = None

    def get_state(self):
        return [len(self.points)] + self.ranges

class RTree:
    def __init__(self, points, leaf_threshold):
        self.points = points
        self.leaf_threshold = leaf_threshold
        self.ranges = [min([x for (x, y) in points]), max([x for (x, y) in points]), min([y for (x, y) in points]), max([y for (x,y) in points])]
        self.next_id = 0
        self.root = Node(self.next_id, 1, self.ranges, self.points)
        #self.next_id += 1
        self.current_node = self.root

    def get_current_node(self):
        pass

    def is_leaf(self, node):
        pass

    def get_next_node(self):
        pass

    def compute_result(self):
        pass

    def cut_node(self, node, cut_dimension, cut_num):
        pass
