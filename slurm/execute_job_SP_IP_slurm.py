"""This file executes the Test for a given series-parallel instance."""

import argparse
from integer_programs.execute_SP_IP import execute_IPs
from auxiliary_programs.parse_SP import rebuild_graph


def process_job(file:str, method:str):
    """Gets name of SP file and name of method which should. Starts with getting the right graph and the execution of the IPs

    Args:
        file (str): name of file
        method (str): used method
    """

    G = rebuild_graph(file)

    execute_IPs(file, G, 1000, 1, method)

"""if this file is executed by slurm script read instance line and method"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--task_id', type=int, required=True)
    parser.add_argument('--method', required= True)
    arguments = parser.parse_args()

    
    process_job(fr'graph_{arguments.task_id-1}',arguments.method)

