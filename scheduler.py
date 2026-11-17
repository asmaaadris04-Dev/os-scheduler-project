import sys


def read_input(path):
    """Read processes from input.txt. Lines starting with # are comments."""
    procs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name, arrival, burst, priority = line.split()
            procs.append({
                "name": name,
                "arrival": int(arrival),
                "burst": int(burst),
                "priority": int(priority),
            })
    return procs


def pnum(p):
    """Number inside the name (P5 -> 5), used for tie-breaking."""
    return int("".join(ch for ch in p["name"] if ch.isdigit()))


def fcfs(procs):
    """Returns the Gantt chart as a list of (name, start, end)."""
    order = sorted(procs, key=lambda p: (p["arrival"], pnum(p)))
    time, gantt = 0, []
    for p in order:
        if time < p["arrival"]:               # CPU idle
            gantt.append(("idle", time, p["arrival"]))
            time = p["arrival"]
        gantt.append((p["name"], time, time + p["burst"]))
        time += p["burst"]
    return gantt


def priority_np(procs):
    """Non-preemptive priority. Smaller number = higher priority.
    Tie -> earlier arrival, then smaller process number."""
    remaining = list(procs)
    time, gantt = 0, []
    while remaining:
        ready = [p for p in remaining if p["arrival"] <= time]
        if not ready:                         # CPU idle until next arrival
            nxt = min(p["arrival"] for p in remaining)
            gantt.append(("idle", time, nxt))
            time = nxt
            continue
        p = min(ready, key=lambda p: (p["priority"], p["arrival"], pnum(p)))
        gantt.append((p["name"], time, time + p["burst"]))
        time += p["burst"]
        remaining.remove(p)
    return gantt


def metrics(procs, gantt):
    """Waiting, turnaround, response for each process."""
    result = {}
    for p in procs:
        slices = [(s, e) for n, s, e in gantt if n == p["name"]]
        first_start = slices[0][0]
        finish = slices[-1][1]
        turnaround = finish - p["arrival"]
        waiting = turnaround - p["burst"]
        response = first_start - p["arrival"]
        result[p["name"]] = (waiting, turnaround, response)
    return result


def print_gantt(gantt):
    bar, times = "|", f"{gantt[0][1]:<5}"
    for name, s, e in gantt:
        bar += f"{name:^5}|"
        times += f"{e:<6}"
    print(bar)
    print(times)


def report(title, procs, gantt):
    m = metrics(procs, gantt)
    print(f"\n===== {title} =====")
    print_gantt(gantt)
    print(f"\n{'Proc':<6}{'Waiting':<10}{'Turnaround':<12}{'Response':<10}")
    for p in procs:
        w, t, r = m[p["name"]]
        print(f"{p['name']:<6}{w:<10}{t:<12}{r:<10}")
    n = len(procs)
    avg = [sum(v[i] for v in m.values()) / n for i in range(3)]
    print(f"{'AVG':<6}{avg[0]:<10.2f}{avg[1]:<12.2f}{avg[2]:<10.2f}")
    return avg


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    procs = read_input(path)

    a = report("FCFS", procs, fcfs(procs))
    b = report("Priority (non-preemptive)", procs, priority_np(procs))

    print("\n===== Comparison (averages) =====")
    print(f"{'':<28}{'Waiting':<10}{'Turnaround':<12}{'Response':<10}")
    print(f"{'FCFS':<28}{a[0]:<10.2f}{a[1]:<12.2f}{a[2]:<10.2f}")
    print(f"{'Priority (non-preemptive)':<28}{b[0]:<10.2f}{b[1]:<12.2f}{b[2]:<10.2f}")


if __name__ == "__main__":
    main()
