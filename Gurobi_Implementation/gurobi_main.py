import xml.etree.ElementTree as ET
from gurobipy import Model, GRB, quicksum
import matplotlib.pyplot as plt
import pandas as pd
from xml.etree import ElementTree as ET
from data_loader import read_xml #reads in data from xml file
from plotting import plot_tours # functions for plotting
from plotting import plot_routes 
from parameters import get_parameters # get parameters
from functions import calculate_fuel_consumption, calculate_distance_matrix # get utility functions

# User Inputs

print("Please choose the number of customers to consider:")
print("1 - All customers")
print("2 - First 5 customers")
customer_choice = int(input("Enter your choice (1-2): "))
model_type = input("Enter the model type (hom/het): ")

# Hardcoded path to the XML file
file_path = '/Users/constantinschaumann/Library/Mobile Documents/com~apple~CloudDocs/Masterarbeit/Data/solomon-1987-c2/C201_025.xml'

# Reads data from XML file
nodes, vehicle_profile, requests, coordinates, demands = read_xml(file_path, customer_choice)

# Get parameters using the requests list
depots, customers, nodes, vehicles, Lv, time_frames, Qv, mv, sv, ev, params = get_parameters(requests)

# Calculate the distances between each pair of nodes using the new function
distances = calculate_distance_matrix(coordinates, nodes)

# Convert distances matrix to dictionary
dij = {(i, j): distances[i][j] for i in range(len(distances)) for j in range(len(distances[i]))}

# Initialize a dictionary to store the emissions for each vehicle and time frame
emissions = {v: {tf: 0 for tf in time_frames} for v in vehicles}

# Maintains a dictionary of total fuel consumption for each vehicle and time frame
fuel_consumption = {v: {tf: 0 for tf in time_frames} for v in vehicles}

# If the user chooses a homogeneous model, assign the same parameters to all vehicles
if model_type.lower() == "hom":
    # Ask the user which vehicle's parameters should be used for all vehicles
    homogeneous_vehicle = input("Enter the vehicle type to use for all vehicles (van/ecar/ebike): ")

    # Use the chosen vehicle's parameters for all vehicles
    Lv = {homogeneous_vehicle: Lv[homogeneous_vehicle]}  # Vehicle capacity
    Qv = {homogeneous_vehicle: Qv[homogeneous_vehicle]}  # Maximum fuel tank capacity of each vehicle
    mv = {homogeneous_vehicle: mv[homogeneous_vehicle]}  # Maximum number of vehicles of each type available
    sv = {homogeneous_vehicle: sv[homogeneous_vehicle]}  # Speed of each vehicle in each time frame
    ev = {homogeneous_vehicle: ev[homogeneous_vehicle]}  # CO2 emission factor for each vehicle (unit: ton of CO2 per unit of fuel)
    params['mu'] = {homogeneous_vehicle: params['mu'][homogeneous_vehicle]}  # Curb weight for all vehicles

    # Update vehicles list
    vehicles = [homogeneous_vehicle]



# Debugging print statements

# Model setup   

# Create a new Gurobi model
m = Model("TimeDependentGreenVRP")

# Define decision variable x_{ijvtf}
x = m.addVars(nodes, nodes, vehicles, time_frames, vtype=GRB.BINARY, name="x")

# Set the objective function
m.setObjective(quicksum(dij[(i, j)] * x[i, j, v, tf] for i in nodes for j in nodes for v in vehicles for tf in time_frames), GRB.MINIMIZE)

# Constraints 

# Each customer is served by at least one vehicle within the 12 time frames
for j in nodes: #iterates over customers
    m.addConstr(quicksum(x[i, j, v, tf] for i in nodes for v in vehicles for tf in time_frames if i != j and ( 
        i, j, v, tf) in x.keys()) == 1, f"customer_served_{j}")

# Flow conservation
# Flow conservation without iterating over time frames
for j in customers:
    for v in vehicles:
        m.addConstr(
            quicksum(x[i, j, v, tf] for i in nodes for tf in time_frames if i != j) == 
            quicksum(x[j, k, v, tf] for k in nodes for tf in time_frames if k != j), 
            f"FlowConservation_{j}_{v}")


# Prevent back and forth travel between nodes in any time frame
for i in nodes:
    for j in nodes:
        if i != j:  # Ensure i and j are different
            for v in vehicles:
                m.addConstr(
                    quicksum(x[i, j, v, tf] for tf in time_frames) + 
                    quicksum(x[j, i, v, tf] for tf in time_frames) <= 1, 
                    f"PreventBackForth_{i}_{j}_{v}")



#Debug Prints





#Check if x contains all combinations of nodes, vehicles and time frames
with open("x_keys_output.txt", "w") as file:
    for key in x.keys():
        file.write(str(key) + "\n") # --> seems to be correct

# Check if the number of keys for x is equal to the product of nodes, vehicles and time frames
expected_length = len(nodes) * len(nodes) * len(vehicles) * len(time_frames)
actual_length = len(x.keys())

