import random
from core.predicates import PredicateFactory

class DNAMutator:
    def __init__(self, components):
        self.components = components 

    def mutate(self):
        """Randomizes block order and injects dead paths."""
        random.shuffle(self.components)
        mutated_output = ""
        
        for block in self.components:
            r = random.randint(0, 100)
            mutated_output += f"\nif {r} < 101:\n    {block}"
            if random.random() > 0.9:
                mutated_output += f"\nelse:\n    pass"
                
        return mutated_output

    def apply_opaque_layer(self, code_blocks):
        factory = PredicateFactory()
        final_blocks = []
        
        for block in code_blocks:
            junk = "print('DEBUG_TRACE_ID_' + str(random.randint(100, 999)))"
            # Logic for wrapping with predicates
            p = factory.get_true()
            wrapped = f"if {p}:\n    {block}\nelse:\n    {junk}"
            final_blocks.append(wrapped)
            
        return final_blocks
