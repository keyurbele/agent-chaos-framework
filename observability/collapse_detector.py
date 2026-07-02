import time

class CollapseDetector:
    def __init__(self, latency_threshold_gradient: float = 2.0):
        # If latency grows by 200% (2.0x) too quickly, trigger collapse alert
        self.gradient_threshold = latency_threshold_gradient
        self.last_p95 = 0.0

    def evaluate_system_state(self, current_p95: float, current_queue_depth: int) -> dict:
        """Analyzes real-time metrics stream to predict infrastructure failure loops."""
        status = "STABLE"
        metrics_breached = []

        # Detect Latency Explosion Rate
        if self.last_p95 > 0:
            growth_rate = (current_p95 - self.last_p95) / self.last_p95
            if growth_rate > self.gradient_threshold:
                status = "COLLAPSED"
                metrics_breached.append(f"Latency Gradient Explosion (+{growth_rate*100:.1f}%)")

        # Detect Structural Queue Divergence
        if current_queue_depth > 80:
            status = "DEGRADED" if status != "COLLAPSED" else "COLLAPSED"
            metrics_breached.append(f"Critical Queue Saturation ({current_queue_depth} deep)")

        self.last_p95 = current_p95

        return {
            "system_state": status,
            "anomalies_detected": metrics_breached,
            "timestamp": time.time()
        }
