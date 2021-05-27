import csv
import sys
sys.setrecursionlimit(9999)

class Node:
    """Class for fusion tree node"""
    def __init__(self, max_keys = None):
        self.keys = []
        self.children = []
        self.key_count = 0

        self.isLeaf = True
        self.m = 0
        self.b_bits = []    # distinguishing bits
        self.m_bits = []    # bits of constant m
        self.gap = 0
        self.node_sketch = 0
        self.mask_sketch = 0
        self.mask_q = 0     # used in parallel comparison

        self.mask_b = 0
        self.mask_bm = 0

        self.keys_max = max_keys
        if max_keys != None:
            # an extra space is assigned so that splitting can be
            # done easily
            self.keys = [None for i in range(max_keys + 1)]
            self.children = [None for i in range(max_keys + 2)]

class FusionTree:
    """Fusion tree class. initiateTree is called after all insertions in
    this example. Practically, node is recalculated if its keys are
    modified."""
    def getDiffBits(self, keys):
        res = []

        bits = 0
        for i in range(len(keys)):
            if keys[i] == None:
                break
            for j in range(i):
                w = self.w
                
                while (keys[i][0] & 1 << w) == (keys[j][0] & 1 << w) and w >= 0:
                    w -= 1
                if w >= 0:
                    bits |= 1 << w
        
        i = 0
        while i < self.w:
            if bits & (1 << i) > 0:
                res.append(i)
            i += 1
        return res

    def getConst(self, b_bits):
        r = len(b_bits)
        m_bits = [0 for i in range(r)]
        for t in range(r):
            mt = 0
            flag = True
            while flag:
                flag = False
                for i in range(r):
                    if flag:
                        break
                    for j in range(r):
                        if flag:
                            break
                        for k in range(t):
                            if mt == b_bits[i] - b_bits[j] + m_bits[k]:
                                flag = True
                                break
                if flag == True:
                    mt += 1
            m_bits[t] = mt
        
        m = 0
        for i in m_bits:
            m |= 1 << i
        return m_bits, m
                        
    def getSketch(self, mask_bits):
        res = 0
        for i in mask_bits:
            res |= 1 << i
        return res

    def sketchApprox(self, node, x):
        xx = x & node.mask_b
        res = xx * node.m

        res = res & node.mask_bm
        return res

    def initiateNode(self, node):
        if node.key_count != 0:
            node.b_bits = self.getDiffBits(node.keys)
            node.m_bits, node.m = self.getConst(node.b_bits)
            node.mask_b = self.getSketch(node.b_bits)

            temp = []
            # bm[i] will be position of b[i] after its multiplication
            # with m[i]. mask_bm will isolate these bits.
            for i in range(len(node.b_bits)):
                temp.append(node.b_bits[i] + node.m_bits[i])
            node.mask_bm = self.getSketch(temp)

            # used to maintain sketch lengths
            r3 = int(pow(node.key_count, 3))

            node.node_sketch = 0
            sketch_len = r3 + 1
            node.mask_sketch = 0
            node.mask_q = 0
            for i in range(node.key_count):
                if node.keys[i] != None:
                    sketch = self.sketchApprox(node, node.keys[i][0])
                    temp = 1 << r3
                    temp |= sketch
                    node.node_sketch <<= sketch_len
                    node.node_sketch |= temp
                    node.mask_q |= 1 << i * (sketch_len)
                    node.mask_sketch |= (1 << (sketch_len - 1)) << i * (sketch_len)
        return

    def __init__(self, word_len = 64, c = 1/5):
        self.keys_max = int(pow(word_len, c))
        self.keys_max = max(self.keys_max, 2)
        self.w = int(pow(self.keys_max, 1/c))
        self.keys_min = self.keys_max // 2

        print("word_len = ", self.w, " max_keys = ", self.keys_max)

        self.root = Node(self.keys_max)
        self.root.isLeaf = True
    
    def splitChild(self, node, x):
        # a b-tree split function. Splits child of node at x index
        z = Node(self.keys_max)
        y = node.children[x]   # y is to be split

        # position of key to propagate
        pos_key = (self.keys_max // 2)

        z.key_count = self.keys_max - pos_key - 1

        # insert first half keys into z
        for i in range(z.key_count):
            z.keys[i] = y.keys[pos_key + i + 1]
            y.keys[pos_key + i + 1] = None
        
        if not y.isLeaf:
            for i in range(z.key_count + 1):
                z.children[i] = y.children[pos_key + i + 1]
        
        y.key_count = self.keys_max - z.key_count - 1

        # insert key into node
        node.keys[x] = y.keys[pos_key]
        
        # same effect as shifting all keys after setting pos_key to None
        del y.keys[pos_key]
        y.keys.append(None)

        # insert z as child at (x + 1)th position
        node.children[x + 1] = z

        node.key_count += 1

    def insert_notsplitting(self, node, k):
        # print(node, node.keys,'\n', node.key_count)
        # insert k into node when no chance of splitting the root
        if node != None and node.isLeaf:
            i = node.key_count
            while i >= 1 and k[0] < node.keys[i - 1][0]:
                node.keys[i][0] = node.keys[i - 1][0]
                i -= 1
            node.keys[i] = k
            node.key_count += 1
            return 
        elif node != None:
            i = node.key_count
            while i >= 1 and k[0] < node.keys[i - 1][0]:
                i -= 1
            # i = position of appropriate child

            if node.children[i].key_count == self.keys_max:
                self.splitChild(node, i)
                if k[0] > node.keys[i][0]:
                    i += 1
            self.insert_notsplitting(node.children[i], k)

    def insert(self, k):
        # This insert checks if splitting is needed
        # then it splits and calls insert_notsplitting

        # if root needs splitting, a new node is assigned as root
        # with split nodes as children
        if self.root.key_count == self.keys_max:
            temp_node = Node(self.keys_max)
            temp_node.isLeaf = False
            temp_node.key_count = 0
            temp_node.children[0] = self.root
            self.root = temp_node
            self.splitChild(temp_node, 0)
            self.insert_notsplitting(temp_node, k)
        else:
            self.insert_notsplitting(self.root, k)
    
    def parallelComp(self, node, k):
        # this function should basically give the index such
        # that sketch of k lies between 2 sketches
        sketch = self.sketchApprox(node, k)
        # This will give repeated sketch patterns to allow for comparison
        # in const time
        sketch_long = sketch * node.mask_q

        res = node.node_sketch - sketch_long

        # mask out unimportant bits
        res &= node.mask_sketch

        # find the leading bit. This leading bit will tell position i of
        # such that sketch(keyi-1) < sketch(k) < sketch(keyi)
        i = 0
        while (1 << i) < res:
            i += 1
        i += 1
        sketch_len = int(pow(node.key_count, 3)) + 1
        return node.key_count - (i // sketch_len)

    def successor(self, k, node = None):
        if node == None:
            node = self.root

        if node.key_count == 0:
            if node.isLeaf:
                return [-1]
            else:
                return self.successor(k, node.children[0])
       
        # the corner cases are not defined.
        # other alternative to handle these would be to have
        # -inf and inf at corners of keys array
        if node.keys[0][0] >= k:
            if not node.isLeaf:
                fin = self.successor(k, node.children[0])
                
                if fin[0] == -1:
                    return node.keys[0]
                else:
                    result = min(node.keys[0][0], fin[0])
                    if result == node.keys[0][0]:
                        return node.keys[0]
                    else:
                        return fin
            else:
                return node.keys[0]
        
        if node.keys[node.key_count - 1][0] < k:
            if node.isLeaf:
                return [-1]
            else:
                return self.successor(k, node.children[node.key_count])

        position = self.parallelComp(node, k)

        if position >= node.key_count:
            print(node.keys, position)
            dump = input()
        
        if position == 0:
            position += 1
            # x = node.keys[position]
        
        # find the common prefix
        # it can be guranteed that successor of k is successor
        # of next smallest element in subtree
        x = max(node.keys[position - 1][0], node.keys[position][0])
        # print("x = ", x)
        common_prefix = 0
        i = self.w
        while i >= 0 and (x & (1 << i)) == (k & (1 << i)):
            # print(i)
            common_prefix |= x & (1 << i) 
            i -= 1
        if i == -1:
            if x == node.keys[position - 1][0]:
                return node.keys[position - 1]
            else:
                return node.keys[position]
        
        temp = common_prefix | (1 << i)

        position = self.parallelComp(node, temp)
        # if position == 0:
        # possible error?
        #     position += 1
        # print("position = ", position, bin(temp))
        if node.isLeaf:
            return node.keys[position]
        else:
            fin = self.successor(k, node.children[position])
            if fin[0] == -1:
                return node.keys[position]
            else:
                return fin

    # def successorSimple(self, node, k):
    #     i = 0
    #     while i < node.key_count and k > node.keys[i][0]:
    #         i += 1
    #     if i < node.key_count and k > node.keys[i][0]:
    #         return node.keys[i]
    #     elif node.isLeaf:
    #         return node.keys[i]
    #     else:
    #         return self.successor(k, node.children[i])

    def predecessor(self, k, node = None):
        if node == None:
            node = self.root

        if node.key_count == 0:
            if node.isLeaf:
                return [-1]
            else:
                return self.predecessor(k, node.children[0])
       
        # the corner cases are not concretely defined.
        # other alternative to handle these would be to have
        # 0 and inf at corners of keys array
        if node.keys[0][0] > k:
            if not node.isLeaf:
                return self.predecessor(k, node.children[0])
            else:
                return [-1]
        
        if node.keys[node.key_count - 1][0] <= k:
            if node.isLeaf:
                return node.keys[node.key_count - 1]
            else:
                final_lst =  self.predecessor(k, node.children[node.key_count])
                res = max(final_lst[0], node.keys[node.key_count - 1][0])
                if res == final_lst[0]:
                    return final_lst
                else:
                    return node.keys[node.key_count - 1]

        position = self.parallelComp(node, k)

        if position >= node.key_count:
            print(node.keys, position, "ERROR? position > key_count")
            dump = input()
        
        if position == 0:
            position += 1
        
        # find the common prefix
        # it can be guranteed that successor of k is successor
        # of next smallest element in subtree
        x = node.keys[position][0]
        common_prefix = 0
        i = self.w
        while i >= 0 and (x & (1 << i)) == (k & (1 << i)):
            common_prefix |= x & (1 << i) 
            i -= 1
        if i == -1:     # i.e. if x is exactly equal to k
            return node.keys[position]
        
        temp = common_prefix | ((1 << i) - 1)
        position = self.parallelComp(node, temp)
        if position == 0:
            if node.isLeaf:
                return node.keys[position]
            final = self.predecessor(k, node.children[1])
            if final[0] == -1:
                return node.keys[position]
            else:
                return final
                
        if node.isLeaf:
            return node.keys[position - 1]
        else:
            final = self.predecessor(k, node.children[position])
            if final[0] == -1:
                return node.keys[position - 1]
            else:
                return final

    def initiate(self, node):
        if node == None:
            node = Node(self.keys_max)
        self.initiateNode(node)
        if not node.isLeaf:
            for i in range(node.keys_max + 1):
                self.initiate(node.children[i])
    
    def initiateTree(self):
        self.initiate(self.root)



# if __name__ == "__main__":
#     # create a fusion tree of degree 3
#     tree = FusionTree(243)
#     f = open("cars.csv", encoding='cp850')
#     f.readline()
#     f_tree_length = 0
#     for i in f:
#         i = i.split(",")
#         lst = [word.strip() for word in i]
#         lst = [int(lst[0])] + lst[1:6] + [int(lst[6])] + lst[7:10] +  [float(lst[10])]
#         tree.insert(lst)
#         f_tree_length += 1
#     f.close()
#     print("Tree length " + str(f_tree_length))
#     tree.initiateTree()

#     ############ FOR LESS THAN and EQUAL TO VALUES (Price and Year) ####################
#     manufacturer = ""
#     price = -1
#     year = 2020
#     output_lst= []

#     for i in range(1, f_tree_length):
#         lst = tree.predecessor(i)
#         # print(lst)
#         if len(output_lst) > 0:
#             if lst != output_lst[-1]:
#                 if manufacturer != "":
#                     if price != -1:
#                         if year != -1:
#                             if lst[1] == manufacturer and lst[10] <= price and lst[6] <= year:
#                                 output_lst.append(lst)
#                         elif lst[1] == manufacturer and lst[10] <= price:
#                             output_lst.append(lst)
#                     elif lst[1] == manufacturer and lst[6] <= year:
#                         output_lst.append(lst)
#                     elif lst[1] == manufacturer and price == -1 and year == -1:
#                         output_lst.append(lst)
#                 elif price != -1 :
#                     if year != -1:
#                         if lst[10] <= price and lst[6] <= year:
#                             output_lst.append(lst)
#                     elif lst[10] <= price:
#                         output_lst.append(lst)
#                 elif year != -1:
#                     if lst[6] <= year:
#                         output_lst.append(lst)
#         else:
#             if manufacturer != "":
#                 if price != -1:
#                     if year != -1:
#                         if lst[1] == manufacturer and lst[10] <= price and lst[6] <= year:
#                             output_lst.append(lst)
#                 elif lst[1] == manufacturer and lst[10] <= price:
#                     output_lst.append(lst)
#                 elif lst[1] == manufacturer and lst[6] <= year:
#                     output_lst.append(lst)
#                 elif lst[1] == manufacturer and price == -1 and year == -1:
#                     output_lst.append(lst)
#             elif price != -1:
#                 if year != -1:
#                     if lst[6] <= year and lst[10] <= price:
#                         output_lst.append(lst)
#                 elif lst[10] <= price:
#                     output_lst.append(lst)
#             elif year != -1:
#                 if lst[6] <= year:
#                     output_lst.append(lst)
#     print(output_lst)


############# FOR GREATER THAN and EQUAL TO VALUES (Price and Year) ####################

    # for i in range(1, f_tree_length):
    #     lst = tree.successor(i)
    #     # print(lst)
    #     if len(output_lst) > 0:
    #         if lst != output_lst[-1]:
    #             if manufacturer != "":
    #                 if price != "":
    #                     if year != "":
    #                         if lst[1] == manufacturer and lst[10] >= price and lst[6] >= year:
    #                             output_lst.append(lst)
    #                     elif lst[1] == manufacturer and lst[10] >= price:
    #                         output_lst.append(lst)
    #                 elif lst[1] == manufacturer and lst[6] >= year:
    #                     output_lst.append(lst)
    #                 elif lst[1] == manufacturer and price == -1 and year == -1:
    #                     output_lst.append(lst)
    #             elif price != "" :
    #                 if year != "":
    #                     if lst[10] >= price and lst[6] >= year:
    #                         output_lst.append(lst)
    #                 elif lst[10] >= price:
    #                     output_lst.append(lst)
    #             elif year != "":
    #                 if lst[6] >= year:
    #                     output_lst.append(lst)
    #     else:
    #         if manufacturer != "":
    #             if price != "":
    #                 if year != "":
    #                     if lst[1] == manufacturer and lst[10] >= price and lst[6] >= year:
    #                         output_lst.append(lst)
    #             elif lst[1] == manufacturer and lst[10] >= price:
    #                 output_lst.append(lst)
    #             elif lst[1] == manufacturer and lst[6] >= year:
    #                 output_lst.append(lst)
    #             elif lst[1] == manufacturer and price == -1 and year == -1:
    #                 output_lst.append(lst)
    #         elif price != "":
    #             if year != "":
    #                 if lst[6] >= year and lst[10] >= price:
    #                     output_lst.append(lst)
    #             elif lst[10] >= price:
    #                 output_lst.append(lst)
    #         elif year != "":
    #             if lst[6] >= year:
    #                 output_lst.append(lst)                
# print(output_lst[-1])
    
    

##    print(tree.root.keys)
##    for i in tree.root.children:
##        if i is not None:
##             print (i, " = ", i.keys)
##             if not i.isLeaf:
##                 for j in i.children:
##                     if j is not None:
##                         print(j.keys)
#     # the tree formed should be like:
#     #      [| 5  | |  16 |]
#     #      /      |       \
#     #     /       |        \
#     # [1, 4]     [15]     [20, 25]
#     # print("\nKeys stored are:")
    # print("Predecessors:")
    # for i in range(26):
    #     print(i, "------------------->", tree.predecessor(i), sep = '\t')
    # print("Successor:")
    # for i in range(26):
    #     print(i, "------------------->", tree.successor(i), sep = '\t')
