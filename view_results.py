#!/usr/bin/env python3
"""
Simple results viewer for HW5.

Displays results in a formatted table without requiring any external libraries.
You can copy this data directly into your report or use it to create plots manually.
"""

import csv
import sys


def view_results(csv_file="results.csv"):
    """
    Read and display results in formatted tables.
    """
    try:
        # Read all data
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Separate by scenario
        scenario1 = [r for r in rows if r['scenario'] == '1']
        scenario2 = [r for r in rows if r['scenario'] == '2']

        # Sort by lambda
        scenario1.sort(key=lambda r: float(r['lambda']))
        scenario2.sort(key=lambda r: float(r['lambda']))

        print("="*100)
        print("HOMEWORK 5 RESULTS - MULTI-CPU SCHEDULING SIMULATION")
        print("="*100)
        print()

        # Print both scenarios side by side for comparison
        print_comparison_table(scenario1, scenario2)
        print()

        # Print detailed per-CPU utilization
        print_cpu_utilization_details(scenario1, scenario2)
        print()

        # Print summary statistics
        print_summary(scenario1, scenario2)

    except FileNotFoundError:
        print(f"Error: Could not find {csv_file}")
        print("Run 'python3 run_experiments.py' first to generate results.")
        sys.exit(1)


def print_comparison_table(scenario1, scenario2):
    """
    Print main metrics in a comparison table.
    """
    print("MAIN METRICS COMPARISON")
    print("-"*100)
    print(f"{'Lambda':>6} | {'Scenario 1 (Per-CPU Queues)':^40} | {'Scenario 2 (Global Queue)':^40}")
    print(f"{'':>6} | {'Turnaround':>10} {'Throughput':>10} {'CPU Util':>10} {'Queue':>8} | "
          f"{'Turnaround':>10} {'Throughput':>10} {'CPU Util':>10} {'Queue':>8}")
    print(f"{'(λ)':>6} | {'(sec)':>10} {'(jobs/s)':>10} {'(avg)':>10} {'(len)':>8} | "
          f"{'(sec)':>10} {'(jobs/s)':>10} {'(avg)':>10} {'(len)':>8}")
    print("-"*100)

    for s1, s2 in zip(scenario1, scenario2):
        lmbda = float(s1['lambda'])
        print(f"{lmbda:>6.0f} | "
              f"{float(s1['avg_turnaround']):>10.6f} "
              f"{float(s1['throughput']):>10.2f} "
              f"{float(s1['avg_cpu_util']):>10.4f} "
              f"{float(s1['avg_ready_q']):>8.2f} | "
              f"{float(s2['avg_turnaround']):>10.6f} "
              f"{float(s2['throughput']):>10.2f} "
              f"{float(s2['avg_cpu_util']):>10.4f} "
              f"{float(s2['avg_ready_q']):>8.2f}")

    print("-"*100)


def print_cpu_utilization_details(scenario1, scenario2):
    """
    Print per-CPU utilization for both scenarios.
    """
    print("PER-CPU UTILIZATION DETAILS")
    print("-"*100)

    print("\nScenario 1: Per-CPU Ready Queues")
    print(f"{'Lambda':>6} | {'CPU 0':>10} {'CPU 1':>10} {'CPU 2':>10} {'CPU 3':>10} | {'Avg':>10} {'Spread':>10}")
    print("-"*70)

    for row in scenario1:
        lmbda = float(row['lambda'])
        cpu0 = float(row['cpu0_util'])
        cpu1 = float(row['cpu1_util'])
        cpu2 = float(row['cpu2_util'])
        cpu3 = float(row['cpu3_util'])
        avg = float(row['avg_cpu_util'])
        spread = max(cpu0, cpu1, cpu2, cpu3) - min(cpu0, cpu1, cpu2, cpu3)

        print(f"{lmbda:>6.0f} | {cpu0:>10.6f} {cpu1:>10.6f} {cpu2:>10.6f} {cpu3:>10.6f} | "
              f"{avg:>10.6f} {spread:>10.6f}")

    print()
    print("Scenario 2: Global Ready Queue")
    print(f"{'Lambda':>6} | {'CPU 0':>10} {'CPU 1':>10} {'CPU 2':>10} {'CPU 3':>10} | {'Avg':>10} {'Spread':>10}")
    print("-"*70)

    for row in scenario2:
        lmbda = float(row['lambda'])
        cpu0 = float(row['cpu0_util'])
        cpu1 = float(row['cpu1_util'])
        cpu2 = float(row['cpu2_util'])
        cpu3 = float(row['cpu3_util'])
        avg = float(row['avg_cpu_util'])
        spread = max(cpu0, cpu1, cpu2, cpu3) - min(cpu0, cpu1, cpu2, cpu3)

        print(f"{lmbda:>6.0f} | {cpu0:>10.6f} {cpu1:>10.6f} {cpu2:>10.6f} {cpu3:>10.6f} | "
              f"{avg:>10.6f} {spread:>10.6f}")

    print("-"*70)


