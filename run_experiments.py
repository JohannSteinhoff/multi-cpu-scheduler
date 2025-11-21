#!/usr/bin/env python3
"""
Helper script to run all experiments for HW5 and save results to CSV.

This script runs the simulator for:
- Lambda values: 50 to 150 in steps of 10 (11 values)
- Average service time: 0.02 seconds (fixed)
- Both scenarios (1 and 2)
- 4 CPUs (fixed)

Results are saved to results.csv for easy plotting.
"""

import subprocess
import csv
import sys


def run_simulation(lmbda, avg_service, scenario, num_cpus):
    """
    Run a single simulation and parse the output.

    Returns a dictionary with all metrics.
    """
    cmd = ["python3", "hw5.py", str(lmbda), str(avg_service), str(scenario), str(num_cpus)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = result.stdout

        # Parse the output to extract metrics
        metrics = {
            "lambda": lmbda,
            "avg_service": avg_service,
            "scenario": scenario,
            "num_cpus": num_cpus,
        }

        # Parse line by line
        for line in output.split('\n'):
            if "Completed:" in line:
                metrics["completed"] = int(line.split()[-1])
            elif "Sim time:" in line:
                metrics["sim_time"] = float(line.split()[-2])
            elif "Avg turnaround:" in line:
                metrics["avg_turnaround"] = float(line.split()[-2])
            elif "Throughput:" in line:
                metrics["throughput"] = float(line.split()[-2])
            elif "Average:" in line and "CPU" not in line:
                # This is the average CPU utilization line
                metrics["avg_cpu_util"] = float(line.split()[-1])
            elif "Avg ready queue length:" in line:
                metrics["avg_ready_q"] = float(line.split()[-1])

        # Also parse individual CPU utilizations
        cpu_utils = []
        in_cpu_section = False
        for line in output.split('\n'):
            if "Per-CPU Utilization:" in line:
                in_cpu_section = True
                continue
            if in_cpu_section and "CPU " in line and ":" in line:
                if "Average:" in line:
                    break  # End of CPU section
                util = float(line.split()[-1])
                cpu_utils.append(util)

        # Add individual CPU utilizations
        for i, util in enumerate(cpu_utils):
            metrics[f"cpu{i}_util"] = util

        return metrics

    except subprocess.CalledProcessError as e:
        print(f"Error running simulation: {e}")
        print(f"Stderr: {e.stderr}")
        return None


def main():
    """
    Run all experiments and save to CSV.
    """
    print("Running all experiments for HW5...")
    print("This will take a few minutes...\n")

    # Experiment parameters (as specified in assignment)
    lambda_values = list(range(50, 151, 10))  # 50, 60, 70, ..., 150
    avg_service = 0.02  # Fixed at 0.02 seconds
    scenarios = [1, 2]  # Both scenarios
    num_cpus = 4  # Fixed at 4 CPUs

    results = []

    # Run all combinations
    total_runs = len(lambda_values) * len(scenarios)
    current_run = 0

    for scenario in scenarios:
        for lmbda in lambda_values:
            current_run += 1
            print(f"[{current_run}/{total_runs}] Running: λ={lmbda}, scenario={scenario}...", end=" ")

            metrics = run_simulation(lmbda, avg_service, scenario, num_cpus)

            if metrics:
                results.append(metrics)
                print(f"✓ (turnaround={metrics['avg_turnaround']:.6f}s, "
                      f"throughput={metrics['throughput']:.2f} jobs/s)")
            else:
                print("✗ Failed")

    # Save to CSV
    if results:
        output_file = "results.csv"
        print(f"\nSaving results to {output_file}...")

        # Determine all keys (some runs might have different numbers of CPUs)
        all_keys = set()
        for r in results:
            all_keys.update(r.keys())

        # Sort keys for consistent column order
        fieldnames = sorted(all_keys)

        # Write CSV
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"✓ Results saved to {output_file}")
        print(f"\nTotal runs: {len(results)}")
        print("\nYou can now use this CSV file to create plots for your report.")
        print("\nQuick summary:")
        print(f"  Lambda range: {min(lambda_values)} - {max(lambda_values)} processes/sec")
        print(f"  Scenarios: {scenarios}")
        print(f"  CPUs: {num_cpus}")
        print(f"  Service time: {avg_service} sec")

    else:
        print("\n✗ No results to save")
        sys.exit(1)


if __name__ == "__main__":
    main()
