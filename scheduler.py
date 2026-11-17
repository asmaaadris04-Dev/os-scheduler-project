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


def draw_gantt(title, gantt, filename):
    """Draw the Gantt chart with matplotlib and save it as a PNG image."""
    try:
        import matplotlib
        matplotlib.use("Agg")            # save to file, no window needed
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed: skipping the chart "
              "(install it with: pip install matplotlib)")
        return

    names = sorted({n for n, s, e in gantt if n != "idle"},
                   key=lambda n: int("".join(c for c in n if c.isdigit())))
    colors = plt.cm.tab10.colors
    color_of = {n: colors[i % 10] for i, n in enumerate(names)}

    fig, ax = plt.subplots(figsize=(10, 2.2))
    for name, start, end in gantt:
        if name == "idle":
            color, label = "lightgray", "idle"
        else:
            color, label = color_of[name], name
        ax.barh(0, end - start, left=start, color=color,
                edgecolor="black", height=0.5)
        ax.text((start + end) / 2, 0, label, ha="center", va="center",
                fontsize=10, fontweight="bold")

    ticks = sorted({s for _, s, _ in gantt} | {e for _, _, e in gantt})
    ax.set_xticks(ticks)
    ax.set_yticks([])
    ax.set_xlabel("Time")
    ax.set_title(title)
    plt.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)
    print(f"Gantt chart saved: {filename}")


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

    g1 = fcfs(procs)
    g2 = priority_np(procs)

    a = report("FCFS", procs, g1)
    draw_gantt("Gantt chart - FCFS", g1, "gantt_fcfs.png")

    b = report("Priority (non-preemptive)", procs, g2)
    draw_gantt("Gantt chart - Priority (non-preemptive)", g2, "gantt_priority.png")

    print("\n===== Comparison (averages) =====")
    print(f"{'':<28}{'Waiting':<10}{'Turnaround':<12}{'Response':<10}")
    print(f"{'FCFS':<28}{a[0]:<10.2f}{a[1]:<12.2f}{a[2]:<10.2f}")
    print(f"{'Priority (non-preemptive)':<28}{b[0]:<10.2f}{b[1]:<12.2f}{b[2]:<10.2f}")


if __name__ == "__main__":
    main()
