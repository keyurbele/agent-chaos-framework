import pandas as pd
import matplotlib.pyplot as plt
import os

def generate_performance_charts():
    csv_path = "analysis/telemetry_output.csv"
    if not os.path.exists(csv_path):
        print(f"[-] Data file missing at {csv_path}.")
        return

    df = pd.read_csv(csv_path)
    df = df.sort_values(by="timestamp")
    df["relative_time"] = df["timestamp"] - df["timestamp"].min()

    plt.figure(figsize=(12, 6))

    plt.subplot(2, 1, 1)
    plt.plot(df["relative_time"], df["latency"], color="crimson", alpha=0.6, label="Request Latency")
    plt.title("System Breakpoint Analysis: Latency vs. Queue Saturation")
    plt.ylabel("Latency (seconds)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.fill_between(df["relative_time"], df["queue_depth"], color="royalblue", alpha=0.4, label="Queue Backlog")
    plt.xlabel("Simulation Elapsed Time (seconds)")
    plt.ylabel("Queue Size")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()

    plt.tight_layout()
    plt.savefig("analysis/system_collapse_curve.png", dpi=300)
    print("[+] Research plot saved successfully to analysis/system_collapse_curve.png")

if __name__ == "__main__":
    generate_performance_charts()
