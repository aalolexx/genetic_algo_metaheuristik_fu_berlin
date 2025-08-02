import matplotlib.pyplot as plt
import os
import random
import matplotlib.cm as cm
import ast
import numpy as np
from collections import defaultdict
import re

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


def plot_routes_timeline(path, routes, max_routes=500):
    if len(routes) > max_routes:
        routes = random.sample(routes, max_routes)

    fig, ax = plt.subplots(figsize=(12, 8))

    # Assign a unique color per PR using a colormap
    unique_prs = list(set(route.PR for route in routes))
    colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_prs)))
    pr_to_color = {pr: colors[i] for i, pr in enumerate(unique_prs)}

    # Plot each route
    for idx, route in enumerate(routes):
        start = route.cluster.start_time
        ax.broken_barh(
            [(start, route.distance)],
            (idx - 0.4, 0.8),
            facecolors=pr_to_color[route.PR]
        )

    # Add vertical lines for each unique cluster start time
    unique_start_times = sorted(set(route.cluster.start_time for route in routes))
    for st in unique_start_times:
        ax.axvline(x=st, color='gray', linestyle='--', linewidth=1)
        ax.text(st, random.randrange(0, len(routes)), f"t={st}", rotation=90, va='bottom', ha='right', fontsize=8, color='gray')

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
        time_events.append((start, route.group_size))
        time_events.append((end, -1 * route.group_size))

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


def plot_generation_birthtype_loss(path, top_y=None):
    file_path = os.path.join(path, "detailed_generation_loss.csv")
    output_path = os.path.join(path, "generation_birthtype_loss.png")

    if not top_y is None:
        output_path = os.path.join(path, "generation_birthtype_loss_zoomed_y.png")

    generations = []

    # Read and parse file line by line
    with open(file_path, "r") as file:
        for idx, line in enumerate(file):
            line = line.strip()
            if not line:
                continue
            try:
                # remove the np.float64(...), as it is not valid python literal syntax and causes a Value error (at least for me)
                line = re.sub(r'np\.float64\(([^)]+)\)', r'\1', line)
                generation = ast.literal_eval(line)
                generations.append(generation)
            except Exception as e:
                print(f"⚠️ Failed to parse line {idx + 1}: {e}")
                continue

    # Organize data for fast plotting
    birth_type_data = defaultdict(lambda: {"x": [], "y": []})

    for gen_idx, generation in enumerate(generations):
        for ind in generation:
            bt = ind["birth_type"]
            loss = ind["loss"]
            birth_type_data[bt]["x"].append(gen_idx)
            birth_type_data[bt]["y"].append(loss)

    # Setup color map
    birth_types = sorted(birth_type_data.keys())
    cmap = cm.get_cmap("rainbow", len(birth_types))
    color_map = {bt: cmap(i) for i, bt in enumerate(birth_types)}

    # Plot all points in bulk per birth_type
    fig, ax = plt.subplots(figsize=(14, 8))
    if not top_y is None:
        plt.ylim(top=top_y)
    for bt in birth_types:
        ax.scatter(
            birth_type_data[bt]["x"],
            birth_type_data[bt]["y"],
            color=color_map[bt],
            label=bt,
            alpha=0.75,
            s=20
        )

    ax.set_xlabel("Generation")
    ax.set_ylabel("Loss")
    ax.set_title("Loss by Generation and Birth Type")
    ax.legend(title="Birth Type", loc="best")
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Plot saved to: {output_path}")


def plot_pr_usage_vs_capacity(path, routes, pr_list):
    output_path = os.path.join(path, "pr_usages.png")

    # Initialize PR usage dictionary
    pr_usage = {pr['id']: 0 for pr in pr_list}
    pr_capacity = {pr['id']: pr['capacity'] for pr in pr_list}

    # Count how many people are assigned to each PR
    for route in routes:
        if route.PR in pr_usage:
            pr_usage[route.PR] += route.group_size
        else:
            print(f"Warning: PR {route.PR} not found in PR list")

    # Sort PRs for consistent plotting
    pr_ids = sorted(pr_usage.keys())

    usage = [pr_usage[pr_id] for pr_id in pr_ids]
    capacities = [pr_capacity[pr_id] for pr_id in pr_ids]

    x = range(len(pr_ids))

    # Plotting
    plt.figure(figsize=(14, 6))
    plt.bar(x, capacities, width=0.4, label='Capacity', align='center', color='lightgray', edgecolor='black')
    plt.bar(x, usage, width=0.4, label='Current Usage', align='edge', color='steelblue')

    # Highlight overflows
    for i, (u, c) in enumerate(zip(usage, capacities)):
        if u > c:
            plt.bar(i, u - c, width=0.4, bottom=c, alpha=0.3, color='red', label='Overflow' if i == 0 else "")

    plt.xticks(x, pr_ids, rotation=45)
    plt.xlabel('PR ID')
    plt.ylabel('Number of Assigned People')
    plt.title('PR Usage vs Capacity')
    plt.legend()
    plt.tight_layout()

    plt.savefig(output_path)
    print(f"Saved plot to {output_path}")