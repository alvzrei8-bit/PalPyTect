import random

class DNAMutator:
    def __init__(self, components):
        self.components = components # List of code blocks (VM, Decoders, Junk)

    def mutate(self):
        """Randomizes the order of independent code blocks and injects dead paths."""
        random.shuffle(self.components)
        mutated_output = ""
        
        for block in self.components:
            # Wrap each block in a random-path conditional
            r = random.randint(0, 100)
            mutated_output += f"\nif {r} < 101:\n    {block}"
            # Inject 10% chance of a dead-end branch
            if random.random() > 0.9:
                mutated_output += f"\nelse:\n    pass # Dead Logic Path"
                
        return mutated_output
        
        
        # snippet to be added to core/mutator.py
    from core.predicates import PredicateFactory

    def apply_opaque_layer(self, code_blocks):
    factory = PredicateFactory()
    final_blocks = []
    
    for block in code_blocks:
        junk = "print('DEBUG_TRACE_ID_' + str(random.randint(100, 999)))"
        wrapped = factory.wrap_logic(block, junk)
        final_blocks.append(wrapped)
        
    return final_blocks
    