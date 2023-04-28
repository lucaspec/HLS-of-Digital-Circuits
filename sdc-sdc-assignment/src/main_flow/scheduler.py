from src.utilities.ilp_manager import *
from src.utilities.cdfg_manager import *
import matplotlib.pyplot as plt
import re
import logging

# function to do sqrt in trivial way
def sqrt(n):
	i = 0
	while (i*i) < n:
		i+=1
	return i

############################################################################################################################################
############################################################################################################################################
#
#	`SCHEDULER` CLASS
#
############################################################################################################################################
#	DESCRIPTION:
#					The following class is used as a scheduler a CDFG (Control DataFlow Graph) representing a function. 
#					It elaborates the CDFG of an IR (Intermediare Representation).
#					Then, it generates its scheduling depending on the scheduling technique selected
############################################################################################################################################
#	ATTRIBUTES:
#					- parser : parser used to generate CDFG after parsing SSA IR
#					- cdfg : CDFG representation of the SSA IR input
#					- cfg : CFG representation of the SSA IR input
#					- sched_tech : scheduling technique selected
#					- sched_sol : scheduling solution
#					- ilp: ilp object
#					- constraints: constraints object
#					- opt_fun: optmization function object
#					- II : Initiation Interval achieved by scheduling solution
#					- log: logger object used to output logs
############################################################################################################################################
#	FUNCTIONS:
#					- set_sched_technique : set scheduling technique
#					- add_artificial_nodes : create super nodes
#					- set_data_dependency_constraints: setting the data dependency constraints
#					- set_II_constraints: setting the initialization interval to the value II_value
#					- add_max_latency_constraint : add max_latency constraint and optimization
#					- add_sink_delays_constraints : add sink delays constraints
#					- set_opt_function: setting the optimiztion function, according to the optimization option
#					- create_scheduling_ilp : create the ILP of the scheduling
#					- solve_scheduling_ilp: solve the ilp and obtain scheduling
#					- get_ilp_tuple : get ilp, constraints and optimization function
#					- get_sink_delays: get delays of sinks after computing solution
#					- print_gantt_chart : prints the gantt chart of a scheduling solution
#					- print_scheduling_summary: it prints the start time of each node into a txt report. If the loop is pipelined, it also prints the achieved II.
############################################################################################################################################
############################################################################################################################################


scheduling_techniques = ["asap", "alap", "pipelined", "naive"]

