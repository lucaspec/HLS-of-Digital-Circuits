from src.utilities.ilp_manager import *
from src.utilities.cdfg_manager import *
import logging

############################################################################################################################################
############################################################################################################################################
#
#	`MRT` CLASS
#
############################################################################################################################################
#	DESCRIPTION:
#					The following class is used for the Modulo Reservation Table (MRT) for resource sharing in pipelined SDC
############################################################################################################################################
#	ATTRIBUTES:
#					- mrt : is the MRT dictionary where the keys are the clock cycles and the values are lists of operations
############################################################################################################################################
#	FUNCTIONS:
#					- generate : it generates the MRT for a given ILP solution
#					- is_legal : it checks if the MRT is legal
############################################################################################################################################
############################################################################################################################################

class MRT: # Modulo Reservation Table (MRT)
	def __init__(self, ilp):
		self.mrt = {}
		self.generate(ilp)

	# function to generate the MRT
	def generate(self, ilp):
		# TODO: write your code here

		loop_latency = int(ilp.get_max_latency_solution())
		print('loop latency = ', loop_latency)

		# initialize dicitionary with empty arrays
		for cycle in range(loop_latency + 1):
			self.mrt[cycle] = []

		for cycle in range(loop_latency + 1):
			# get all scheduled operations in current cycle
			ops = ilp.get_variables_solution(cycle)

			# populate dictionary considering this and future loop iterations
			i = cycle
			while(i < loop_latency + 1):
				self.mrt[i].extend(ops)

				i += ilp.get_II_solution()

		print(f'MRT table: {self.mrt}')


	# function to check legal MRT
	def is_legal(self, operation, clock_time, max_allowed_instances, operations_solved):
		# TODO: write your code here

		print(operation)

		# list of ops in that cycle
		ops = self.mrt[clock_time]
		print(f'ops in cycle {clock_time}: {ops}')

		# only consider type of given operation
		operations_solved_type = [op for op in operations_solved if op.attr['type'] == operation.attr['type']]
		print(f'operations_solved_type = {operations_solved_type}')

		# evaluate number of scheduled ops in that cycle 
		nr_ops = 1
		for op in ops:
			if op in operations_solved_type:
				nr_ops += 1
		
		# check if there are more instances of an operation than allowed
		return nr_ops <= max_allowed_instances
		


############################################################################################################################################
############################################################################################################################################
#
#	`RESOURCE` CLASS
#
############################################################################################################################################
#	DESCRIPTION:
#					The following class is used for resource sharing in CDFG (Control DataFlow Graph) representing a function.
############################################################################################################################################
#	ATTRIBUTES:
#					- resource_dic : dictionary containing resources
#					- ilp : ILP problem of the class ILP
#					- constraint_set : set of constraints of the class CONSTRAINT_SET
#					- opt_function : optimization function of the class OPT_FUNCTION
#					- log: logger object used to output logs
############################################################################################################################################
#	FUNCTIONS:
#					- set_ilp_tuple : set ilp, constraints and optimization function
#					- set_resource_constraints : set resource constraints
# 					- add_resource_constraints : setting up the maximum resource usage per res type in the constraint set
#					- add_resource_constraints_pipelined : add resources constraints for pipelined scheduling
############################################################################################################################################
############################################################################################################################################

allowed_resources = ["load", "add", "mul", "div", "zext"]

