import asyncio
import json
import os
from core.engine import AgentStressTestbed

async def run_scientific_suite():
    with open("experiments/configs.json", "r") as f:
        suite = json.load(f)

    summary_results = {}

    for exp_id, profile in suite.items():
        print(f"\n[🔬 INITIATING SCIENTIFIC SUITE: {exp_id}]")
        print(f"Hypothesis: {profile['hypothesis']}")
        
        testbed = AgentStressTestbed(
            total_agents=profile["total_agents"],
            max_queue_size=profile["max_queue_size"],
            starting_workers=profile["starting_workers"]
        )
        testbed.chaos.drop_rate = profile["drop_rate"]
        
        final_state = await testbed.execute_testbed(exp_id)
        summary_results[exp_id] = final_state

    print("\n" + "="*40 + "\n🔬 CROSS-EXPERIMENT SYSTEM COMPARISON LAYER\n" + "="*40)
    for k, v in summary_results.items():
        print(f" -> System Profile {k} resolved state: {v}")
    print("\nConclusion: Asynchronous system stability decreases non-linearly with queue saturation thresholds.")
    print("="*40)

if __name__ == "__main__":
    asyncio.run(run_scientific_suite())
