"""This file executes the Test for a given series-parallel instance."""

import argparse
from linear_programs.execute_sp import execute_LPs
from auxiliary_programs.parse_SP import rebuild_graph


def process_job(file:str, method:str):
    """Gets name of SP file and name of method which should. Starts with getting the right graph and the execution of the LPs

    Args:
        file (str): name of file
        method (str): used method
    """

    G = rebuild_graph(file)

    execute_LPs(file, G, 1000, 1, method)

"""if this file is executed by slurm script read city, method and line"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--task_id', type=int, required=True)
    parser.add_argument('--method', required= True)
    arguments = parser.parse_args()

    
    process_job(fr'graph_{arguments.task_id-1}',arguments.method)

