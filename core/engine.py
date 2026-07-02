import asyncio
import time
import random
from core.types import SystemEvent, EventType, FailureType
from fault_model.chaos import FaultInjector
from observability.telemetry import StreamTelemetryEngine
from observability.collapse_detector import ScientificCollapseDetector

class AgentStressTestbed:
    def __init__(self, total_agents: int, max_queue_size: int, starting_workers: int, seed: int = 42):
        random.seed(seed) # Strict reproducibility anchor
        self.total_agents = total_agents
        self.max_queue_size = max_queue_size
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.chaos = FaultInjector(drop_rate=0.15, latency_spike=0.25)
        self.telemetry = StreamTelemetryEngine()
        
        self.base_workers = starting_workers
        self.injection_throttle_delay = 0.0
        self.state_history = []

    async def workload_generator_producer(self, agent_id: int, workload_type: str):
        """Diversified Client Workload Engine."""
        await asyncio.sleep(random.uniform(0.01, 0.2)) # Distribute initial thread pressure
        
        # Apply closed-loop pacing adaptation backpressure
        if self.injection_throttle_delay > 0:
            await asyncio.sleep(self.injection_throttle_delay)
            
        start_time = time.perf_counter()
        payload = {"agent_id": agent_id, "type": workload_type, "produced_at": start_time}
        
        try:
            # Handle queue drops cleanly via structured failure taxonomy
            if self.queue.qsize() >= self.max_queue_size:
                raise asyncio.QueueFull
            await self.queue.put(payload)
            self.telemetry.consume_event(SystemEvent(
                EventType.REQUEST_CREATED, time.time(), agent_id, workload_type, queue_depth=self.queue.qsize()
            ))
        except (asyncio.QueueFull, Exception):
            self.telemetry.consume_event(SystemEvent(
                EventType.FAULT_INJECTED, time.time(), agent_id, workload_type,
                latency=time.perf_counter() - start_time, status_code=503,
                queue_depth=self.queue.qsize(), failure_mode=FailureType.QUEUE_OVERFLOW
            ))

    async def backend_processor_worker(self, worker_id: int):
        try:
            while True:
                payload = await self.queue.get()
                agent_id = payload["agent_id"]
                w_type = payload["type"]
                
                # Dynamic complexity multiplier for differentiated workloads
                processing_weight = 2.5 if w_type == "HEAVY_REQUEST" else 1.0
                
                status = await self.chaos.apply_fault_models()
                if status >= 500:
                    f_mode = FailureType.FAULT_PROPAGATION_SPIKE
                else:
                    f_mode = FailureType.NONE
                    await asyncio.sleep(0.01 * processing_weight)
                
                latency = time.perf_counter() - payload["produced_at"]
                
                self.telemetry.consume_event(SystemEvent(
                    EventType.REQUEST_COMPLETED, time.time(), agent_id, w_type,
                    latency=latency, queue_depth=self.queue.qsize(), status_code=status, failure_mode=f_mode
                ))
                self.queue.task_done()
        except asyncio.CancelledError:
            pass

    async def closed_loop_control_system(self, detector: ScientificCollapseDetector):
        """Active Control Loop: Continuous Monitor-Analyze-Adapt Execution."""
        try:
            while True:
                await asyncio.sleep(0.05)
                metrics = self.telemetry.get_rolling_metrics()
                current_depth = self.queue.qsize()
                
                state = detector.evaluate_mathematical_model(metrics["p95_latency"], current_depth, self.max_queue_size)
                self.state_history.append(state)

                # Closed-Loop Mitigation Adaption
                if state["system_state"] == "DEGRADED":
                    self.injection_throttle_delay = 0.05  # Restrict workload generators
                elif state["system_state"] == "COLLAPSED":
                    self.injection_throttle_delay = 0.20  # Extreme mitigation throttle
                else:
                    self.injection_throttle_delay = 0.00  # Nominal throughput optimization
        except asyncio.CancelledError:
            pass

    async def execute_testbed(self, exp_id: str):
        start_wall_time = time.time()
        detector = ScientificCollapseDetector(start_time=start_wall_time)
        
        workers = [asyncio.create_task(self.backend_processor_worker(i)) for i in range(self.base_workers)]
        control_loop = asyncio.create_task(self.closed_loop_control_system(detector))
        
        # Build diversified client matrix
        producers = []
        for i in range(self.total_agents):
            w_choice = random.choice(["LIGHT_REQUEST", "LIGHT_REQUEST", "HEAVY_REQUEST", "BURST_INJECTION"])
            producers.append(self.workload_generator_producer(i, w_choice))
            
        await asyncio.gather(*producers)
        await self.queue.join()
        
        control_loop.cancel()
        for w in workers:
            w.cancel()
            
        self.telemetry.generate_system_insights(exp_id, self.state_history)
        return self.state_history[-1]["system_state"] if self.state_history else "STABLE"
