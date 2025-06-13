#!/usr/bin/env python

import angr
import claripy

# Load the firmware
p = angr.Project('a.out', auto_load_libs=False)

# Create symbolic argument
sym_arg = claripy.BVS('sym_arg',  32)

# Cannot pass it is as program args, use global var
sym = p.loader.find_symbol('s_header')
if sym is None:
    raise Exception("Symbol s_header not found!")
global_addr = sym.rebased_addr

# Will looking for _abort() call
sym = p.loader.find_symbol('_abort')
if sym is None:
    raise Exception("Symbol not found!")
abort_addr = sym.rebased_addr

# Go to program entry point
state = p.factory.entry_state()

# Save the symbolic argument to the global var
state.memory.store(global_addr, sym_arg)

# Now we manage the simulation
sm = p.factory.simulation_manager(state)

# Try to resolve the _abort() call symbolically
sm.explore(find=abort_addr)

found = sm.found[0]
answer = found.solver.eval(sym_arg, cast_to=bytes)
print("Solution:", answer)
