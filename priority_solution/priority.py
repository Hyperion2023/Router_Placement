import numpy as np
from classes import PrioritySolution

def priority(
	data,
	initial_state: np.array,
	fitness_function,
	num_iterations: int,
	evaluation_delay: int,
	verbose:bool = True
):
	return PrioritySolution(
		data=data,
		initial_state=initial_state,
		fitness_function=fitness_function,
		verbose=verbose
	).run(
		num_iterations=num_iterations,
		evaluation_delay=evaluation_delay
	)