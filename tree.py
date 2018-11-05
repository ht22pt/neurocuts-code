import math

import torch

class Rule:
    def __init__(self, ranges):
        # each range is left inclusive and right exclusive, i.e., [left, right)
        self.ranges = ranges
        self.names = ["src_ip", "dst_ip", "src_port", "dst_port", "proto"]

    def is_intersect(self, dimension, left, right):
        return not (left >= self.ranges[dimension*2+1] or \
            right <= self.ranges[dimension*2])

    def __str__(self):
        result = ""
        for i in range(len(self.names)):
            result += "%s:[%d, %d) " % (self.names[i],
                self.ranges[i*2], self.ranges[i*2+1])
        return result

class Node:
    def __init__(self, ranges, rules, depth):
        self.ranges = ranges
        self.rules = rules
        self.depth = depth
        self.children = []

        if self.ranges != None:
            self.state = torch.tensor([[i/20. for i in self.ranges]])

    def compact_ranges(self):
        self.ranges = self.rules[0].ranges.copy()
        for rule in self.rules:
            for i in range(len(self.ranges)//2):
                self.ranges[i*2] = min(self.ranges[i*2], rule.ranges[i*2])
                self.ranges[i*2+1] = max(self.ranges[i*2+1], rule.ranges[i*2+1])
        self.state = torch.tensor([[i/20. for i in self.ranges]])

    def is_leaf(self):
        return len(self.rules) == 1

    def get_state(self):
        return self.state

    def __str__(self):
        result = "Depth:%d\nRange:\n%s\nRules:\n" % (self.depth, str(self.ranges))
        for rule in self.rules:
            result += str(rule) + "\n"
        return  result

class Tree:
    def __init__(self, ranges, rules):
        # hyperparameters
        self.cuts_per_dimension = 2

        self.rules = rules
        self.root = Node(ranges, rules, 1)
        self.root.compact_ranges()
        self.current_node = self.root
        self.nodes_to_cut = [self.root]
        self.depth = -1

    def get_depth(self):
        return self.depth

    def get_current_node(self):
        return self.current_node

    def is_finish(self):
        return len(self.nodes_to_cut) == 0

    def cut_current_node(self, action):
        self.depth = max(self.depth, self.current_node.depth + 1)
        node = self.current_node
        cut_dimension = action
        range_left = node.ranges[cut_dimension*2]
        range_right = node.ranges[cut_dimension*2+1]
        cut_num = min(self.cuts_per_dimension, range_right - range_left)
        range_per_cut = math.ceil((range_right - range_left) / cut_num)

        children = []
        for i in range(cut_num):
            child_ranges = node.ranges.copy()
            child_ranges[cut_dimension*2] = range_left + i * range_per_cut
            child_ranges[cut_dimension*2+1] = min(range_right,
                range_left + (i+1) * range_per_cut)

            child_rules = []
            for rule in node.rules:
                if rule.is_intersect(cut_dimension,
                    child_ranges[cut_dimension*2],
                    child_ranges[cut_dimension*2+1]):
                    child_rules.append(rule)

            child = Node(child_ranges, child_rules, node.depth + 1)
            children.append(child)

        node.children.extend(children)
        children.reverse()
        self.nodes_to_cut.pop()
        self.nodes_to_cut.extend(children)
        self.current_node = self.nodes_to_cut[-1]
        return children

    def get_next_node(self):
        self.nodes_to_cut.pop()
        if len(self.nodes_to_cut) > 0:
            self.current_node = self.nodes_to_cut[-1]
        else:
            self.current_node = None
        return self.current_node

    def print_layers(self, layer_num = 5):
        nodes = [self.root]
        for i in range(layer_num):
            if len(nodes) == 0:
                return

            print("Layer", i)
            next_layer_nodes = []
            for node in nodes:
                print(node)
                next_layer_nodes.extend(node.children)
            nodes = next_layer_nodes

def test():
    print("========== rule ==========")
    rule = Rule([0, 10, 0, 10, 10, 20, 0, 0, 0, 0])
    print(rule)

    print("========== node ==========")
    rules = []
    rules.append(Rule([0, 10, 0, 10, 10, 20, 10, 15, 0, 0]))
    rules.append(Rule([0, 100, 0, 100, 0, 100, 20, 30, 0, 0]))
    rules.append(Rule([0, 100, 0, 100, 0, 100, 40, 50, 0, 0]))
    ranges = [0, 1000, 0, 1000, 0, 1000, 0, 1000, 0, 1000]
    node = Node(ranges, rules, 1)
    print(node)
    node.compact_ranges()
    print(node)

    print("========== tree ==========")
    rules = []
    rules.append(Rule([0, 10, 0, 10, 0, 1, 0, 1, 0, 1]))
    rules.append(Rule([0, 10, 10, 20, 0, 1, 0, 1, 0, 1]))
    rules.append(Rule([10, 20, 0, 10, 0, 1, 0, 1, 0, 1]))
    rules.append(Rule([10, 20, 10, 20, 0, 1, 0, 1, 0, 1]))
    ranges = [0, 1000, 0, 1000, 0, 1000, 0, 1000, 0, 1000]
    tree = Tree(ranges, rules)
    tree.cut_current_node(0)
    tree.print_layers()

    tree.cut_current_node(1)
    tree.get_next_node()
    tree.get_next_node()
    tree.cut_current_node(1)
    tree.print_layers()

if __name__ == "__main__":
    test()
