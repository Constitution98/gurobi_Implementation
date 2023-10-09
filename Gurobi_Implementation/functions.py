from math import sqrt
from gurobipy import Model, GRB, quicksum

def euclidean_distance(point1, point2):
    return sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def calculate_distance_matrix(coordinates, nodes):
    return [[euclidean_distance(coordinates[node1], coordinates[node2]) for node2 in nodes] for node1 in nodes]

def calculate_fuel_consumption(distance, speed, load, vehicle_type, params):
    # Unpack parameters
    Ne = params['Ne']
    V = params['V']
    k = params['k']
    mu = params['mu'][vehicle_type]
    alpha = params['alpha']
    beta = params['beta']
    gamma = params['gamma']
    lambda_param = params['lambda']

    # Calculate fuel consumption
    fuel_consumption = (lambda_param * k * Ne * V * distance / speed
                        + gamma * beta * distance / speed**2
                        + gamma * alpha * (mu + load) * distance)
    return fuel_consumption





#old debug statements

"""# Check if constraints include combinations of xij with node 0

# 1. Check x[i,j,v,tf] combinations
for v in vehicles:
    for tf in time_frames:
        from_depot = any(x[0, j, v, tf].X > 0.5 for j in nodes if j != 0) # leaving the depot
        to_depot = any(x[i, 0, v, tf].X > 0.5 for i in nodes if i != 0) # returning to the depot
        
        if not from_depot:
            print(f"Vehicle {v} in time frame {tf} has no arc leaving the depot.")
        if not to_depot:
            print(f"Vehicle {v} in time frame {tf} has no arc returning to the depot.")

# 2. Check tij[i,j,v,tf] combinations
for v in vehicles:
    for tf in time_frames:
        from_depot_tij = any((0, j, v, tf) in tij for j in nodes if j != 0) # leaving the depot
        to_depot_tij = any((i, 0, v, tf) in tij for i in nodes if i != 0) # returning to the depot
        
        if not from_depot_tij:
            print(f"Vehicle {v} in time frame {tf} has no travel time leaving the depot in tij.")
        if not to_depot_tij:
            print(f"Vehicle {v} in time frame {tf} has no travel time returning to the depot in tij.")
"""


"""# check distance matrix
print("Depot (Node 0) coordinates:", coordinates[0])
for request in requests[:5]: #considering first 5 requests
    node_id = request['node']
    print(f"Customer {node_id} coordinates:", coordinates[node_id])
for i in range(6):
    for j in range(6):
        print(f"Distance between Node {i} and Node {j}:", distances[i][j])
    print("------")


# check dij dictionary
for i in range(6):
    for j in range(6):
        print(f"Distance between Node {i} and Node {j} from dij:", dij[(i, j)])
    print("------")"""

# Old constraints

"""# force atleast one start at the depot
for v in vehicles:
    m.addConstr(quicksum(x[0, j, v, tf] for j in nodes for tf in time_frames if j != 0) >= 1, f"force_start_{v}")"""
    
    
"""# Dissalow (0,0) arcs // for all i equal toj
for v in vehicles:
    for tf in time_frames:
        m.addConstr(x[0, 0, v, tf] == 0, f"no_self_loop_{v}_tf{tf}")"""
        
        
"""# start and end at the depot
for v in vehicles:
    for tf in time_frames:
        m.addConstr(quicksum(x[0, j, v, tf] for j in nodes) == quicksum(x[i, 0, v, tf] for i in nodes), f"start_end_depot_{v}_tf{tf}")"""
        
