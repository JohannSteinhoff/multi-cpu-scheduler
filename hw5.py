#!/usr/bin/env python3
"""
CS3360 Homework 5: Multi-CPU Discrete-Event Simulator
Johann Steinhoff

This thing simulates multiple CPUs handling jobs using FCFS schedulng.
I made two different “setups” basically:
  Scenario 1: each CPU just has its own ready queue (jobs get tossed randomly)
  Scenario 2: all CPUs share one big queue

Arrival + service times are both exponential (Poisson arrivals). It keeps going
until 10,000 jobs finish. Probably could tune this but whatever.
"""

import sys
import math
import random
import heapq
from collections import deque

# event type “constants” (helps keep track)
ARR = 0   # job shows up
DEP = 1   # job finishing / departing


def simulate(lmbda, avg_service, scenario, num_cpus, target_completions=10_000, seed=1):
    """
    Runs the multi-CPU discrete-event sim.

    Params:
        lmbda: arrival rate (jobs/sec)
        avg_service: avg time a job takes (seconds)
        scenario: 1 = per-CPU queues, 2 = shared global queue
        num_cpus: number of CPUs in the whole system
        target_completions: stop after this many jobs finish
        seed: random seed so it doesnt flake out

    Returns:
        A dict with stuff like:
        - completed: number of finished jobs
        - time: whole simulated time
        - avg_turnaround: how long jobs wait overall
        - throughput: jobs/sec
        - cpu_utils: per-CPU utilization (roughly)
        - avg_ready_q: time-weighted avg size of queue(s)
    """
    random.seed(seed)
    mu = 1.0 / avg_service  # service rate (jobs/sec); careful for div by zero lol

    # ============================================================================
    # EVENT QUEUE SETUP
    # ============================================================================
    # Priority queue of events: (t, kind, seq#, data)
    # - time = when event happens
    # - kind = ARR or DEP
    # - seq = just used to avoid weird ties messing up order
    # - data = misc (cpu id, pid, etc)
    event_q = []
    seq = 0  # tie breaker since heapq doesn't like equal keys sometimes

    # ============================================================================
    # CPU STATE TRACKING
    # ============================================================================
    # keep track of what each CPU is doing
    cpu_busy = [False] * num_cpus       # cpu is busy or not
    cpu_busy_time = [0.0] * num_cpus    # total amount of actual service time
    running_pid = [None] * num_cpus     # storing which pid is running rn

    # ============================================================================
    # READY QUEUES (depends on scenario)
    # ============================================================================
    if scenario == 1:
        # each CPU gets its own queue (FCFS)
        ready_queues = [deque() for _ in range(num_cpus)]
    else:
        # One giant FCFS queue shared by all
        global_ready_queue = deque()

    # ============================================================================
    # PROCESS BOOKKEEPING
    # ============================================================================
    next_pid = 0                 # giving processes ids
    arrival = {}                 # pid -> arrival time
    service = {}                 # pid -> service time
    assigned_cpu = {}            # used only for scenario 1, prob not needed elsewhere

    # ============================================================================
    # METRICS
    # ============================================================================
    current_time = 0.0
    completed = 0
    sum_turnaround = 0.0

    # tracking average queue length (kinda annoying honestly)
    rq_area = 0.0
    last_ev_time = 0.0

    # ============================================================================
    # HELPERS
    # ============================================================================

    def get_total_rq_len():
        """
        Returns total # of jobs in the ready queue(s).
        scenario 1: sum all per-CPU queues
        scenario 2: just check the global one
        """
        if scenario == 1:
            return sum(len(q) for q in ready_queues)
        else:
            return len(global_ready_queue)

    def enqueue_process(pid, cpu_id=None):
        """
        Puts a process into whatever queue it belongs in.
        scenario 1 -> use specific CPU’s queue
        scenario 2 -> dump it in global queue
        """
        if scenario == 1:
            ready_queues[cpu_id].append(pid)
        else:
            global_ready_queue.append(pid)

    def dequeue_process(cpu_id):
        """
        Grabs the next job for a cpu.
        scenario 1 -> pull from that CPU's queue
        scenario 2 -> take from global queue always

        Returns None if there's nothing waiting there.
        """
        if scenario == 1:
            if len(ready_queues[cpu_id]) > 0:
                return ready_queues[cpu_id].popleft()
            return None
        else:
            if len(global_ready_queue) > 0:
                return global_ready_queue.popleft()
            return None

    def schedule_next_arrival(now):
        """
        Schedules the next incoming job.  
        Interarrival is exponential w/ rate lambda.
        """
        nonlocal seq
        inter = random.expovariate(lmbda)
        heapq.heappush(event_q, (now + inter, ARR, seq, None))
        seq += 1

    def start_cpu_if_idle(cpu_id):
        """
        If CPU isn't doing anything, try to give it a job.
        scenario 1 -> CPU only uses *its* queue
        scenario 2 -> CPU can pull from shared queue

        Schedules a departure event once job starts.
        """
        nonlocal seq

        if cpu_busy[cpu_id]:
            return  # already working on something

        pid = dequeue_process(cpu_id)
        if pid is None:
            return

        # actually start service
        running_pid[cpu_id] = pid
        cpu_busy[cpu_id] = True
        st = service[pid]
        cpu_busy_time[cpu_id] += st  # keep track for utilization math later

        # schedule departure
        heapq.heappush(event_q, (current_time + st, DEP, seq, (cpu_id, pid)))
        seq += 1

    def try_start_all_cpus():
        """
        Tries to start work on any idle CPUs.
        In scenario 2, randomizes cpu order so CPU0 doesn't hog everthing.
        """
        if scenario == 1:
            for cid in range(num_cpus):
                start_cpu_if_idle(cid)
        else:
            cpu_order = list(range(num_cpus))
            random.shuffle(cpu_order)
            for cid in cpu_order:
                start_cpu_if_idle(cid)

    # ============================================================================
    # FIRST ARRIVAL (init)
    # ============================================================================
    first = random.expovariate(lmbda)
    heapq.heappush(event_q, (first, ARR, seq, None))
    seq += 1

    # ============================================================================
    # MAIN SIM LOOP
    # ============================================================================
    while completed < target_completions and event_q:
        ev_time, kind, _, data = heapq.heappop(event_q)

        # update area under queue-length curve
        rq_area += get_total_rq_len() * (ev_time - last_ev_time)
        last_ev_time = ev_time
        current_time = ev_time

        # arrival event
        if kind == ARR:
            pid = next_pid
            next_pid += 1

            arrival[pid] = ev_time
            st = random.expovariate(mu)
            service[pid] = st

            # put job in the right queue
            if scenario == 1:
                cpu_id = random.randint(0, num_cpus - 1)
                assigned_cpu[pid] = cpu_id
                enqueue_process(pid, cpu_id)
            else:
                enqueue_process(pid)

            schedule_next_arrival(ev_time)
            try_start_all_cpus()

        # departure event
        else:
            cpu_id, pid = data

            completed += 1
            sum_turnaround += (ev_time - arrival[pid])

            cpu_busy[cpu_id] = False
            running_pid[cpu_id] = None

            try_start_all_cpus()

    # ============================================================================
    # FINAL METRICS
    # ============================================================================
    avg_turnaround = sum_turnaround / completed if completed > 0 else float('nan')
    throughput = completed / current_time if current_time > 0 else 0.0

    cpu_utils = [
        cpu_busy_time[i] / current_time if current_time > 0 else 0.0
        for i in range(num_cpus)
    ]

    avg_rq_len = rq_area / current_time if current_time > 0 else 0.0

    return {
        "completed": completed,
        "time": current_time,
        "avg_turnaround": avg_turnaround,
        "throughput": throughput,
        "cpu_utils": cpu_utils,
        "avg_ready_q": avg_rq_len,
    }


