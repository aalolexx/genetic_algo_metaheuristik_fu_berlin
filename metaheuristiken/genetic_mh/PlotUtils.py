import matplotlib.pyplot as plt
import os
import random


def plot_losses(path):
    """
    Plots the average and best losses from text files in the given directory.
    
    Args:
        path (str): Directory containing 'average_losses.txt' and 'best_losses.txt'
    """
    avg_file = os.path.join(path, "average_losses.csv")
    best_file = os.path.join(path, "best_losses.csv")

    if not os.path.exists(avg_file) or not os.path.exists(best_file):
        print("One or both loss files do not exist in the given path.")
        return

    # Read average losses
    with open(avg_file, 'r') as f:
        average_losses = [float(line.strip()) for line in f if line.strip()]

    # Read best losses
    with open(best_file, 'r') as f:
        best_losses = [float(line.strip()) for line in f if line.strip()]

    # Create x-axis values
    generations = list(range(len(average_losses)))

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(generations, average_losses, label='Average Loss', color='blue')
    plt.plot(generations, best_losses, label='Best Loss', color='green')
    plt.xlabel('Generation')
    plt.ylabel('Loss')
    plt.title('Loss Over Generations')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Save the plot instead of showing it
    output_path = os.path.join(path, "loss_plot.png")
    plt.savefig(output_path)
    print(f"Plot saved to: {output_path}")


def plot_routes_timeline(path, routes, max_routes=800):
    # Optionally sample for performance
    if len(routes) > max_routes:
        routes = random.sample(routes, max_routes)

    fig, ax = plt.subplots(figsize=(12, 8))

    for idx, route in enumerate(routes):
        start = route.start_time
        end = route.start_time + route.distance
        ax.broken_barh([(start, route.distance)], (idx - 0.4, 0.8), facecolors='blue')

    ax.set_xlabel("Time")
    ax.set_ylabel("Route index")
    ax.set_title("Rescue Route Timeline")

    # Save the plot instead of showing it
    output_path = os.path.join(path, "gantt_routes_timeline.png")
    plt.savefig(output_path)
    print(f"Plot saved to: {output_path}")


def plot_people_on_street(path, routes, your_max_capacity, step_size=10):
    time_events = []

    for route in routes:
        start = route.start_time
        end = route.start_time + route.distance
        time_events.append((start, +1))
        time_events.append((end, -1))

    time_events.sort()
    current_people = 0
    times = []
    counts = []

    for t, delta in time_events:
        current_people += delta
        times.append(t)
        counts.append(current_people)

    plt.figure(figsize=(12, 4))
    plt.plot(times, counts, label='People on street')
    plt.axhline(y=your_max_capacity, color='red', linestyle='--', label='Street capacity')
    plt.xlabel("Time")
    plt.ylabel("People on Street")
    plt.title("Street Load Over Time")
    plt.legend()
    plt.tight_layout()
    
    # Save the plot instead of showing it
    output_path = os.path.join(path, "people_on_street_heatmap.png")
    plt.savefig(output_path)
    print(f"Plot saved to: {output_path}")
