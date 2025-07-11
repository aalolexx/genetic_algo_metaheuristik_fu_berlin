import matplotlib.pyplot as plt
import os
import random
import matplotlib.cm as cm
import matplotlib.colors as mcolors


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


def plot_loss_dict(path):
    """
    Plots all losses of the best solution of each generation to analyze how they relate and develop
    """
    # Load data
    value1_list = []
    value2_list = []
    value3_list = []

    dict_file = os.path.join(path, "best_solution_loss_dict.csv")

    with open(dict_file, 'r') as f:
        for row in f:
            # Convert string like "(140.8, 1, 1.0)" to actual tuple
            tup = eval(row.strip())  # Safe here if you fully trust the file
            value1_list.append(tup[0])
            value2_list.append(tup[1])
            value3_list.append(tup[2])

    # X-axis is just the generation/index
    x = list(range(len(value1_list)))

    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(x, value1_list, label='Street Cap Overflow')
    plt.plot(x, value2_list, label='PR Overflow')
    plt.plot(x, value3_list, label='Time (normalized)')

    plt.xlabel("Generation")
    plt.ylabel("Metric Value")
    plt.title("Loss Dict of each generation")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save the plot instead of showing it
    output_path = os.path.join(path, "loss_dict_plot.png")
    plt.savefig(output_path)
    print(f"Plot saved to: {output_path}")


def plot_routes_timeline(path, routes, max_routes=800):
    if len(routes) > max_routes:
        routes = random.sample(routes, max_routes)

    fig, ax = plt.subplots(figsize=(12, 8))

    # Assign a unique color per PR using a simple color cycle
    unique_prs = list(set(route.PR for route in routes))
    colors = plt.cm.rainbow.resampled(len(unique_prs))
    pr_to_color = {pr: colors(i) for i, pr in enumerate(unique_prs)}

    for idx, route in enumerate(routes):
        start = route.cluster.start_time
        ax.broken_barh(
            [(start, route.distance)],
            (idx - 0.4, 0.8),
            facecolors=pr_to_color[route.PR]
        )

    ax.set_xlabel("Time")
    ax.set_ylabel("Route index")
    ax.set_title("Rescue Route Timeline (Colored by PR)")
    plt.tight_layout()

    output_path = os.path.join(path, "gantt_routes_timeline.png")
    plt.savefig(output_path)
    print(f"Plot saved to: {output_path}")


def plot_people_on_street(path, routes, your_max_capacity, step_size=10):
    time_events = []

    for route in routes:
        start = route.cluster.start_time
        end = route.cluster.start_time + route.distance
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
