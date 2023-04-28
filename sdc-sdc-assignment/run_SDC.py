#!/bin/python3
import argparse
from src.main_flow.parser import Parser
from src.main_flow.scheduler import Scheduler
from src.main_flow.resource import Resources
import logging

from src.utilities.ilp_manager import *
from src.utilities.cdfg_manager import *

# create log interface
log = logging.getLogger('sdc')
log.setLevel(logging.INFO)
console_handler = logging.StreamHandler() # create console handler and set level to debug
formatter = logging.Formatter('%(levelname)s - %(message)s') # create formatter
console_handler.setFormatter(formatter) # add formatter to console
log.addHandler(console_handler) # add console_handler to log


def main(args):

	input_list = args.input_list
	base_path = args.examples_folder
	debug_mode = args.debug

	log.info("Arguments selected:\n\tINPUT LIST = {0}\n\tEXAMPLE FOLDER PATH = {1}\n\tDEBUG = {2}".format(base_path, input_list, debug_mode))

	# if debug_mode is selected logger is set to debug
	if debug_mode:
		log.setLevel(logging.DEBUG)

	#reading the list of examples to execute
	examples_list_file = open(input_list, "r")
	examples_list = examples_list_file.read().split("\n")
	examples_list_file.close()

	for example_name in examples_list:
		if example_name == "":
			continue

		log.info("*** BENCHMARK {0} ***".format(example_name))
		# the path of the ssa file should be base_path/example_name/reports/example_name.cpp_mem2reg_constprop_simplifycfg_die.ll
		path_ssa_example = "{0}/{1}/reports/{1}.cpp_mem2reg_constprop_simplifycfg_die.ll".format(base_path, example_name)

		log.info("Parsing file {0}".format(path_ssa_example))
		ssa_parser = Parser(path_ssa_example, example_name, log)
		if not(ssa_parser.is_valid()):
			log.error("Parser has encountered a problem. Please verify path correctness ({0})".format(path_ssa_example))
			continue
		ssa_parser.draw_cdfg("{0}/{1}/parser_output.pdf".format(base_path, example_name))

		###################### Naive #####################
		# scheduling_type = "naive"
		# scheduler = Scheduler(ssa_parser, scheduling_type, log = log)
		# scheduler.create_scheduling_ilp()
		# status = scheduler.solve_scheduling_ilp(base_path, example_name)
		# chart_title = "{0} - {1}".format("Naive", example_name)
		# scheduler.print_gantt_chart(chart_title, "{0}/{1}/{2}_{1}.pdf".format(base_path, example_name, scheduling_type))
		# scheduler.print_scheduling_summary("{0}/{1}/{2}_{1}.txt".format(base_path, example_name, scheduling_type))

		###################### ASAP ######################
		# TODO: write your code here

		# scheduling_type = "asap"
		# scheduler = Scheduler(ssa_parser, scheduling_type, log = log)
		# scheduler.create_scheduling_ilp()
		# status = scheduler.solve_scheduling_ilp(base_path, example_name)
		# chart_title = "{0} - {1}".format("ASAP", example_name)
		# scheduler.print_gantt_chart(chart_title, "{0}/{1}/{2}_{1}.pdf".format(base_path, example_name, scheduling_type))
		# scheduler.print_scheduling_summary("{0}/{1}/{2}_{1}.txt".format(base_path, example_name, scheduling_type))

		###################### ALAP ######################
		# TODO: write your code here

		# # run ASAP to obtain latency bound
		# scheduling_type = "asap"
		# scheduler_asap = Scheduler(ssa_parser, scheduling_type, log = log)
		# scheduler_asap.create_scheduling_ilp()
		# status = scheduler_asap.solve_scheduling_ilp(base_path, example_name)

		# # add latency bound for each supersink 
		# scheduling_type = "alap"
		# scheduler_alap = Scheduler(ssa_parser, scheduling_type, log = log)
		# list_of_nodes = set(get_cdfg_nodes(scheduler_asap.cdfg))
		# for node in list_of_nodes: # find supersink
		# 	if node.attr["type"] == 'supersink':
		# 		scheduler_alap.constraints.add_constraint({f'sv{node}': 1}, "eq", float(node.attr["latency"])) # add bound
		
		# # run actual ALAP
		# scheduler_alap.create_scheduling_ilp()
		# status = scheduler_alap.solve_scheduling_ilp(base_path, example_name)
		# chart_title = "{0} - {1}".format("ALAP", example_name)
		# scheduler_alap.print_gantt_chart(chart_title, "{0}/{1}/{2}_{1}.pdf".format(base_path, example_name, scheduling_type))
		# scheduler_alap.print_scheduling_summary("{0}/{1}/{2}_{1}.txt".format(base_path, example_name, scheduling_type))

		###################### ASAP with RESOURCE CONSTRAINTS ######################
		# TODO: write your code here

		# # run every combination
		# for nr_mul in range(1,4):
		# 	for nr_add in range(1,4):
		# 		for nr_zext in range(1,4):
					
		# 			ssa_parser = Parser(path_ssa_example, example_name, log)

		# 			print(nr_mul, nr_add, nr_zext)

		# 			scheduling_type = "asap"
		# 			resource_dic = {"mul": nr_mul, "add": nr_add, "zext": nr_zext} # define resource constraints here

		# 			scheduler = Scheduler(ssa_parser, scheduling_type, log = log)
		# 			resources = Resources(ssa_parser, resource_dic)

		# 			scheduler.create_scheduling_ilp()
		# 			ilp, constraints, opt_function = scheduler.get_ilp_tuple()
		# 			resources.add_resource_constraints(ilp, constraints, opt_function)

		# 			status = scheduler.solve_scheduling_ilp(base_path, example_name)
		# 			chart_title = "{0} - {1}".format("asap-rc", example_name)
		# 			scheduler.print_gantt_chart(chart_title, f"{base_path}/{example_name}/{scheduling_type}_{example_name}_resource_add_{nr_add}_mul_{nr_mul}_zext_{nr_zext}.txt.pdf".format(base_path, example_name, scheduling_type))
		# 			scheduler.print_scheduling_summary(f"{base_path}/{example_name}/{scheduling_type}_{example_name}_resource_add_{nr_add}_mul_{nr_mul}_zext_{nr_zext}.txt".format(base_path, example_name, scheduling_type))

		###################### ALAP with RESOURCE CONSTRAINTS ######################
		# TODO: write your code here
		pass

		###################### ASAP pipelined ######################
		# TODO: write your code here
		
		# scheduling_type = "pipelined"
		# scheduler = Scheduler(ssa_parser, scheduling_type, log = log)
		# scheduler.create_scheduling_ilp()

		# II = 1
		# scheduler.set_II_constraints(II)
		# while(scheduler.solve_scheduling_ilp(base_path, example_name) == -1): # check whether schedule is feasible
		# 	#print(f'no feasibible schedule found with II = {II}')
		# 	II += 1
		# 	scheduler.set_II_constraints(II) # replace old constraints with new ones

		# #print(f'feasibible schedule found with II = {II}! \n')

		# chart_title = "{0} - {1}".format("pipelined", example_name)
		# scheduler.print_gantt_chart(chart_title, "{0}/{1}/{2}_{1}.pdf".format(base_path, example_name, scheduling_type))
		# scheduler.print_scheduling_summary("{0}/{1}/{2}_{1}.txt".format(base_path, example_name, scheduling_type))

		###################### ASAP pipelined resource constrained ######################
		# TODO: write your code here

		scheduling_type = "pipelined"
		nr_mul, nr_add, nr_zext = 1, 1, 1 # define resource constraints here
		resource_dic = {"mul": nr_mul, "add": nr_add, "zext": nr_zext} 

		scheduler = Scheduler(ssa_parser, scheduling_type, log = log)
		resources = Resources(ssa_parser, resource_dic)

		scheduler.create_scheduling_ilp()
		II = 1
		scheduler.set_II_constraints(II)
		while(scheduler.solve_scheduling_ilp(base_path, example_name) == -1): # check whether schedule is feasible
			II += 1
			scheduler.set_II_constraints(II) # replace old constraints with new ones

		ilp, constraints, opt_function = scheduler.get_ilp_tuple() # initial ilp scheduling

		while(not resources.add_resource_constraints_pipelined(ilp, constraints, opt_function, budget = 20)): # loop until heuristics finds a feasible solution
			II += 1
			print('II = ', II)
			scheduler.set_II_constraints(II) # replace old constraints with new ones
			status = scheduler.solve_scheduling_ilp(base_path, example_name)
			ilp, constraints, opt_function = scheduler.get_ilp_tuple()
		
		scheduler.set_II_constraints(II) 
		status = scheduler.solve_scheduling_ilp(base_path, example_name) # final schedule

		print('done! II =', II)

		chart_title = "{0} - {1}".format("asap-pipelined-rc", example_name)
		scheduler.print_gantt_chart(chart_title, f"{base_path}/{example_name}/{scheduling_type}_{example_name}_resource_add_{nr_add}_mul_{nr_mul}_zext_{nr_zext}.txt.pdf".format(base_path, example_name, scheduling_type))
		scheduler.print_scheduling_summary(f"{base_path}/{example_name}/{scheduling_type}_{example_name}_resource_add_{nr_add}_mul_{nr_mul}_zext_{nr_zext}.txt".format(base_path, example_name, scheduling_type))



if __name__ == '__main__':
	arg_parser = argparse.ArgumentParser(description="Welcome to the SDC project for the Summer Semester 2023!")
	arg_parser.add_argument('--input_list', type=str, help='Input filelist containing examples to run', default="filelist.lst")
	arg_parser.add_argument('--examples_folder', type=str, help='Path of the examples folder', default="examples")
	arg_parser.add_argument('--debug', action='store_true' , help='Set debug mode', default=False)


	args = arg_parser.parse_args()

	main(args)