class Resources:
	def __init__(self, parser, resource_dic=None, log=None):
		assert(parser != None) # ensure Parser is different from None
		self.cdfg = parser.get_cdfg() # save the CDFG of the parser
		self.cfg = parser.get_cfg() # save the CFG of the parser
		if log != None:
			self.log = log
		else:
			self.log = logging.getLogger('resource') # if the logger is not given at object generation, create a new one
		self.resource_dic = {}
		if resource_dic != None:
			self.set_resource_constraints(resource_dic)
		self.ilp = None
		self.constraint_set = None
		self.opt_function = None

	# function to set ilp, constraints and optimization function
	def set_ilp_tuple(self, ilp, constraint_set, opt_function):
		if ilp == None:
			self.ilp = ILP(log=self.log)
		else:
			self.ilp = ilp
		self.constraint_set = constraint_set
		self.opt_function = opt_function

	# function to set the resource constraints using a dictionary input
	def set_resource_constraints(self, resource_dic):
		for resource in resource_dic:
			if not(resource in allowed_resources): # the resource type should be present in the list of allowed resource types
				self.log.error("Resource {0} is not allowed (allowed resources = {1})".format(resource, allowed_resources))
				continue
			if resource in self.resource_dic:
				self.log.warning("Resource {0} is already present in the dictionary. \n\tOld value = {1} New value = {2}".format(resource, self.resource_dic[resource], resource_dic[resource]))
			self.resource_dic[resource] = resource_dic[resource]

	# function for setting up the maximum resource usage per res type in the constraint set
	def add_resource_constraints(self, ilp, constraints, opt_function):
		self.set_ilp_tuple(ilp, constraints, opt_function)
		# TODO: write your code here
		# get the topological order 
		ordering = get_topological_order(self.cdfg)
		list_of_bbs = set(get_cdfg_nodes(self.cfg))
		for bb in list_of_bbs:
			ordering_in_bb = [n for n in ordering if n.attr['bbID'] == bb] # get topological order within a BB
			for resource in self.resource_dic:
				constraint = self.resource_dic[resource] # number of allowed instances of this resource
				ordered_op_list = [n for n in ordering_in_bb if n.attr['type'] == resource] # get topological order for a certain op type
				#print(ordered_op_list)
				for i in range(len(ordered_op_list)-constraint):
					# add resource constraint
					self.constraint_set.add_constraint({f'sv{ordered_op_list[i]}': 1, f'sv{ordered_op_list[i+constraint]}': -1}, "leq", -1) 


	# function to add resources constraints for pipelined scheduling
	def add_resource_constraints_pipelined(self, ilp, constraints, opt_function, budget):
		self.set_ilp_tuple(ilp, constraints, opt_function)
		# TODO: write your code here

		mrt_class = MRT(self.ilp) # MRT object containing execution cycle of each operation according to ilp solution
		operations_solved = [] # list of operations for which cycle has been decided
		constraints_list = [] # list of new constraints added and to remove in case of failure

		ordering = get_topological_order(self.cdfg)
		schedQueue = [op for op in ordering if op.attr['bbID'] == 'for.body' and op.attr['type'] in self.resource_dic] # initial queue containing all resource constrained operations
		print('schedQueue: ', schedQueue)

		while(len(schedQueue) and budget >= 0):
			
			print(budget)

			operation = schedQueue.pop(0) # pop resource critical operation
			sv_operation = self.ilp.get_ilp_solution()[f'sv{operation}'] # retrieve starting time of operation
			print(sv_operation)
								
			# check if the operation and its execution time are valid according to resource constraint considering the list of solved operations
			if mrt_class.is_legal(operation, sv_operation, self.resource_dic[operation.attr['type']], operations_solved):
				constraint_id = self.constraint_set.add_constraint({f'sv{operation}': 1}, "eq", sv_operation) # if operation is legal, execute at precise cycle
				constraints_list.append(constraint_id)
				print(constraint_id)
				operations_solved.append(operation)
			else:
				constraint_id = self.constraint_set.add_constraint({f'sv{operation}': 1}, "geq", sv_operation + 1) # if operation cannot be executed this cycle, it should be scheduled next cycle
				constraints_list.append(constraint_id)
				print(constraint_id)
				self.ilp.set_constraints(self.constraint_set)
				status = self.ilp.solve_ilp() # compute new solution due to new constraint
				
				if status == 1: # check feasibility
					schedQueue.insert(0, operation)
					print(schedQueue)
					mrt_class.generate(self.ilp) # generate new table for new scheduling solution
				else:
					for constraint_id in constraints_list: 
						self.constraint_set.remove_constraint(constraint_id) # since unfeasibile, remove added constraints
					return False # fail
			
			budget -= 1
		
		if len(schedQueue):
			for constraint_id in constraints_list:
				self.constraint_set.remove_constraint(constraint_id) # since unfeasibile, remove added constraints
			return False # fail
		else:
			return True # success
