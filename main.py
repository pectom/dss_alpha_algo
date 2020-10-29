from bpmnalphatemplate import MyGraph


def determine_all_successors(direct_succession):
    events = set()
    for successors in direct_succession.values():
        for event in successors:
            events.add(event)
    return events


def determine_all_events(direct_succession):
    return determine_all_successors(direct_succession).union(direct_succession.keys())


def determine_end_set_events(direct_succession):
    return determine_all_events(direct_succession) - direct_succession.keys()


def determine_start_set_events(direct_succession):
    return direct_succession.keys() - determine_all_successors(direct_succession)


def calculate_causality(direct_succession):
    causality = {}
    events = determine_all_events(direct_succession)
    for event1 in events:
        for event2 in events:
            if event1 in direct_succession.keys() and event2 in direct_succession[event1]:
                if event2 not in direct_succession.keys() or event1 not in direct_succession[event2]:
                    if event1 not in causality.keys():
                        causality[event1] = set()
                    causality[event1].add(event2)
    return causality


def calculate_parallel_event(direct_succession):
    parallel_events = set()
    events = determine_all_events(direct_succession)
    for event1 in events:
        for event2 in events:
            if event1 in direct_succession.keys() and event2 in direct_succession[event1]:
                if event2 in direct_succession.keys() and event1 in direct_succession[event2]:
                    parallel_events.add((event1, event2))
    return parallel_events


def calculate_inv_causality(causality):
    inv_causality = {}
    for key, value in causality.items():
        if len(value) == 1:
            event = next(iter(value))
            if event not in inv_causality.keys():
                inv_causality[event] = set()
            inv_causality[event].add(key)
    return inv_causality


if __name__ == '__main__':
    direct_successions = {
        'a': {'b', 'f'},
        'b': {'c', 'd'},
        'c': {'d', 'e'},
        'd': {'c', 'e'},
        'e': {'h'},
        'f': {'g'},
        'g': {'h'},
        'h': {'i', 'j'},
        'i': {'k'},
        'j': {'k'}
    }

    causality = calculate_causality(direct_successions)
    parallel_events = calculate_parallel_event(direct_successions)

    start_set_events = determine_start_set_events(direct_successions)
    end_set_events = determine_end_set_events(direct_successions)

    inv_causality = calculate_inv_causality(causality)

    G = MyGraph()

    # adding split gateways based on causality
    for event in causality:
        if len(causality[event]) > 1:
            if tuple(causality[event]) in parallel_events:
                G.add_and_split_gateway(event, causality[event])
            else:
                G.add_xor_split_gateway(event, causality[event])

    # adding merge gateways based on inverted causality
    for event in inv_causality:
        if len(inv_causality[event]) > 1:
            if tuple(inv_causality[event]) in parallel_events:
                G.add_and_merge_gateway(inv_causality[event], event)
            else:
                G.add_xor_merge_gateway(inv_causality[event], event)
        elif len(inv_causality[event]) == 1:
            source = list(inv_causality[event])[0]
            G.edge(source, event)

    # adding start event
    G.add_event("start")
    if len(start_set_events) > 1:
        if tuple(start_set_events) in parallel_events:
            G.add_and_split_gateway(event, start_set_events)
        else:
            G.add_xor_split_gateway(event, start_set_events)
    else:
        G.edge("start", list(start_set_events)[0])

    # adding end event
    G.add_event("end")
    if len(end_set_events) > 1:
        if tuple(end_set_events) in parallel_events:
            G.add_and_merge_gateway(end_set_events, event)
        else:
            G.add_xor_merge_gateway(end_set_events, event)
    else:
        G.edge(list(end_set_events)[0], "end")

    G.render('simple_graphviz_graph')
    G.view('simple_graphviz_graph')
