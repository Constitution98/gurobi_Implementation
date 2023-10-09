import xml.etree.ElementTree as ET
from gurobipy import Model, GRB, quicksum
import random
import matplotlib.pyplot as plt
import pandas as pd
from math import sqrt
from xml.etree import ElementTree as ET



def read_xml(file_path, customer_choice):
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extracts the different nodes i.e. customers and their coordinates
    nodes = []
    coordinates = {}
    for node in root.findall('./network/nodes/node'):
        node_id = int(node.get('id'))
        
        # Limit the number of nodes based on user's choice to 5 customers
        if customer_choice == 2 and len(nodes) >= 6:  # 6 including the depot
            break
        
        nodes.append(node_id)
        cx = float(node.find('cx').text)
        cy = float(node.find('cy').text)
        coordinates[node_id] = (cx, cy)

    # Get the vehicle profile
    vehicle_profile_element = root.find('fleet/vehicle_profile')
    vehicle_profile = {
        'departure_node': int(vehicle_profile_element.find('departure_node').text),
        'arrival_node': int(vehicle_profile_element.find('arrival_node').text),
        'capacity': float(vehicle_profile_element.find('capacity').text),
        'max_travel_time': float(vehicle_profile_element.find('max_travel_time').text),
    }

    #Get requests and their demands
    requests = []
    demands = {}
    for request in root.findall('./requests/request'):
        request_id = int(request.get('id'))
        # Limit the number of requests based on user's choice
        if customer_choice == 2 and request_id > 5:
            break
        request_dict = {}
        request_dict['id'] = request_id
        request_dict['node'] = int(request.get('node'))
        request_dict['start'] = float(request.find('tw/start').text)
        request_dict['end'] = float(request.find('tw/end').text)
        request_dict['service_time'] = float(request.find('service_time').text)
        requests.append(request_dict)
        quantity = float(request.find('quantity').text)
        demands[request_dict['id']] = quantity
    return nodes, vehicle_profile, requests, coordinates, demands