class Scheduler:

	# initialization of the scheduler with the parser
	def __init__(self, parser, sched_technique, log=None):
		if log != None:
			self.log = log
		else:
			self.log = logging.getLogger('scheduler') # if the logger is not given at object generation, create a new one
		self.parser = parser
		self.cdfg = parser.get_cdfg()
		self.cfg = parser.get_cfg()
		self.add_artificial_nodes() # adding supersource and supersinks to the cdfg
		self.set_sched_technique(sched_technique)
		self.sched_sol = None
		self.II = None
		self.remove_buffer = []

		# set solver options
		self.ilp = ILP(log=log)
		self.constraints = Constraint_Set(self.ilp, log=log)
		self.opt_fun = Opt_Function(self.ilp, log=log)

		# This is how you retrieve information
		for operation_node in get_cdfg_nodes(self.cdfg):
			print(f'Name of the node: {operation_node}')
			print(f'Type: {operation_node.attr["type"]}')
			print(f'Latency: {get_node_latency(operation_node.attr)} \n')

		# loop through the entire graph, and access attributes of edges
		for cdfg_edge in get_cdfg_edges(self.cdfg):
			print(f'For Edge: {cdfg_edge[0]} -> {cdfg_edge[1]}')
			if cdfg_edge.attr["style"] == "dashed":
				print('Edge type: back edge. \n')
			else:
				print('Edge type: normal edge. \n')

		# define ilp variable per each node
		# TODO: write your code here
		for n in self.cdfg:
			self.ilp.add_variable(f"sv{n}", lower_bound = 0, var_type = "i")

		self.ilp.add_variable("II", lower_bound = 0, var_type = "i")


	# function to set scheduling technique
	def set_sched_technique(self, technique):
		assert(technique in scheduling_techniques) # the scheduling technique chosen must belong to the allowed ones
		self.log.info(f'Setting the scheduling technique to be "{technique}"')
		self.sched_tech = technique

	# function for setting the data dependency constraints
	def set_data_dependency_constraints(self, break_bb_connections=False):
		# TODO: write your code here

		# within every BB, iterate over normal edges and set constraints
		list_of_nodes = set(get_cdfg_nodes(self.cdfg))
		list_of_bbs = set(get_cdfg_nodes(self.cfg))
		list_of_edges = set(get_cdfg_edges(self.cdfg))
		
		for bb in list_of_bbs:
			nodes_in_bb = [n for n in list_of_nodes if n.attr['bbID'] == bb]
			for edge in list_of_edges:
				if edge[0] in nodes_in_bb and edge[1] in nodes_in_bb and edge.attr["style"] != "dashed": # only consider intra BB and normal edges
					self.constraints.add_constraint({f'sv{edge[0]}': -1, f'sv{edge[1]}': 1}, "geq", get_node_latency(edge[0].attr)) # add constraint

			# for node in nodes_in_bb:
			# 	list_of_predecessors = self.cdfg.predecessors(node)
			# 	for pre in list_of_predecessors:
			# 		if pre.attr['bbID'] == bb: # only consider predecessors of same BB
			# 			self.constraints.add_constraint({f'sv{pre}': -1, f'sv{node}': 1}, "geq", get_node_latency(pre.attr)) # add constraint



	# function for setting the initialization interval to the value II_value
	def set_II_constraints(self, II_value):
		# TODO: write your code here

		# remove constraints from previous iteration
		for constraint_id in self.remove_buffer:
				self.constraints.remove_constraint(constraint_id)
		self.remove_buffer.clear()

		# add pipelining constraints
		self.II = II_value
		for edge in get_cdfg_edges(self.cdfg):	
			if edge.attr["style"] == "dashed" and (edge[0].attr['type'] != 'br' or edge[1].attr['type'] != 'phi'): # backedge from br to phi is not a data dependency
				constraint_id = self.constraints.add_constraint({f'sv{edge[0]}': 1, f'sv{edge[1]}': -1, 'II': -1}, "leq", -get_node_latency(edge[0].attr))
				self.remove_buffer.append(constraint_id) # track added constraints

		# add II constraint
		constraint_id = self.constraints.add_constraint({'II': 1}, "eq", self.II)
		self.remove_buffer.append(constraint_id) # track added constraint



	# function to add max_latency constraint and optimization
	def add_max_latency_constraint(self):
		# TODO: write your code here
		pass

	# function to add sink delays constraints
	def add_sink_delays_constraints(self, sink_delays):
		# TODO: write your code here
		pass

		# function to get ilp, constraints and optimization function
	def get_ilp_tuple(self):
		# TODO: write your code here
		return self.ilp, self.constraints, self.opt_fun

	# function to get delays of sinks after computing solution
	def get_sink_delays(self):
		# TODO: write your code here
		pass

	# function to create super nodes
	def add_artificial_nodes(self):
		# TODO: write your code here
		list_of_nodes = set(get_cdfg_nodes(self.cdfg))
		list_of_bbs = set(get_cdfg_nodes(self.cfg))

		for cdfg_edge in get_cdfg_edges(self.cdfg):
			if cdfg_edge.attr["style"] == "dashed":
				print(cdfg_edge[0].attr["bbID"])

		for bb in list_of_bbs:
			# add one supersource and supersink node per BB
			id = bb.attr["id"]
			source_node_name = f'ssource_bb{id}'
			sink_node_name = f'ssink_bb{id}'
			self.cdfg.add_node(source_node_name, id = id, bbID = bb, type = 'supersource', label = source_node_name) # add supersource node
			self.cdfg.add_node(sink_node_name, id = id, bbID = bb, type = 'supersink', label = sink_node_name) # add supersink node

			# remove all dashed edges
			dashed_nodes1, dashed_nodes2 = [], [] # lists to track dashed edges that were removed
			for cdfg_edge in get_cdfg_edges(self.cdfg):	
				if cdfg_edge.attr["style"] == "dashed":
					self.cdfg.delete_edge(cdfg_edge[0], cdfg_edge[1])
					dashed_nodes1.append(cdfg_edge[0])
					dashed_nodes2.append(cdfg_edge[1])

			# Connect supernodes with existing nodes, following the rules from section 3
			nodes_in_bb = [n for n in list_of_nodes if n.attr['bbID'] == bb]
			for node in nodes_in_bb:
				list_of_predecessors = self.cdfg.predecessors(node)
				list_of_successors = self.cdfg.successors(node)

				if not list_of_predecessors or all(p.attr['bbID'] != bb for p in list_of_predecessors):
					# no predecessors from same BB, connect to source
					self.cdfg.add_edge(source_node_name, node)

				if not list_of_successors or all(s.attr['bbID'] != bb for s in list_of_successors):
					# no successors from same BB, connect to sink
					self.cdfg.add_edge(node, sink_node_name)

			# add dashed edges back again
			for src, dst in zip(dashed_nodes1, dashed_nodes2):
				self.cdfg.add_edge(src, dst, style = 'dashed')	

			# TODO?: connect sources with preceding sinks 	


	# function for setting the optimization function, according to the optimization option
	def set_opt_function(self):
		if self.sched_tech == 'asap':
			# TODO: write your code here
			list_of_nodes = set(get_cdfg_nodes(self.cdfg))

			# minimize start time of supersink of each BB
			for node in list_of_nodes: 
				if node.attr["type"] == 'supersink': # find supersink
					self.opt_fun.add_variable(f'sv{node}', 1)

		elif self.sched_tech == 'alap':
			# TODO: write your code here
			list_of_nodes = set(get_cdfg_nodes(self.cdfg))

			# maximize start time of every operation except for supersink
			for node in list_of_nodes:
				if node.attr["type"] != 'supersink': # find supersink
					self.opt_fun.add_variable(f'sv{node}', -1)
		
		elif self.sched_tech == 'pipelined':
			# TODO: write your code here
			# list_of_nodes = set(get_cdfg_nodes(self.cdfg))
			# list_of_bbs = set(get_cdfg_nodes(self.cfg))

			# for bb in list_of_bbs:
			# 	if bb == 'for.body': # find loop body BB
			# 		# minimize start time of loop body BB
			# 		for node in list_of_nodes: 
			# 			if node.attr["type"] == 'supersink': # find supersink
			# 				self.opt_fun.add_variable(f'sv{node}', 1)

			# same as ALAP
			list_of_nodes = set(get_cdfg_nodes(self.cdfg))

			# minimize start time of supersink of each BB
			for node in list_of_nodes: 
				if node.attr["type"] == 'supersink': # find supersink
					self.opt_fun.add_variable(f'sv{node}', 1)

		elif self.sched_tech == 'naive':
			# we minimize the last node in the topological order
			ordering = get_topological_order(self.cdfg)
			list_of_bbs = set(get_cdfg_nodes(self.cfg))
			for bb in list_of_bbs:
				# filter the topological ordering within a BB
				ordering_in_bb = [n for n in ordering if n.attr['bbID'] == bb]
				self.opt_fun.add_variable(f'sv{ordering_in_bb[-1]}', 1)

		else:
			self.log.error(f'Not implemented option! {self.sched_tech}')
			raise NotImplementedError

	# function to create the ILP of the scheduling
	def create_scheduling_ilp(self, sink_delays=None):
		if self.sched_tech == "asap":
			# TODO: write your code here
			self.set_data_dependency_constraints()

		elif self.sched_tech == "alap":
			# TODO: write your code here
			self.set_data_dependency_constraints()

		elif self.sched_tech == "pipelined":
			# TODO: write your code here
			self.set_data_dependency_constraints()

		# This is just a dummy scheduling for your reference, you can delete this part afterwards
		elif self.sched_tech == "naive":
			# 1. We first obtain a Topological sort.
			ordering = get_topological_order(self.cdfg)
			# 2. We assume that different BBs are completely disjoint.
			# Therefore we perform naive scheduling with respect to individual BBs
			list_of_bbs = set(get_cdfg_nodes(self.cfg))
			for bb in list_of_bbs:
				# filter the topological ordering within a BB
				ordering_in_bb = [n for n in ordering if n.attr['bbID'] == bb]
				# For every two adjacent nodes in the topological order of this BB
				for src, dst in zip(ordering_in_bb[0:-1], ordering_in_bb[1:]):
					src, dst = self.cdfg.get_node(src), self.cdfg.get_node(dst)
					# The later node cannot start before the earlier node finishes.
					# We create an ILP constraint every two adjacent nodes.
					self.constraints.add_constraint({f'sv{src}': -1, f'sv{dst}': 1}, "geq", get_node_latency(src.attr))

		self.set_opt_function()


