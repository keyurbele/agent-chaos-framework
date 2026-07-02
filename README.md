# Agent Chaos Framework: Distributed Systems Simulation Engine

## 📌 Project Overview
The **Agent Chaos Framework** is a terminal-based systems architecture and network resilience tool designed to stress-test backend infrastructures. Instead of testing basic consumer frontend applications, this framework models high-concurrency environments by orchestrating 500+ simultaneous AI agent nodes competing for a bounded shared queue resource.

By integrating a specialized "Chaos Monkey" fault-injection layer, the engine simulates emergent system behaviors, network degradation patterns, and structural bottlenecks to analyze how and when distributed systems collapse.

---

## 🛠️ System Architecture
The framework is engineered across three decoupled modules to mirror industrial-grade testing pipelines:

* **`engine.py` (The Concurrency Orchestrator):** Manages asynchronous task lifecycles using Python's `asyncio` routines. It utilizes a producer-consumer model via an `asyncio.Queue` bottleneck to create real resource contention without crashing local hardware threads.
* **`chaos.py` (The Fault Injector):** Intercepts active execution timelines to probablistically introduce network latency spikes, packet drops, and internal server faults (HTTP 500/503 errors).
* **`telemetry.py` (The Metrics Parser):** Tracks timestamp data, real-time queue depth, and logs performance metrics. It runs mathematical distributions to calculate exact $p50$, $p95$, and $p99$ latency metrics.
