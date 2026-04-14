import sys
from typing import List, Tuple

"""
Question D: Tree, TREE!!!

You are given a tree with n nodes.
For any chosen root r, we define a value called the cuteness of the tree as follows:
• Consider all possible sets of k distinct nodes.
• For each set, compute their Lowest Common Ancestor (LCA) when the tree is rooted at r.
• Collect all such LCA results into a set Sᵣ (only distinct nodes).
• The cuteness for root r is the size of this set: f(r) = |Sᵣ|

Goal: Kawaiiness
Compute the total cuteness over all possible roots.

Input
• First line: integer t — number of test cases
• For each test case:
    o First line: integers n and k
        ▪ 2 ≤ 𝑘 ≤ 𝑛 ≤ 2 ∙ 10^5
    o Next n−1 lines: edges of the tree
        ▪ Each line contains u v, meaning an edge between nodes u and v
        
Output
For each test case, output a single integer — the kawaiiness of the tree.
"""


def compute_kawaiiness(t: int, test_cases: List[Tuple[int, int]]):
    remaining = test_cases

    for _ in range(t):
        current, remaining = process_test_cases(remaining)
        kawaiiness = compute_cuteness(current)
        print(kawaiiness)


# Process the test cases to separate the current tree and the rest of the trees
def process_test_cases(test_cases: List[Tuple[int, int]]):
    n, k = test_cases[0]
    current = test_cases[:n]
    rest = test_cases[n:]

    return current, rest


def compute_cuteness(current: List[Tuple[int, int]]):
    # Each root changes the structure of the tree (parent/child relationships).
    # That affects which nodes can become LCAs of k chosen nodes.
    # Your task is to efficiently compute how many nodes can act as LCAs across all roots.

    n = current[0][0]
    k = current[0][1]
    edges = current[1:]

    # Create a Undirected Tree using adjacency list
    tree = [[] for _ in range(n + 1)]
    for u, v in edges:
        tree[u].append(v)
        tree[v].append(u)
    # print(tree)

    # Use DFS to compute the size of the subtree for each node and determine how many nodes can be LCAs for k chosen nodes.
    subtree_size = [0] * (n + 1)
    parent_map = [0] * (n + 1)
    dfs(1, tree, subtree_size, parent_map)

    """ 
    Core Algorithm: Contribution-based LCA counting (per-node perspective)
    Reference: ChatGPT-5.3 & Claude Sonnet 4.6

    Instead of iterating over each root r and computing f(r) directly, we transpose the summation:

    sum_{r=1}^{n} f(r) = sum_{v=1}^{n} contribution(v)

    where contribution(v) = number of roots r under which v can appear as an LCA.

    When the tree is rooted at r, node v can be the LCA of some k-subset if and only if no single "block" around v 
    contains >= (n - k + 1) nodes. A block is defined as a connected component formed by removing v from the tree — 
    one block per neighbor of v.

    For a fixed node v, removing it splits the tree into deg(v) blocks. 
    When we re-root at r (which lies in one of these blocks), that block gets "absorbed" into v's perspective, 
    eliminating it as a threat. Therefore:

    • If 0 large blocks exist: v is a valid LCA under ALL n roots.
    • If 1 large block exists: v is valid under all roots EXCEPT those inside that large block (size = big_blocks[0]).
    • If 2+ large blocks exist: v can never be a valid LCA under any root, 
    since re-rooting can eliminate at most one large block at a time.
    """
    cuteness = []
    threshold = n - k + 1

    for v in range(1, n + 1):
        # Compute the size of each block around v
        blocks = []
        for nb in tree[v]:
            if nb == parent_map[v]:
                blocks.append(n - subtree_size[v])
            else:
                blocks.append(subtree_size[nb])

        # Identify blocks large enough to invalidate v as an LCA
        big_blocks = [b for b in blocks if b >= threshold]
        num_big = len(big_blocks)

        # No large blocks — v is a valid LCA under every root
        if num_big == 0:
            cuteness.append(n)
        # One large block — v is invalid only when root lies inside it
        # Valid under: n - big_blocks[0] roots
        elif num_big == 1:
            cuteness.append(n - big_blocks[0])
        # num_big >= 2: re-rooting can eliminate at most one large block,
        # so v remains invalid under every root — contribution is 0

    # print(cuteness)
    return sum(cuteness)


def dfs(root, tree, subtree_size, parent_map):
    stack = [(root, 0)]
    order = []

    # Record parent and initialize each node's subtree size to 1
    while stack:
        node, parent = stack.pop()
        parent_map[node] = parent
        subtree_size[node] = 1
        order.append(node)

        for neighbor in tree[node]:
            if neighbor != parent:
                stack.append((neighbor, node))

    # Traverse in reverse so children are always processed before their parent
    for node in reversed(order):
        p = parent_map[node]
        if p != 0:
            subtree_size[p] += subtree_size[node]


def start():
    t = int(input())

    test_cases = []
    for _ in range(t):
        n, k = map(int, input().split())
        test_cases.append((n, k))

        for _ in range(n - 1):
            u, v = map(int, input().split())
            test_cases.append((u, v))

    compute_kawaiiness(t, test_cases)


if __name__ == '__main__':
    """
    Usage 1: 
    Run the code with custom test cases by uncommenting the block below and commenting out start().
    
    Expected output:
        2
        9
        17
    """
    # t = 3
    # test_cases = [
    #     (2, 2), (1, 2),
    #     (5, 3), (1, 2), (1, 3), (1, 4), (1, 5),
    #     (6, 3), (1, 2), (1, 3), (2, 4), (2, 5), (3, 6)
    # ]
    #
    # compute_kawaiiness(t, test_cases)

    """
    Usage 2: 
    Run the code with standard input (e.g., from a file or terminal) by uncommenting the line below and comment above.
    
    Example input (typed or piped):
        3
        2 2
        1 2
        5 3
        1 2
        1 3
        1 4
        1 5
        6 3
        1 2
        1 3
        2 4
        2 5
        3 6
    
    Expected output:
        2
        9
        17
    """
    start()
