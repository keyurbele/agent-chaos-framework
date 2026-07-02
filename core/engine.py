import asyncio
import time
import random
from core.types import SystemEvent, EventType, FailureType
from fault_model.chaos import FaultInjector
from observability.telemetry import StreamTelemetryEngine
from observability.collapse_detector import CollapseDetector

class AgentStressTestbed:
    def __init__(self, total_agents: int, max_queue_size: int, starting_workers: int, seed: int = 42):
        random.seed(seed)
        self.total_agents = total_agents
        self.max_queue_size = max_queue_size
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.chaos = FaultInjector(drop_rate=0.05, latency_spike=0.20)
        self.telemetry = StreamTelemetryEngine()
        
        self.base_workers = starting_workers
        self.injection_throttle_delay = 0.0
        self.state_history = []
        
        # Track historical queue depths to compute actual d(Queue)/dt derivatives
        self.last_queue_depth = 0
        self.last_depth_timestamp = time.time()

    def calculate_queue_derivative(self, current_depth: int) -> float:
        """Computes d(Queue)/dt: the rate of change of queue depth per second."""
        now = time.time()
        delta_t = now - self.last_depth_timestamp
        if delta_t <= 0:
            return 0.0
        
        delta_q = current_depth - self.last_queue_depth
        dq_dt = delta_q / delta_t
        
        # Cache current values for next computation loop
        self.last_queue_depth = current_depth
        self.last_depth_timestamp = now
        return dq_dt

    async def workload_generator_producer(self, agent_id: int, workload_type: str):
        await asyncio.sleep(random.uniform(0.005, 0.1))
        
        if self.injection_throttle_delay > 0:
            await asyncio.sleep(self.injection_throttle_delay)
            
        start_time = time.perf_counter()
        payload = {"agent_id": agent_id, "type": workload_type, "produced_at": start_time}
        
        current_depth = self.queue.qsize()
        
        # 5. Organic Failure Loop: Queue pressure itself exponentially increases failure probability
        saturation_ratio = current_depth / self.max_queue_size
        dynamic_drop_chance = self.chaos.drop_rate + (saturation_ratio ** 2)
        
        if random.random() < dynamic_drop_chance and current_depth > 0:
            # Simulate a congestion-driven dropped connection before even entering the queue
            self.telemetry.consume_event(SystemEvent(
                EventType.FAULT_INJECTED, time.time(), agent_id, workload_type,
                latency=time.perf_counter() - start_time, status_code=503,
                queue_depth=current_depth, failure_mode=FailureType.CONGESTION_FAILURE
            ))
            return

        try:
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
                w_type = payload["type"]
                processing_weight = 2.0 if w_type == "HEAVY_REQUEST" else 1.0
                
                status = await self.chaos.apply_fault_models()
                if status >= 500:
                    f_mode = FailureType.FAULT_PROPAGATION_SPIKE
                else:
                    f_mode = FailureType.NONE
                    await asyncio.sleep(0.005 * processing_weight)
                
                latency = time.perf_counter() - payload["produced_at"]
                
                self.telemetry.consume_event(SystemEvent(
                    EventType.REQUEST_COMPLETED, time.time(), payload["agent_id"], w_type,
                    latency=latency, queue_depth=self.queue.qsize(), status_code=status, failure_mode=f_mode
                ))
                self.queue.task_done()
        except asyncio.CancelledError:
            pass

    async def closed_loop_control_system(self, detector: CollapseDetector):
        try:
            while True:
                await asyncio.sleep(0.05)
                metrics = self.telemetry.get_rolling_metrics()
                current_depth = self.queue.qsize()
                
                # Compute actual derivative values
                dq_dt = self.calculate_queue_derivative(current_depth)
                
                state = detector.evaluate_mathematical_model(
                    metrics["p95_latency"], current_depth, self.max_queue_size, dq_dt
                )
                self.state_history.append(state)

                # 4. Closed-Loop Backpressure Adaptation
                if state["system_state"] == "DEGRADED":
                    self.injection_throttle_delay = 0.02
                elif state["system_state"] == "COLLAPSED":
                    self.injection_throttle_delay = 0.10
                else:
                    self.injection_throttle_delay = 0.00
        except asyncio.CancelledError:
            pass

    async def execute_testbed(self, exp_id: str):
        start_wall_time = time.time()
        detector = CollapseDetector(start_time=start_wall_time)
        self.last_depth_timestamp = start_wall_time
        
        workers = [asyncio.create_task(self.backend_processor_worker(i)) for i in range(self.base_workers)]
        control_loop = asyncio.create_task(self.closed_loop_control_system(detector))
        
        producers = []
        for i in range(self.total_agents):
            w_choice = random.choice(["LIGHT_REQUEST", "LIGHT_REQUEST", "HEAVY_REQUEST"])
            producers.append(self.workload_generator_producer(i, w_choice))
            
        await asyncio.gather(*producers)
        await self.queue.join()
        
        control_loop.cancel()
        for w in workers:
            w.cancel()
            
        self.telemetry.generate_system_insights(exp_id, self.state_history)
        return self.state_history[-1]["system_state"] if self.state_history else "STABLE"
