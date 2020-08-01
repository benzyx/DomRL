
def process_decision(agent, decision, state):

    # Get decision from agent.
    move_indices = agent.choose(decision, state)

    # TODO(benzyx): Enforce that the indices are not repeated.
    if decision.optional:
        if len(move_indices) > decision.num_select:
            raise Exception("Decision election error! Too many moves selected.")
    else:
        if len(move_indices) != decision.num_select:
            raise Exception("Decision election error! Number of moves selected not correct.")

    for idx in move_indices:
        decision.moves[idx].do(state)
        