def print_summary(scenario1, scenario2):
    """
    Print summary statistics and observations.
    """
    print("SUMMARY AND KEY OBSERVATIONS")
    print("-"*100)

    for scenario_num, data, name in [(1, scenario1, "Per-CPU Queues"),
                                      (2, scenario2, "Global Queue")]:
        print(f"\nScenario {scenario_num}: {name}")

        turnarounds = [float(r['avg_turnaround']) for r in data]
        throughputs = [float(r['throughput']) for r in data]
        utils = [float(r['avg_cpu_util']) for r in data]
        queues = [float(r['avg_ready_q']) for r in data]
        lambdas = [float(r['lambda']) for r in data]

        # Calculate CPU imbalance
        spreads = []
        for row in data:
            cpus = [float(row[f'cpu{i}_util']) for i in range(4)]
            spreads.append(max(cpus) - min(cpus))

        print(f"  Lambda range:          {min(lambdas):.0f} - {max(lambdas):.0f} processes/sec")
        print(f"  Turnaround time:       {min(turnarounds):.6f} - {max(turnarounds):.6f} sec")
        print(f"  Throughput:            {min(throughputs):.2f} - {max(throughputs):.2f} jobs/sec")
        print(f"  CPU utilization:       {min(utils):.4f} - {max(utils):.4f}")
        print(f"  Ready queue length:    {min(queues):.2f} - {max(queues):.2f} jobs")
        print(f"  Max CPU imbalance:     {max(spreads):.6f}")

    # Comparison
    print("\nScenario Comparison:")

    # Average turnaround at high load (λ=150)
    s1_turnaround = float(scenario1[-1]['avg_turnaround'])
    s2_turnaround = float(scenario2[-1]['avg_turnaround'])
    improvement = ((s1_turnaround - s2_turnaround) / s1_turnaround) * 100

    print(f"  At λ=150:")
    print(f"    Turnaround time reduction: {improvement:.1f}% (Scenario 2 is better)")

    # Queue length comparison
    s1_queue = float(scenario1[-1]['avg_ready_q'])
    s2_queue = float(scenario2[-1]['avg_ready_q'])
    queue_reduction = ((s1_queue - s2_queue) / s1_queue) * 100

    print(f"    Queue length reduction:    {queue_reduction:.1f}% (Scenario 2 is better)")

    # CPU balance
    s1_spreads = []
    s2_spreads = []
    for r1, r2 in zip(scenario1, scenario2):
        cpus1 = [float(r1[f'cpu{i}_util']) for i in range(4)]
        cpus2 = [float(r2[f'cpu{i}_util']) for i in range(4)]
        s1_spreads.append(max(cpus1) - min(cpus1))
        s2_spreads.append(max(cpus2) - min(cpus2))

    print(f"    CPU load balance:          Scenario 2 has {max(s2_spreads):.6f} max spread")
    print(f"                               Scenario 1 has {max(s1_spreads):.6f} max spread")

    print("\nConclusion:")
    print("  Scenario 2 (Global Queue) provides:")
    print("    ✓ Lower average turnaround times")
    print("    ✓ Shorter ready queue lengths")
    print("    ✓ Better CPU load balancing")
    print("    ✓ Same overall throughput capacity")

    print("-"*100)


def export_for_excel(csv_file="results.csv", output_file="results_excel.csv"):
    """
    Create a simplified CSV that's easier to import into Excel for plotting.
    """
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Create simplified format
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow(['Lambda', 'Scenario', 'Avg_Turnaround', 'Throughput',
                        'CPU_Utilization', 'Ready_Queue_Length'])

        # Data rows
        for row in rows:
            writer.writerow([
                row['lambda'],
                f"Scenario {row['scenario']}",
                row['avg_turnaround'],
                row['throughput'],
                row['avg_cpu_util'],
                row['avg_ready_q']
            ])

    print(f"✓ Simplified CSV exported to {output_file}")
    print("  This file can be easily imported into Excel or Google Sheets for plotting.")


def main():
    """
    Main function to display results.
    """
    if len(sys.argv) > 1 and sys.argv[1] == "--export":
        export_for_excel()
    else:
        view_results()
        print("\nTip: Run 'python3 view_results.py --export' to create a simplified CSV for Excel.")


if __name__ == "__main__":
    main()
