import pandas as pd 
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch

def plot_routes(coordinates, solution):
    # Ask the user if they want to visualize the routes
    user_input = input("Do you want to visualize the nodes and routes? (yes/no): ").strip().lower()
    if user_input == 'yes':
        plt.figure(figsize=(12, 8))
        
        # Generates a list of distinct colors based on the number of vehicles
        colors = plt.cm.jet(np.linspace(0, 1, len(solution)))
        
        first_customer = True
        # Plot all nodes and annotate them with their IDs
        for node, (x, y) in coordinates.items():
            if node == 0:  # depot
                plt.scatter(x, y, c='red', s=100, label='Depot', zorder=5)
                plt.text(x, y, str(node), ha='right', va='bottom', fontsize=10, zorder=5)
            else:
                if first_customer:  # Add label only for the first customer
                    plt.scatter(x, y, c='blue', s=50, label='Customer', zorder=5)
                    first_customer = False
                else:
                    plt.scatter(x, y, c='blue', s=50, zorder=5)
                plt.text(x, y, str(node), ha='right', va='bottom', fontsize=10, zorder=5)
        
        # Plot arcs for each vehicle with unique colors
        for idx, (vehicle, arcs) in enumerate(solution.items()):
            first_arc = True
            for (i, j, tf) in arcs:
                x1, y1 = coordinates[i]
                x2, y2 = coordinates[j]
                
                # Add an arrow to indicate direction
                arrow = FancyArrowPatch((x1, y1), (x2, y2), connectionstyle="arc3,rad=.2", 
                                        arrowstyle='->,head_width=0.5,head_length=0.5', 
                                        color=colors[idx], mutation_scale=15)
                plt.gca().add_patch(arrow)
                
                # Label only the first arrow for each vehicle for legend
                if first_arc:
                    arrow.set_label(f'Vehicle {vehicle}')
                    first_arc = False
        
        # Set title, legend, and show plot
        plt.title("Vehicle Routes")
        plt.legend()
        plt.show()
    else:
        print("Visualization skipped.")



#Extract tour information
def extract_tours(solution, solution_time_frames, sv, travel_time):
    tours = []
    for v in solution:
        for tf in solution_time_frames[v]:
            tour = {}
            tour['vehicle'] = v
            tour['time_frame'] = tf
            tour['speed'] = sv[v][tf]
            tour['travel_time'] = travel_time[v][tf]
            tours.append(tour)
    return tours

# Plot travel time and speed 
def plot_tours(solution, solution_time_frames, sv, travel_time):
    tours = extract_tours(solution, solution_time_frames, sv, travel_time)

    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(tours)
    
    # Ask the user if they want the plots
    plot_choice = input("Do you want to generate the plots (yes/no)? ").lower()
    
    if plot_choice == "yes":

        # Determine the full range of time frames
        all_time_frames = set()
        for v in solution_time_frames:
            all_time_frames.update(solution_time_frames[v])
        all_time_frames = sorted(list(all_time_frames))

        # Convert the list of dictionaries to a pandas DataFrame
        df = pd.DataFrame(tours)
        
        # Gather all unique time frames from the solution
        all_time_frames = set()
        for v in solution_time_frames:
            all_time_frames.update(solution_time_frames[v])
        all_time_frames = sorted(list(all_time_frames))
        
        for v in df['vehicle'].unique():
            # Create a dataframe for the vehicle and merge it with all the time frames, filling NA values with 0
            df_vehicle = df[df['vehicle'] == v]
            df_vehicle_all = pd.DataFrame({'time_frame': all_time_frames})
            df_vehicle_all = df_vehicle_all.merge(df_vehicle, on='time_frame', how='left').fillna(0)

            # Plot travel speed
            plt.figure(figsize=(10, 6))
            plt.bar(df_vehicle_all['time_frame'], df_vehicle_all['speed'], color='blue')
            plt.title(f'Vehicle: {v} - Speed')
            plt.xlabel('Time Frame')
            plt.ylabel('Speed')
            plt.show()
            
            # Plot travel time
            plt.figure(figsize=(10, 6))
            plt.plot(df_vehicle_all['time_frame'], df_vehicle_all['travel_time'], label='Travel Time', color='green')
            plt.title(f'Vehicle: {v} - Travel Time')
            plt.xlabel('Time Frame')
            plt.ylabel('Travel Time')
            plt.legend()
            plt.show()

