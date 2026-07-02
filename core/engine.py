import asyncio
import time
from typing import Dict, Any
from src.chaos import FaultInjector
from src.telemetry import TelemetryTracker

class AgentSimulationEngine:
    def __init__(self, total_agents: int, max_queue_size: int, starting_workers: int):
        self.total_agents = total_agents
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.chaos = FaultInjector(drop_rate=0.15, latency_spike=0.25)
        self.telemetry = TelemetryTracker()
        self.current_workers = starting_workers
        self.worker_tasks = []

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
        try:
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
        except asyncio.CancelledError:
            pass

    async def auto_scaler_monitor(self):
        """Dynamic load balancer: Monitors queue depth and spins up workers on demand."""
        worker_id_counter = self.current_workers
        while True:
            await asyncio.sleep(0.1) # Check system health every 100ms
            queue_depth = self.queue.qsize()
            
            # If queue saturation passes 50%, scale up backend resources immediately
            if queue_depth > 50 and len(self.worker_tasks) < 20:
                print(f"[▲ AUTO-SCALE] Queue depth critical ({queue_depth} requests). Deploying new worker pool node...")
                new_worker = asyncio.create_task(self.server_worker(worker_id_counter))
                self.worker_tasks.append(new_worker)
                worker_id_counter += 1

    async def run_swarm(self):
        print(f"[*] Starting engine with {self.current_workers} baseline workers...")
        print(f"[*] Launching stress-test: {self.total_agents} agents flooding the system...")
        
        # Start initial workers
        self.worker_tasks = [asyncio.create_task(self.server_worker(i)) for i in range(self.current_workers)]
        
        # Start the background auto-scaler monitor
        scaler_task = asyncio.create_task(self.auto_scaler_monitor())
        
        # Fire off all agent producers simultaneously
        producers = [self.agent_producer(i) for i in range(self.total_agents)]
        await asyncio.gather(*producers)
        
        # Wait until the queue is completely emptied
        await self.queue.join()
        
        # Clean up background tasks
        scaler_task.cancel()
        for w in self.worker_tasks:
            w.cancel()
            
        self.telemetry.save_telemetry_data()
        self.telemetry.calculate_percentiles()

if __name__ == "__main__":
    # Starts with 5 workers, but will scale up dynamically to survive the 500 agent swarm!
    engine = AgentSimulationEngine(total_agents=500, max_queue_size=100, starting_workers=5)
    asyncio.run(engine.run_swarm())