#### DO NOT TOUCH FROM THIS LINE ####

	# function to solve the ilp and obtain scheduling
	def solve_scheduling_ilp(self, base_path, example_name):
		# log the result
		self.ilp.print_ilp("{0}/{1}/output.lp".format(base_path, example_name))
		res = self.ilp.solve_ilp()
		if res != 1:
			self.log.warn("The ILP problem cannot be solved")
			return res
		self.sched_sol = self.ilp.get_ilp_solution() # save solution in an attribute
		# iterate through the different variables to obtain results
		for var, value in self.ilp.get_ilp_solution().items():
			node_type = 'AUX'
			# check if the node represents a timing
			if re.search(r'^sv', var):
				node_name = re.sub(r'^sv', '', var)
				attributes = self.cdfg.get_node(node_name).attr
				node_type = attributes['type']
				attributes['label'] = attributes['label'] + '\n' + f'[{value}]'
				attributes['latency'] = value
			self.log.debug(f'{var} of type {node_type}:= {value}')
		self.cdfg.draw("test_dag_result.pdf", prog="dot")
		if 'max_latency' in self.ilp.get_ilp_solution():
			self.log.info(f'The maximum latency for this cdfg is {self.ilp.get_ilp_solution()["max_latency"]}')
		elif 'max_II' in self.ilp.get_ilp_solution():
			self.log.info(f'The maximum II for this cdfg is {self.ilp.get_ilp_solution()["max_II"]}')
			self.II = self.ilp.get_ilp_solution()["max_II"]
		elif 'II' in self.ilp.get_ilp_solution():
			self.log.info(f'The II for this cdfg is {self.ilp.get_ilp_solution()["II"]}')
			self.II = self.ilp.get_ilp_solution()["II"]
		return res

	# function to get the gantt chart of a scheduling 
	def print_scheduling_summary(self, file_path=None):
		assert self.sched_sol != None, "There should be a solution to an ILP before running this function"
		with open(file_path, 'w') as f:
			# sort the summary by BBs, print the starting time of each node
			for id_ in range(len(self.cfg)):
				# sort the summary by starting time of each node
				for node in sorted(get_cdfg_nodes(self.cdfg), key=lambda n : n.attr["latency"]):
					if int(node.attr['id']) == id_:
						f.write(f'sv({node}) @ bb({id_}) := {node.attr["latency"]}\n')
			if self.II != None:
				f.write(f'II := {self.II}')
			else:
				f.write(f'II := N/A')

	# function to get the gantt chart of a scheduling 
	def print_gantt_chart(self, chart_title="Untitled", file_path=None):
		assert self.sched_sol != None, "There should be a solution to an ILP before running this function"
		variables = {}
		start_time = {}
		duration = {}
		latest_tick = {} # variable to find last tick for xlables
		bars_colors = {}
		for node_name in get_cdfg_nodes(self.cdfg):
			if 'label' in self.cdfg.get_node(node_name).attr:
				attributes = self.cdfg.get_node(node_name).attr
				bb_id = attributes['id']
				if not(bb_id in variables):
					variables[bb_id] = []
					start_time[bb_id] = []
					duration[bb_id] = []
					bars_colors[bb_id] = []
					latest_tick[bb_id] = 0
				variables[bb_id].append(node_name)
				start_time[bb_id].append(float(attributes['latency'])) # start time of each operation
				node_latency = float(get_node_latency(attributes))
				if node_latency == 0.0:
					node_latency = 0.1
					bars_colors[bb_id].append("firebrick")
				else:
					bars_colors[bb_id].append("dodgerblue")
				duration[bb_id].append(node_latency) # duration of each operation
				tmp_tick = float(attributes['latency']) + float(get_node_latency(attributes))
				if tmp_tick > latest_tick[bb_id]:
					latest_tick[bb_id] = tmp_tick
		graphs_per_row = sqrt(len(variables))
		#fig, axs = plt.subplots(int(len(variables)))
		fig = plt.figure(figsize=(20 * 1.5, 11.25 * 1.5), layout='constrained')
		axs=[]
		subplot_format = (graphs_per_row * 110) + 1

		axs_id = 0
		for bb_id in variables:
			axs.append(fig.add_subplot(subplot_format))
			subplot_format += 1
			axs[axs_id].barh(y=variables[bb_id], left=start_time[bb_id], width=duration[bb_id], color=bars_colors[bb_id])
			axs[axs_id].grid()
			axs[axs_id].set_xticks([i for i in range(int(latest_tick[bb_id])+1)])
			axs[axs_id].title.set_text("BB {}".format(bb_id))
			#if self.II != None: # adding II information on the plot
			#	axs[axs_id].hlines(y=-1, xmin=0, xmax=self.II, color='r', linestyle = '-')
			#	axs[axs_id].text(self.II/2-0.35, -2, "II = {0}".format(int(self.II)), color='r')
			axs_id += 1
		#plt.title(chart_title)
		if file_path != None:
			plt.savefig(file_path)
		plt.show()
