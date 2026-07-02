import pandas as pd
import numpy as np
import os
from typing import Dict, Any

class TelemetryTracker:
    def __init__(self):
        self.raw_logs = []

    def log_event(self, metrics: Dict[str, Any]):
        self.raw_logs.append(metrics)

    def save_telemetry_data(self):
        df = pd.DataFrame(self.raw_logs)
        os.makedirs("analysis", exist_ok=True)
        df.to_csv("analysis/telemetry_output.csv", index=False)
        print("[+] Telemetry logs safely exported to analysis/telemetry_output.csv")

    def calculate_percentiles(self):
        if not self.raw_logs:
            print("[-] No telemetry logs recorded.")
            return
            
        df = pd.DataFrame(self.raw_logs)
        latencies = df["latency"].values
        
        p50 = np.percentile(latencies, 50)
        p95 = np.percentile(latencies, 95)
        p99 = np.percentile(latencies, 99)
        error_rate = (df["status_code"] >= 500).mean() * 100
        max_queue_observed = df["queue_depth"].max()

        print("\n=== SYSTEM ARCHITECTURE SIMULATION RESULTS ===")
        print(f"Median (p50) Latency    : {p50:.4f} seconds")
        print(f"Severe (p95) Latency    : {p95:.4f} seconds")
        print(f"Outlier (p99) Latency   : {p99:.4f} seconds")
        print(f"Peak Queue Saturation   : {max_queue_observed} requests deep")
        print(f"Total Swarm Error Rate  : {error_rate:.2f}%")
        print("==============================================")
