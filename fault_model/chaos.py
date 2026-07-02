import asyncio
import random

class FaultInjector:
    def __init__(self, drop_rate: float, latency_spike: float):
        self.drop_rate = drop_rate          
        self.latency_spike = latency_spike  

    async def apply_fault_models(self) -> int:
        if random.random() < 0.30: 
            await asyncio.sleep(self.latency_spike)
        else:
            await asyncio.sleep(0.02) 
            
        if random.random() < self.drop_rate:
            return 500 
            
        return 200
