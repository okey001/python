import ast

s = """
class Hao:

    def __init__(self):
        self.as = 1

    def zhi_chi(self):
        pass

    def wei_wu(self):
        pass

    def you_xi_wang_le(self):
        pass


class YaoWan:

    def __init__(self):
        pass

    class Meta:

        def __init__(self):
            pass

"""

root = ast.parse(s)


def dfs(root, indent=''):
    nodes = ast.iter_child_nodes(root)
    for node in nodes:
        if type(node).__name__ not in ('ClassDef', 'FunctionDef', 'Module'):
            print(type(node))
            continue
        print(indent + node.name)
        dfs(node, indent + '  ')


dfs(root)