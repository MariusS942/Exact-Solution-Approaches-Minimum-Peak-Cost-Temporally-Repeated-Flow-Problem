"""This file executes the Test for a given city and a line of the generated job .txt"""

import argparse
import osmnx
from integer_programs.execute_IP import execute_IPs


def process_job(city:str, line:str,method:str):
    """Gets city name and information about combination. Starts with getting the right graph and the execution of the IPs

    Args:
        city (str): name of city
        line (str): information about combination
        method (str): used method
    """

    information = line.split()
    origin_name, origin_coordinates = information[0], (float(information[1]), float(information[2]))
    arrival_name, arrival_coordinates = information[3], (float(information[4]), float(information[5]))
    bbox = {}
    bbox['north'] = information[6]
    bbox['south'] = information[7]
    bbox['west'] = information[8]
    bbox['east'] = information[9]

    G = osmnx.io.load_graphml(rf'networks/{city}.graphhml')
    execute_IPs(city, origin_name, origin_coordinates, arrival_name, arrival_coordinates, G, 1000, 1, method)

"""if this file is executed by slurm script read city, method and line"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--city', required= True)
    parser.add_argument('--task_id', type=int, required=True)
    parser.add_argument('--method', required= True)
    arguments = parser.parse_args()

    with open(f'city_params/{arguments.city}.txt') as file:
        lines = file.read().splitlines()
    
    line = lines[arguments.task_id -1]
    process_job(arguments.city, line,arguments.method)

