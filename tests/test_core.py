import asyncio
from core.types import FailureType, EventType, SystemEvent
from observability.collapse_detector import CollapseDetector

def test_failure_taxonomy_assignment():
    """Verify that events accept and store explicit structural failure classifications."""
    event = SystemEvent(
        event_type=EventType.FAULT_INJECTED,
        timestamp=100.0,
        agent_id=7,
        workload_type="HEAVY_REQUEST",
        failure_mode=FailureType.CONGESTION_FAILURE
    )
    assert event.failure_mode == FailureType.CONGESTION_FAILURE
    assert event.workload_type == "HEAVY_REQUEST"

def test_collapse_detector_gradient_trip():
    """Verify detector catches rapid latency changes using calculated slope evaluations."""
    detector = CollapseDetector(start_time=0.0, gradient_threshold=1.0)
    
    # Establish a stable baseline
    _ = detector.evaluate_mathematical_model(current_p95=0.02, queue_depth=5, max_queue=100, dq_dt=0.0)
    
    # Introduce a massive 300% surge in latency metrics
    result = detector.evaluate_mathematical_model(current_p95=0.09, queue_depth=10, max_queue=100, dq_dt=5.0)
    assert result["system_state"] == "COLLAPSED"

if __name__ == "__main__":
    print("[*] Launching local unit validation checks...")
    test_failure_taxonomy_assignment()
    test_collapse_detector_gradient_trip()
    print("[+] System unit validations verified successfully.")