print(f"Expected number of keys: {expected_length}")
print(f"Actual number of keys: {actual_length}") # For 5 customers: Expected number of keys: 1296; Actual number of keys: 1296 --> seems to be correct





# Writes the model into lp format
m.write("my_model4.lp")


# Solves the model
m.optimize()

#Debug prints
# Print only the arcs that are used
for key, var in x.items():
    if var.X > 0.5:  
        print(f"Vehicle travels arc {key} with value: {var.X}")






#Extract and structure the solution data from the model
def extract_solution_data(): # Initializes dictionaries to store different aspects of the solution
    solution = {} # stores edges travelled by vehicles
    solution_time_frames = {} # stores time frames in which vehicles are active
    fuel_remaining = {}
    travel_time = {}
    starts_from_depot = {} # to check if a vehicle starts its tour from the depot
    ends_at_depot = {} # to check if a vehicle ends its tour at the depot

    # Extracting data for each vehicle
    for v in vehicles: # iterate over vehicles
        solution[v] = [(i, j, tf) for i, j in dij.keys()
                       for tf in time_frames if x[i, j, v, tf].x > 0.5] # if xij is greater than 0.5 it means it is 1 and the edge ij is traversed
        solution[v].sort()
        solution_time_frames[v] = list(set([tf for i, j, tf in solution[v]])) 
        fuel_remaining[v] = {tf: Qv[v] for tf in solution_time_frames[v]}
        
        # Check if the vehicle starts or ends its journey at the depot
        for tf in solution_time_frames[v]:
            starts_from_depot[v, tf] = any(i == 0 for i, j, t in solution[v] if t == tf)
            ends_at_depot[v, tf] = any(j == 0 for i, j, t in solution[v] if t == tf)
    
    return solution, solution_time_frames, fuel_remaining, travel_time, starts_from_depot, ends_at_depot

#Prints the tour details for a specific vehicle
def print_tour_details_for_vehicle(v, solution, solution_time_frames, fuel_remaining, starts_from_depot, ends_at_depot):
    
    total_distance_for_vehicle = 0 # initialized to zero
    print(f"\nOrder for vehicle {v}:\n")
    for tf in sorted(solution_time_frames[v]): #iterates through time frames and sorts them in ascending order
        order = [] # retrieves the order of locations that vehicle v visits in time frame tf
        for i, j, t in solution[v]:
            if t == tf:
                if not order: # this is so that the depot (node 0) can be dispaleyed twice
                    order.append(i)
                order.append(j)
        
        
        # Conditionally add "Depot" based on the extracted information
        route_str = ' --> '.join(str(i) for i in order)    
        print(f"Time Frame {tf}: {route_str}")

        distance_for_tf = 0 #initialized to zero
        for i, j, t in solution[v]:
            if t == tf:
                print(f"Traversed arc: ({i}, {j}) with distance: {dij[i, j]} km")
                """fuel_used = calculate_fuel_consumption(dij[i, j], sv[v][tf], z[i, v, tf].x, v, params)"""
                """fuel_remaining[v][tf] -= fuel_used"""
                total_distance_for_vehicle += dij[i, j]
                distance_for_tf += dij[i, j]

        emissions = (Qv[v] - fuel_remaining[v][tf]) * ev[v]
        print(f"Emissions for time frame {tf}: {round(emissions, 2)} kg of CO2")
        print(f"Remaining fuel at end of tour that began in time frame {tf}: {round(100 * fuel_remaining[v][tf] / Qv[v], 2)}%")
        """print(f"Total travel time of tour started in time frame {tf}: {round(travel_time[v][tf], 2)} hours")"""
        print(f"Total distance travelled by vehicle {v} in time frame {tf}: {distance_for_tf} km")
        print(f"\nCumulative distance travelled by vehicle {v} up to and including time frame {tf}: {total_distance_for_vehicle} km\n")

    return total_distance_for_vehicle

if m.status == GRB.OPTIMAL:
    # Extracting the solution data
    solution, solution_time_frames, fuel_remaining, travel_time, starts_from_depot, ends_at_depot = extract_solution_data()
    
    total_distance = {}
    for v in vehicles:
        total_distance[v] = print_tour_details_for_vehicle(v, solution, solution_time_frames, fuel_remaining, starts_from_depot, ends_at_depot)

    # Print final total distances for all vehicles
    print("\nFinal total distances for all vehicles:", total_distance)

    # Calculate and print the total distance travelled by all vehicles combined
    total_distance_all = sum(total_distance.values())
    print(f"\nTotal distance travelled by all vehicles: {total_distance_all} km")
    
    # Call the function to generate the plots
    # plot_tours(solution, solution_time_frames, sv, travel_time)
    
    plot_routes(coordinates, solution)
    
    # Print only the arcs that are used
    for key, var in x.items():
        if var.X > 0.5:  
            print(f"Vehicle travels arc {key} with value: {var.X}")


elif m.status == GRB.INFEASIBLE:
    print("The model is infeasible")
    m.computeIIS()
    for c in m.getConstrs():
        if c.IISConstr:
            print('%s' % c.constrName)
else:
    print(f'Optimization ended with status {m.status}')
