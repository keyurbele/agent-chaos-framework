from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any

class FailureType(Enum):
    NONE = "NOMINAL_OPERATION"
    CONGESTION_FAILURE = "CONGESTION_FAILURE"
    WORKER_STARVATION = "WORKER_STARVATION"
    QUEUE_OVERFLOW = "QUEUE_OVERFLOW"
    LATENCY_CASCADE = "LATENCY_CASCADE"
    FAULT_PROPAGATION_SPIKE = "FAULT_PROPAGATION_SPIKE"

class EventType(Enum):
    REQUEST_CREATED = "REQUEST_CREATED"
    REQUEST_COMPLETED = "REQUEST_COMPLETED"
    FAULT_INJECTED = "FAULT_INJECTED"
    QUEUE_THROTTLED = "QUEUE_THROTTLED"
    RESOURCE_ADAPTED = "RESOURCE_ADAPTED"

@dataclass
class SystemEvent:
    event_type: EventType
    timestamp: float
    agent_id: int
    workload_type: str
    latency: float = 0.0
    queue_depth: int = 0
    status_code: int = 200
    failure_mode: FailureType = FailureType.NONE