"""# Maximum tour duration can't extend beyond the day
for v in vehicles:
    for tf in time_frames:
        m.addConstr(quicksum(tij[i, j, v, k] * x[i, j, v, k] for i, j in dij.keys() for k in range(tf, tf + (13 - tf)) if (i, j, v, k) in x.keys()) <= (13 - tf), f"tour_duration_{v}_tf{tf}")

"""
"""
# Refueling and vehicle limit constraints for each vehicle
for v in vehicles:
    # Handle the first time frame separately
    m.addConstr(y[0, v, 1] == Qv[v], f"refuel_depot_{v}_tf1") # at the beginning of tf1 vehicles are fully refuelld at the depot
    m.addConstr(quicksum(x[0, j, v, 1] for j in nodes if (0, j, v, 1) in tij.keys()) <= mv[v], # ensure that no more vehilces leave the depot than are available
                f"vehicle_limit_{v}_tf1")

    # Handle the rest of the time frames
    for tf in range(2, len(time_frames)):  # start from the second time frame
        # Each vehicle is refueled at the depot after spending one time frame at the depot
        m.addConstr(y[0, v, tf] == fuel_remaining[0, v, tf-1] + 
                    Qv[v] * quicksum(x[0, j, v, tf-1] for j in nodes if (0, j, v, tf-1) in tij.keys()),
                    f"refuel_depot_{v}_tf{tf}")
        # Vehicle has to stay at the depot for one time frame if its fuel level is less than 10%
        m.addConstr(fuel_remaining[0, v, tf] <= 0.1 + 
                    quicksum(x[0, j, v, tf-1] for j in nodes if (0, j, v, tf-1) in tij.keys()),
                    f"depot_stay_{v}_tf{tf}")
        # Limit on number of vehicles so no more vehilces can leave the depot than are available
        m.addConstr(quicksum(x[0, j, v, tf] for j in nodes if (0, j, v, tf) in tij.keys()) <= mv[v], 
                    f"vehicle_limit_{v}_tf{tf}")"""
                    
                    
"""# Constraint to ensure that a vehicles cannot jump from one cusomter to another between time frames without having arcs between them
# For each vehicle, each pair of customers, and each time frame (starting from the second time frame)
for v in vehicles:
    for i in customers:
        for j in customers:
            if i != j:
                for tf in time_frames[1:]:
                    m.addConstr(x[i, j, v, tf] <= quicksum(x[k, i, v, tf - 1] for k in nodes), f"route_progression_{i}_to_{j}_{v}_tf{tf}")


# Constraint to ensure that if a vehicle starts from a node other than the depot in a given time frame it must end at that node in the previous time frame
for v in vehicles:
    for tf in time_frames[1:]:  # Start from the second time frame
        for j in customers:
            m.addConstr(x[0, j, v, tf] <= quicksum(x[i, j, v, tf-1] for i in nodes), f"consistent_start_{v}_tf{tf}_node{j}")"""
            
            
            
"""# Flow Conservation without time frame iteration
for v in vehicles:  # iterates over vehicles and customers
    for j in customers:
        m.addConstr(
            quicksum(x[i, j, v, tf] for i in nodes if i != j for tf in time_frames) == 
            quicksum(x[j, k, v, tf] for k in nodes if k != j for tf in time_frames), 
            f"flow_conservation_{j}_{v}"
        )  # sum of xij across all time frames must be equal to sum of xjk across all time frames"""
        

"""# Constraint to ensure that if a vehilce returns to the depot in any given time frame it it must start from the depot in all subsequent time frames
for v in vehicles:
    for day in days:
        for tf in range((day-1)*12+1, day*12): # Loop from start of the day to end of the day
            m.addConstr(quicksum(x[i, 0, v ,tf] for i in nodes) <= quicksum(x[0, j, v ,tf] for j in nodes), f"no_teleport_{v}_day{day}_tf{tf}")"""
            
"""# Each customer can only be servded once
for j in customers: #iterates over customers
    m.addConstr(quicksum(x[i, j, v, tf] for i in nodes for v in vehicles for tf in time_frames if i != j) <= 1, f"visit_once_{j}")"""
    
"""# Sequential Arc Continuity Constraint
for j in nodes:
    for v in vehicles:
        for tf in time_frames:
            m.addConstr(quicksum(x[i, j, v, tf] for i in nodes if (i, j) in x.keys()) * quicksum(x[j, k, v, tf] for k in nodes if (j, k) in x.keys()) 
                        == quicksum(x[i, j, v, tf] for i in nodes if (i, j) in x.keys()), f"arc_continuity_{j}_{v}_tf{tf}")"""