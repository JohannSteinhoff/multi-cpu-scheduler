#!/usr/bin/env python3
"""
Plotting script for HW5 results.

Generates the following plots:
1. Average Turnaround Time vs Lambda
2. Throughput vs Lambda
3. Average CPU Utilization vs Lambda
4. Average Ready Queue Length vs Lambda

Each plot shows both scenarios for comparison.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for saving files
import matplotlib.pyplot as plt
import csv
import sys


def read_csv_data(csv_file):
    """
    Read CSV file and return data separated by scenario.
    Returns two dictionaries (scenario1, scenario2) with lists for each metric.
    """
    scenario1 = {'lambda': [], 'avg_turnaround': [], 'throughput': [],
                 'avg_cpu_util': [], 'avg_ready_q': [],
                 'cpu0_util': [], 'cpu1_util': [], 'cpu2_util': [], 'cpu3_util': []}
    scenario2 = {'lambda': [], 'avg_turnaround': [], 'throughput': [],
                 'avg_cpu_util': [], 'avg_ready_q': [],
                 'cpu0_util': [], 'cpu1_util': [], 'cpu2_util': [], 'cpu3_util': []}

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            scenario = int(row['scenario'])
            data_dict = scenario1 if scenario == 1 else scenario2

            data_dict['lambda'].append(float(row['lambda']))
            data_dict['avg_turnaround'].append(float(row['avg_turnaround']))
            data_dict['throughput'].append(float(row['throughput']))
            data_dict['avg_cpu_util'].append(float(row['avg_cpu_util']))
            data_dict['avg_ready_q'].append(float(row['avg_ready_q']))
            data_dict['cpu0_util'].append(float(row['cpu0_util']))
            data_dict['cpu1_util'].append(float(row['cpu1_util']))
            data_dict['cpu2_util'].append(float(row['cpu2_util']))
            data_dict['cpu3_util'].append(float(row['cpu3_util']))

    # Sort by lambda
    for data in [scenario1, scenario2]:
        sorted_indices = sorted(range(len(data['lambda'])), key=lambda i: data['lambda'][i])
        for key in data.keys():
            data[key] = [data[key][i] for i in sorted_indices]

    return scenario1, scenario2


def create_plots(csv_file="results.csv", output_dir="."):
    """
    Read results CSV and create all required plots.
    """
    try:
        # Read the CSV file
        scenario1, scenario2 = read_csv_data(csv_file)
        total_records = len(scenario1['lambda']) + len(scenario2['lambda'])
        print(f"[OK] Loaded {total_records} results from {csv_file}")

        # Create figure with 4 subplots (2x2 layout)
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Multi-CPU Scheduling Simulation Results (4 CPUs, FCFS)',
                     fontsize=16, fontweight='bold')

        # ====================================================================
        # PLOT 1: Average Turnaround Time vs Lambda
        # ====================================================================
        ax = axes[0, 0]
        ax.plot(scenario1['lambda'], scenario1['avg_turnaround'],
                marker='o', linewidth=2, label='Scenario 1: Per-CPU Queues', color='#1f77b4')
        ax.plot(scenario2['lambda'], scenario2['avg_turnaround'],
                marker='s', linewidth=2, label='Scenario 2: Global Queue', color='#ff7f0e')
        ax.set_xlabel('λ (arrivals per second)', fontsize=11)
        ax.set_ylabel('Average Turnaround Time (sec)', fontsize=11)
        ax.set_title('Average Turnaround Time vs Arrival Rate', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # ====================================================================
        # PLOT 2: Throughput vs Lambda
        # ====================================================================
        ax = axes[0, 1]
        ax.plot(scenario1['lambda'], scenario1['throughput'],
                marker='o', linewidth=2, label='Scenario 1: Per-CPU Queues', color='#1f77b4')
        ax.plot(scenario2['lambda'], scenario2['throughput'],
                marker='s', linewidth=2, label='Scenario 2: Global Queue', color='#ff7f0e')
        ax.set_xlabel('λ (arrivals per second)', fontsize=11)
        ax.set_ylabel('Throughput (jobs/sec)', fontsize=11)
        ax.set_title('Throughput vs Arrival Rate', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # ====================================================================
        # PLOT 3: Average CPU Utilization vs Lambda
        # ====================================================================
        ax = axes[1, 0]
        ax.plot(scenario1['lambda'], scenario1['avg_cpu_util'],
                marker='o', linewidth=2, label='Scenario 1: Per-CPU Queues', color='#1f77b4')
        ax.plot(scenario2['lambda'], scenario2['avg_cpu_util'],
                marker='s', linewidth=2, label='Scenario 2: Global Queue', color='#ff7f0e')
        ax.set_xlabel('λ (arrivals per second)', fontsize=11)
        ax.set_ylabel('Average CPU Utilization', fontsize=11)
        ax.set_title('Average CPU Utilization vs Arrival Rate', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(bottom=0, top=1.05)  # Utilization is 0-1

        # ====================================================================
        # PLOT 4: Average Ready Queue Length vs Lambda
        # ====================================================================
        ax = axes[1, 1]
        ax.plot(scenario1['lambda'], scenario1['avg_ready_q'],
                marker='o', linewidth=2, label='Scenario 1: Per-CPU Queues', color='#1f77b4')
        ax.plot(scenario2['lambda'], scenario2['avg_ready_q'],
                marker='s', linewidth=2, label='Scenario 2: Global Queue', color='#ff7f0e')
        ax.set_xlabel('λ (arrivals per second)', fontsize=11)
        ax.set_ylabel('Average Ready Queue Length', fontsize=11)
        ax.set_title('Average Ready Queue Length vs Arrival Rate', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Adjust layout to prevent overlap
        plt.tight_layout()

        # Save the figure
        output_file = f"{output_dir}/hw5_results.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"[OK] Saved plot to {output_file}")

        # Also create individual plots for better readability in report
        create_individual_plots(scenario1, scenario2, output_dir)

    except FileNotFoundError:
        print(f"[ERROR] Could not find {csv_file}")
        print("  Run 'python3 run_experiments.py' first to generate results.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Error creating plots: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def create_individual_plots(scenario1, scenario2, output_dir="."):
    """
    Create individual high-resolution plots for each metric.
    These are better for including in reports.
    """
    metrics = [
        ('avg_turnaround', 'Average Turnaround Time (sec)', 'turnaround'),
        ('throughput', 'Throughput (jobs/sec)', 'throughput'),
        ('avg_cpu_util', 'Average CPU Utilization', 'cpu_util'),
        ('avg_ready_q', 'Average Ready Queue Length', 'ready_q')
    ]

    for column, ylabel, filename in metrics:
        fig, ax = plt.subplots(figsize=(8, 6))

        ax.plot(scenario1['lambda'], scenario1[column],
                marker='o', linewidth=2, markersize=8,
                label='Scenario 1: Per-CPU Queues', color='#1f77b4')
        ax.plot(scenario2['lambda'], scenario2[column],
                marker='s', linewidth=2, markersize=8,
                label='Scenario 2: Global Queue', color='#ff7f0e')

        ax.set_xlabel('λ (arrivals per second)', fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(f'{ylabel} vs Arrival Rate\n(4 CPUs, FCFS Scheduling)',
                     fontsize=13, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)

        # Special handling for utilization plot
        if column == 'avg_cpu_util':
            ax.set_ylim(bottom=0, top=1.05)

        plt.tight_layout()

        # Save individual plot
        output_file = f"{output_dir}/hw5_{filename}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"[OK] Saved {filename} plot to {output_file}")

        plt.close()


def print_summary_stats(csv_file="results.csv"):
    """
    Print summary statistics for the report.
    """
    scenario1, scenario2 = read_csv_data(csv_file)

    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)

    for scenario_num, data in [(1, scenario1), (2, scenario2)]:
        scenario_name = "Per-CPU Queues" if scenario_num == 1 else "Global Queue"

        print(f"\nScenario {scenario_num}: {scenario_name}")
        print("-" * 70)

        print(f"  Lambda Range: {min(data['lambda']):.0f} - {max(data['lambda']):.0f} processes/sec")
        print(f"  Turnaround:   {min(data['avg_turnaround']):.6f} - {max(data['avg_turnaround']):.6f} sec")
        print(f"  Throughput:   {min(data['throughput']):.2f} - {max(data['throughput']):.2f} jobs/sec")
        print(f"  CPU Util:     {min(data['avg_cpu_util']):.4f} - {max(data['avg_cpu_util']):.4f}")
        print(f"  Ready Queue:  {min(data['avg_ready_q']):.6f} - {max(data['avg_ready_q']):.6f} jobs")

        # Calculate maximum CPU utilization imbalance
        max_spread = 0.0
        for i in range(len(data['lambda'])):
            cpu_utils = [data['cpu0_util'][i], data['cpu1_util'][i],
                        data['cpu2_util'][i], data['cpu3_util'][i]]
            spread = max(cpu_utils) - min(cpu_utils)
            max_spread = max(max_spread, spread)

        print(f"  Max CPU imbalance: {max_spread:.6f} (difference between busiest and least busy CPU)")

    print("\n" + "="*70)


def main():
    """
    Main function to create all plots and print statistics.
    """
    print("Creating plots for HW5 results...\n")

    # Create the plots
    create_plots()

    # Print summary statistics
    print_summary_stats()

    print("\n[OK] All plots created successfully!")
    print("\nFiles generated:")
    print("  - hw5_results.png (combined 2x2 plot)")
    print("  - hw5_turnaround.png (individual plot)")
    print("  - hw5_throughput.png (individual plot)")
    print("  - hw5_cpu_util.png (individual plot)")
    print("  - hw5_ready_q.png (individual plot)")


if __name__ == "__main__":
    main()
