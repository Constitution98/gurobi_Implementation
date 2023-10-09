def get_parameters(requests): 
    # Parameters
    depots = [0]
    customers = [request['id'] for request in requests]
    nodes = depots + customers
    vehicles = ['van', 'ecar', 'ebike']

    # Vehicle capacity
    Lv = {'van': 200, 'ecar': 100, 'ebike': 50}

    # Time dependent variables
    time_frames = list(range(1, 13))  # 12 time frames

    # Maximum fuel tank capacity of each vehicle
    Qv = {'van': 160, 'ecar': 160, 'ebike': 100}

    # Maximum number of vehicles of each type available
    mv = {'van': 1, 'ecar': 1, 'ebike': 1}

    # Speed of each vehicle in each time frame
    sv = {
        'van': {1: 20, 2: 15, 3: 18, 4: 21, 5: 22, 6: 19, 7: 20, 8: 21, 9: 22, 10: 23, 11: 24, 12: 25},
        'ecar': {1: 25, 2: 20, 3: 23, 4: 24, 5: 25, 6: 24, 7: 23, 8: 24, 9: 25, 10: 26, 11: 27, 12: 28},
        'ebike': {1: 15, 2: 12, 3: 14, 4: 15, 5: 16, 6: 15, 7: 16, 8: 15, 9: 16, 10: 17, 11: 18, 12: 17}
    }

    # CO2 emission factor for each vehicle (unit: ton of CO2 per unit of fuel)
    ev = {'van': 4, 'ecar': 2, 'ebike': 2}

    # Engine parameters based on Ehmke (2018) and Franceschetti (2013) CEM
    params = {
        'Ne': 33,  # Engine speed
        'V': 5,  # Engine displacement
        'k': 0.2,  # Engine friction factor
        'mu': {
            'ecar': 1850,  # Curb weight for standard vehicle (ecar)
            'van': 4700,  # Curb weight for heavy vehicle (van)
            'ebike': 500  # Curb weight for light vehicle (ebike)
        },
        'alpha': 0.0981,  # Parameter related to the vehicle and its engine
        'beta': 1.6487,  # Parameter related to the vehicle and its engine
        'gamma': 0.0028,  # Parameter related to the vehicle and its engine
        'lambda': 1/32428  # Parameter related to the vehicle and its engine
    }
    return depots, customers, nodes, vehicles, Lv, time_frames, Qv, mv, sv, ev, params