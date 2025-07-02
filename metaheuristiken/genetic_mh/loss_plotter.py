import matplotlib.pyplot as plt
import os

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