def main():
    """
    Handles CLI args + runs the sim.

    Usage: python3 hw5.py <lambda> <avg_service> <scenario> <num_cpus>

    scenario = 1 (per-CPU queues)
             = 2 (shared queue)
    """
    if len(sys.argv) != 5:
        print("Usage: python3 hw5.py <arrival_rate_lambda> <avg_service_time> <scenario: 1 or 2> <num_cpus>")
        print("\nArgs:")
        print("  arrival_rate_lambda : lol basically how fast jobs show up")
        print("  avg_service_time    : avg service time, ex. 0.02 secs")
        print("  scenario            : 1 or 2 only")
        print("  num_cpus            : how many cpus u want")
        sys.exit(1)

    try:
        lmbda = float(sys.argv[1])
        avg_service = float(sys.argv[2])
        scenario = int(sys.argv[3])
        num_cpus = int(sys.argv[4])
    except ValueError:
        print("Error: wrong argument types. Lambda + avg_service gotta be floats,")
        print("       scenario + num_cpus must be ints.")
        sys.exit(1)

    if scenario not in (1, 2):
        print("Error: scenario must be 1 or 2, nothing else")
        sys.exit(1)

    if num_cpus < 1:
        print("Error: num_cpus needs to be at least 1, cant do zero lol")
        sys.exit(1)

    stats = simulate(lmbda, avg_service, scenario, num_cpus, target_completions=10_000, seed=1)

    scenario_label = f"Scenario {scenario}: "
    if scenario == 1:
        scenario_label += "Per-CPU Ready Queues"
    else:
        scenario_label += "Global Ready Queue"

    print(f"Scenario: \t\t\t{scenario_label}")
    print(f"Number of CPUs: \t\t{num_cpus}")
    print(f"Arrival rate (lambda): \t\t{lmbda:.2f} processes/sec")
    print(f"Avg service time: \t\t{avg_service:.4f} sec")
    print(f"Completed: \t\t\t{stats['completed']}")
    print(f"Sim time:  \t\t\t{stats['time']:.6f} sec")
    print(f"Avg turnaround: \t\t{stats['avg_turnaround']:.6f} sec")
    print(f"Throughput:     \t\t{stats['throughput']:.6f} jobs/sec")

    print(f"\nPer-CPU Utilization:")
    for i, util in enumerate(stats['cpu_utils']):
        print(f"  CPU {i}: \t\t\t{util:.6f}")

    avg_util = sum(stats['cpu_utils']) / len(stats['cpu_utils'])
    print(f"  Average: \t\t\t{avg_util:.6f}")

    print(f"\nAvg ready queue length: \t{stats['avg_ready_q']:.6f}")


if __name__ == "__main__":
    main()
