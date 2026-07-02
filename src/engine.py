import asyncio
import time
from typing import Dict, Any
from src.chaos import FaultInjector
from src.telemetry import TelemetryTracker

class AgentSimulationEngine:
    def __init__(self, total_agents: int, max_queue_size: int, num_workers: int):
        self.total_agents = total_agents
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.chaos = FaultInjector(drop_rate=0.15, latency_spike=0.25)
        self.telemetry = TelemetryTracker()
        self.num_workers = num_workers

    async def agent_producer(self, agent_id: int):
        start_time = time.perf_counter()
        payload = {"agent_id": agent_id, "produced_at": start_time}
        try:
            await self.queue.put(payload)
        except Exception as e:
            metrics = {
                "agent_id": agent_id,
                "timestamp": time.time(),
                "latency": time.perf_counter() - start_time,
                "status_code": 503,
                "queue_depth": self.queue.qsize()
            }
            self.telemetry.log_event(metrics)

    async def server_worker(self, worker_id: int):
        while True:
            payload = await self.queue.get()
            agent_id = payload["agent_id"]
            produced_at = payload["produced_at"]
            status_code = await self.chaos.apply_fault_models()
            current_depth = self.queue.qsize()
            latency = time.perf_counter() - produced_at
            
            metrics = {
                "agent_id": agent_id,
                "timestamp": time.time(),
                "latency": latency,
                "status_code": status_code,
                "queue_depth": current_depth
            }
            self.telemetry.log_event(metrics)
            self.queue.task_done()

    async def run_swarm(self):
        print(f"[*] Starting engine with {self.num_workers} backend server workers...")
        print(f"[*] Launching stress-test: {self.total_agents} agents flooding a queue...")
        
        workers = [asyncio.create_task(self.server_worker(i)) for i in range(self.num_workers)]
        producers = [self.agent_producer(i) for i in range(self.total_agents)]
        
        await asyncio.gather(*producers)
        await self.queue.join()
        
        for w in workers:
            w.cancel()
            
        self.telemetry.save_telemetry_data()
        self.telemetry.calculate_percentiles()

if __name__ == "__main__":
    engine = AgentSimulationEngine(total_agents=500, max_queue_size=100, num_workers=5)
    asyncio.run(engine.run_swarm())
