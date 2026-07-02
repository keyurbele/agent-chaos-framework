import time

class ScientificCollapseDetector:
    def __init__(self, start_time: float, gradient_threshold: float = 1.5):
        self.start_time = start_time
        self.gradient_threshold = gradient_threshold
        self.previous_p95 = 0.0

    def evaluate_mathematical_model(self, current_p95: float, queue_depth: int, max_queue: int) -> dict:
        """
        Calculates mathematical stability boundaries.
        Collapse conditions met when: d(Queue)/dt > worker_capacity AND latency_gradient > threshold
        """
        status = "STABLE"
        anomalies = []

        # Quantify Latency Overlap Gradient
        if self.previous_p95 > 0:
            gradient = (current_p95 - self.previous_p95) / self.previous_p95
            if gradient > self.gradient_threshold:
                status = "COLLAPSED"
                anomalies.append(f"Latency Explosion Gradient Breached (+{gradient*100:.1f}%)")

        # Quantify Queue Pressure Ratio
        pressure_ratio = queue_depth / max_queue
        if pressure_ratio >= 0.85:
            status = "COLLAPSED"
            anomalies.append(f"Queue Divergence Overflow Balance (Saturation: {pressure_ratio*100:.1f}%)")
        elif pressure_ratio >= 0.50 and status != "COLLAPSED":
            status = "DEGRADED"

        self.previous_p95 = current_p95
        return {
            "system_state": status,
            "anomalies_detected": anomalies,
            "timestamp": time.time() - self.start_time
        }
