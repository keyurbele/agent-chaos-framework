import time

class CollapseDetector:
    def __init__(self, start_time: float, gradient_threshold: float = 1.0):
        self.start_time = start_time
        self.gradient_threshold = gradient_threshold
        self.previous_p95 = 0.0

    def evaluate_mathematical_model(self, current_p95: float, queue_depth: int, max_queue: int, dq_dt: float) -> dict:
        """
        Calculates system stability state based on real-time parameters.
        Tracks d(Queue)/dt to verify if input rate persistently eclipses drain rate.
        """
        status = "STABLE"
        anomalies = []

        # Track Latency Growth Rate
        if self.previous_p95 > 0:
            latency_gradient = (current_p95 - self.previous_p95) / self.previous_p95
            if latency_gradient > self.gradient_threshold:
                status = "COLLAPSED"
                anomalies.append(f"Latency Spike Gradient Exception (+{latency_gradient*100:.1f}%)")

        # 2. Honest Math Verification: Cross-reference dq_dt directly with queue saturation
        pressure_ratio = queue_depth / max_queue
        if pressure_ratio >= 0.85 or (dq_dt > 15.0 and pressure_ratio > 0.60):
            status = "COLLAPSED"
            anomalies.append(f"Queue Accumulation Divergence (dK/dt={dq_dt:.1f} req/sec at {pressure_ratio*100:.1f}% load)")
        elif pressure_ratio >= 0.40 and status != "COLLAPSED":
            status = "DEGRADED"

        self.previous_p95 = current_p95
        return {
            "system_state": status,
            "anomalies_detected": anomalies,
            "timestamp": time.time() - self.start_time
        }
