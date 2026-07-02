import pandas as pd
import numpy as np
import os
import time
from typing import List
from core.types import SystemEvent, FailureType

class StreamTelemetryEngine:
    def __init__(self, window_size: int = 50):
        self.event_stream: List[SystemEvent] = []
        self.window_size = window_size

    def consume_event(self, event: SystemEvent):
        self.event_stream.append(event)

    def get_rolling_metrics(self) -> dict:
        """Computes statistical windowed metrics across the live event stream stream."""
        recent_events = self.event_stream[-self.window_size:]
        if not recent_events:
            return {"p95_latency": 0.0, "throughput_sec": 0.0, "error_clustering": 0.0}

        latencies = [e.latency for e in recent_events if e.latency > 0]
        p95 = np.percentile(latencies, 95) if latencies else 0.0

        # Calculate Throughput / Sec over window duration
        time_span = recent_events[-1].timestamp - recent_events[0].timestamp
        throughput = len(recent_events) / time_span if time_span > 0 else 0.0

        # Error Clustering Index (ratio of consecutive failures)
        failures = [1 if e.status_code >= 500 else 0 for e in recent_events]
        clustering_index = np.std(failures) if failures else 0.0

        return {
            "p95_latency": p95,
            "throughput_sec": throughput,
            "error_clustering": clustering_index
        }

    def generate_system_insights(self, experiment_id: str, state_history: list):
        """Automated Data Parsing & Insight Synthesis Layer."""
        df = pd.DataFrame([{
            "time": e.timestamp, "latency": e.latency, 
            "status": e.status_code, "q_depth": e.queue_depth
        } for e in self.event_stream])
        
        os.makedirs("analysis", exist_ok=True)
        df.to_csv(f"analysis/telemetry_{experiment_id}.csv", index=False)

        print(f"\n=== 🔬 EXPERIMENT DIAGNOSTIC REPORT: {experiment_id} ===")
        collapse_events = [s for s in state_history if s["system_state"] == "COLLAPSED"]
        
        if collapse_events:
            break_time = collapse_events[0]["timestamp"]
            print(f"STATUS          : CRITICAL STRUCTURAL COLLAPSE")
            print(f"Break-Point Time: T+{break_time:.2f} seconds into run")
            print(f"Primary Catalyst: {collapse_events[0]['anomalies_detected'][0]}")
        else:
            print(f"STATUS          : DETERMINISTIC NOMINAL STABILITY")
            print(f"Conclusion      : Core processing loops sustained target concurrent workload.")
        print("====================================================")
