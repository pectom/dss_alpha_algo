import graphviz

class AlphaPlusGraph(graphviz.Digraph):
    def __init__(self, *args):
        super(AlphaPlusGraph, self).__init__(*args)
        self.graph_attr['rankdir'] = 'LR'
        self.node_attr['shape'] = 'Mrecord'
        self.graph_attr['splines'] = 'ortho'
        self.graph_attr['nodesep'] = '0.8'
        self.edge_attr.update(penwidth='2')

    def add_event(self, name):
        super(AlphaPlusGraph, self).node(name, shape="circle", label="")

    def add_and_gateway(self, *args):
        super(AlphaPlusGraph, self).node(*args, shape="diamond",
                                         width=".6", height=".6",
                                         fixedsize="true",
                                         fontsize="40", label="+")

    def add_xor_gateway(self, *args, **kwargs):
        super(AlphaPlusGraph, self).node(*args, shape="diamond",
                                         width=".6", height=".6",
                                         fixedsize="true",
                                         fontsize="35", label="×")

    def add_and_split_gateway(self, source, targets, *args):
        gateway = 'ANDs ' + str(source) + '->' + str(targets)
        self.add_and_gateway(gateway, *args)
        super(AlphaPlusGraph, self).edge(source, gateway)
        for target in targets:
            super(AlphaPlusGraph, self).edge(gateway, target)


    def add_xor_split_gateway(self, source, targets, *args):
        gateway = 'XORs ' + str(source) + '->' + str(targets)
        self.add_xor_gateway(gateway, *args)
        super(AlphaPlusGraph, self).edge(source, gateway)
        for target in targets:
            super(AlphaPlusGraph, self).edge(gateway, target)

    def add_loop_gateway(self, source, loop, target,  *args):
        gateway1 = 'XORs ' + str(source) + ' -> gateway2'
        gateway2 = 'XORs gateway2 ->' + str(loop)
        self.add_xor_gateway(gateway1, *args)
        self.add_xor_gateway(gateway2, *args)
        super(AlphaPlusGraph, self).edge(source, gateway1)
        super(AlphaPlusGraph, self).edge(gateway1, gateway2)
        super(AlphaPlusGraph, self).edge(gateway2, target)
        super(AlphaPlusGraph, self).edge(gateway2, loop)
        super(AlphaPlusGraph, self).edge(loop, gateway1)

    def add_and_merge_gateway(self, sources, target, *args):
        gateway = 'ANDm ' + str(sources) + '->' + str(target)
        self.add_and_gateway(gateway, *args)
        super(AlphaPlusGraph, self).edge(gateway, target)
        for source in sources:
            super(AlphaPlusGraph, self).edge(source, gateway)

    def add_xor_merge_gateway(self, sources, target, *args):
        gateway = 'XORm ' + str(sources) + '->' + str(target)
        self.add_xor_gateway(gateway, *args)
        super(AlphaPlusGraph, self).edge(gateway, target)
        for source in sources:
            super(AlphaPlusGraph, self).edge(source, gateway)


