import graphviz

class MyGraph(graphviz.Digraph):
    def __init__(self, *args):
        super(MyGraph, self).__init__(*args)
        self.graph_attr['rankdir'] = 'LR'
        self.node_attr['shape'] = 'Mrecord'
        self.graph_attr['splines'] = 'ortho'
        self.graph_attr['nodesep'] = '0.8'
        self.edge_attr.update(penwidth='2')

    def add_event(self, name):
        super(MyGraph, self).node(name, shape="circle", label="")

    def add_and_gateway(self, *args):
        super(MyGraph, self).node(*args, shape="diamond",
                                  width=".6", height=".6",
                                  fixedsize="true",
                                  fontsize="40", label="+")

    def add_xor_gateway(self, *args, **kwargs):
        super(MyGraph, self).node(*args, shape="diamond",
                                  width=".6", height=".6",
                                  fixedsize="true",
                                  fontsize="35", label="×")

    def add_and_split_gateway(self, source, targets, *args):
        gateway = 'ANDs ' + str(source) + '->' + str(targets)
        self.add_and_gateway(gateway, *args)
        super(MyGraph, self).edge(source, gateway)
        for target in targets:
            super(MyGraph, self).edge(gateway, target)

    def add_xor_split_gateway(self, source, targets, *args):
        gateway = 'XORs ' + str(source) + '->' + str(targets)
        self.add_xor_gateway(gateway, *args)
        super(MyGraph, self).edge(source, gateway)
        for target in targets:
            super(MyGraph, self).edge(gateway, target)

    def add_and_merge_gateway(self, sources, target, *args):
        gateway = 'ANDm ' + str(sources) + '->' + str(target)
        self.add_and_gateway(gateway, *args)
        super(MyGraph, self).edge(gateway, target)
        for source in sources:
            super(MyGraph, self).edge(source, gateway)

    def add_xor_merge_gateway(self, sources, target, *args):
        gateway = 'XORm ' + str(sources) + '->' + str(target)
        self.add_xor_gateway(gateway, *args)
        super(MyGraph, self).edge(gateway, target)
        for source in sources:
            super(MyGraph, self).edge(source, gateway)


