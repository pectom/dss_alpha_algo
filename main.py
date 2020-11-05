from bpmnalphatemplate import MyGraph
from more_itertools import pairwise, first, last


def determine_all_successors(direct_succession):
    events = set()
    for successors in direct_succession.values():
        for event in successors:
            events.add(event)
    return events


def determine_all_events(direct_succession):
    return determine_all_successors(direct_succession).union(direct_succession.keys())


def determine_all_events_from_log(log):
    return set([item for sublist in log for item in sublist])


def determine_end_set_events(direct_succession):
    return determine_all_events(direct_succession) - direct_succession.keys()


def determine_start_set_events(direct_succession):
    return direct_succession.keys() - determine_all_successors(direct_succession)


# a -> b <=> ...ab... and not ...ba...
def calculate_causality(direct_succession, sequences):
    causality = {}
    events = determine_all_events(direct_succession)
    for event1 in events:
        for event2 in events:
            if event1 in direct_succession.keys() and event2 in direct_succession[event1]:
                if (event2 not in direct_succession.keys() or event1 not in direct_succession[event2]) or \
                        (event1 in sequences.keys() and event2 in sequences[event1]):
                    if event1 not in causality.keys():
                        causality[event1] = set()
                    causality[event1].add(event2)
    return causality


# a || b <=>
def calculate_parallel_event(direct_succession, sequences):
    parallel_events = set()
    events = determine_all_events(direct_succession)
    for event1 in events:
        for event2 in events:
            if event1 in direct_succession.keys() and event2 in direct_succession[event1]:
                if event2 in direct_succession.keys() and event1 in direct_succession[event2]:
                    if event1 in sequences.keys() and event2 not in sequences[event1]:
                        parallel_events.add((event1, event2))
    return parallel_events


# a inv-> b
def calculate_inv_causality(causality):
    inv_causality = {}
    for key, value in causality.items():
        if len(value) == 1:
            event = next(iter(value))
            if event not in inv_causality.keys():
                inv_causality[event] = set()
            inv_causality[event].add(key)
    return inv_causality


# a /\ b <=> ...aba...
def calculate_subsequences(log):
    subsequences = {}
    for trace in log:
        triples = [[trace[i], trace[i + 1], trace[i + 2]] for i in range(len(trace) - 2)]
        for triple in triples:
            if triple[0] == triple[2] and triple[0] != triple[1]:
                if triple[0] not in subsequences.keys():
                    subsequences[triple[0]] = set()
                subsequences[triple[0]].add(triple[1])
    return subsequences


def calculate_sequences(log):
    sequences = {}
    subsequences = calculate_subsequences(log)
    for event1 in subsequences.keys():
        for event2 in subsequences[event1]:
            if event2 in subsequences.keys() and event1 in subsequences[event2]:
                if event1 not in sequences.keys():
                    sequences[event1] = set()
                sequences[event1].add(event2)
    return sequences


def calculate_direct_succession(log):
    direct_succession = {}
    for trace in log:
        for event_pair in pairwise(trace):
            if first(event_pair) not in direct_succession.keys():
                direct_succession[first(event_pair)] = set()
            direct_succession[first(event_pair)].add(last(event_pair))
    return direct_succession


def calculate_short_loops(log):
    events_in_short_loops = {}
    for trace in log:
        idx = 0
        while idx < len(trace) - 1:
            if trace[idx] == trace[idx + 1]:
                previous = trace[idx - 1]
                i = idx
                # TODO border cases (aaax, xaaa)
                while trace[i] == trace[idx]:
                    i += 1
                next = trace[i]
                if trace[idx] not in events_in_short_loops.keys():
                    events_in_short_loops[trace[idx]] = set()
                events_in_short_loops[trace[idx]].add((previous, next))
                idx = i
            else:
                idx += 1
    return events_in_short_loops


if __name__ == '__main__':
    log = [
        ['x', 'a', 'y'],
        ['x', 'a', 'b', 'a', 'y'],
        ['x', 'a', 'b', 'a', 'b', 'a', 'y'],
        ['x', 'a', 'a', 'a', 'y'],
        ['x', 'a', 'a', 'y'],
        ['x', 'y'],
    ]

    # log = [
    #     ['a', 'b', 'c', 'd', 'e', 'g'],
    #     ['a', 'b', 'c', 'd', 'f', 'g'],
    #     ['a', 'c', 'b', 'd', 'e', 'g'],
    #     ['a', 'c', 'b', 'd', 'f', 'g'],
    # ]

    direct_successions = calculate_direct_succession(log)

    start_set_events = determine_start_set_events(direct_successions)
    end_set_events = determine_end_set_events(direct_successions)

    subsequences = calculate_subsequences(log)
    print(subsequences)
    sequences = calculate_sequences(log)
    print(sequences)

    short_loops = calculate_short_loops(log)
    print(short_loops)

    causality = calculate_causality(direct_successions, sequences)
    parallel_events = calculate_parallel_event(direct_successions, sequences)

    inv_causality = calculate_inv_causality(causality)

    G = MyGraph()

    # adding split gateways based on causality
    for event in causality:
        if len(causality[event]) > 1:
            if tuple(causality[event]) in parallel_events:
                G.add_and_split_gateway(event, causality[event])
            else:
                G.add_xor_split_gateway(event, causality[event])
        else:
            source = list(causality[event])[0]
            if event in short_loops.keys():
                for (prev, next) in short_loops[event]:
                    G.add_xor_split_gateway(event, [next, event])

    # adding merge gateways based on inverted causality
    for event in inv_causality:
        if len(inv_causality[event]) > 1:

            if tuple(inv_causality[event]) in parallel_events:
                G.add_and_merge_gateway(inv_causality[event], event)
            else:
                G.add_xor_merge_gateway(inv_causality[event], event)
        elif len(inv_causality[event]) == 1:
            source = list(inv_causality[event])[0]
            if event in short_loops.keys():
                for (prev, next) in short_loops[event]:
                    G.edge(prev, event)
                    G.add_xor_split_gateway(event, [next, event])
            elif source not in short_loops.keys():
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
