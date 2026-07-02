# Agent Chaos Framework
### A framework for studying congestion and fault propagation in asynchronous queue-based systems.

## 📌 Project Concept
The Agent Chaos Framework is a local python-based testbed designed to simulate how backend microservices handle concurrent load spikes, resource constraints, and network instability. 

Instead of hiding application layers behind broad abstractions, this tool orchestrates hundreds of concurrent worker tasks communicating across a single bounded queue layer. This makes it possible to isolate, monitor, and record exactly how systemic failures propagate through an application runtime in real-time.

## 📐 Bounded Queue Stability Model

The system tracks backlog acceleration boundaries using a discrete calculation loop inside the execution engine. Stability balances follow standard fluid queue dynamics:

$$\frac{d(\text{Queue})}{dt} = \lambda(t) - \mu(t)$$

Where $\lambda(t)$ represents the incoming traffic generation rate from independent agents, and $\mu(t)$ represents the active consumer system processing rate.

A **System Collapse State** is flagged by the detector when either of these criteria are met:
1. The queue acceleration derivative $d(\text{Queue})/dt$ remains continuously positive while the buffer saturation exceeds $85\%$.
2. The rolling $p95$ latency calculation gradient surges beyond a $1.0\times$ ($100\%$) growth interval within a single monitoring window.

## 🧱 Software Directory Design

* **`core/`**: Controls asynchronous task lifecycle execution using Python `asyncio` loops. Houses event objects and throttle feedback loops.
* **`fault_model/`**: Contains probabilistic delay matrices that emulate connection degradation and service errors (HTTP 500/503 patterns).
* **`observability/`**: Aggregates streaming metric windows to calculate active tracking statistics (rolling p95, throughput capacity, slope gradients).
* **`experiments/`**: Executes distinct testing setups using parameters supplied by JSON configuration schemas.

## 📊 Scientific Control Validation & Benchmarks
To guarantee the simulator tracks runtime state changes reliably, validation checks were conducted against standard configuration bounds:

| Configuration Matrix | Target Agent Load | Base Worker Allocation | Observed Queue Trajectory | Resulting State Profile |
| :--- | :--- | :--- | :--- | :--- |
| **EXP-001 (Control)** | 80 Agents | 12 Workers | Sustained Empty Buffer ($dK/dt \le 0$) | **STABLE** |
| **EXP-002 (Stress-Test)** | 400 Agents | 4 Workers | Buffer Saturation Peak ($dK/dt > 15.0$) | **COLLAPSED** |

## 🛡️ Framework Limitations & Scope
* **Single-Process Context**: Execution relies entirely on local asynchronous event loops on a single machine; it does not model separate physical distributed hardware over a real network grid.
* **In-Memory Buffer Layer**: Workload messages pass through memory via `asyncio.Queue`, bypassing physical TCP/IP stack simulations or network serialization layers.

## 🚀 Planned Roadmap Iterations
* **OpenTelemetry Specification Integration**: Upgrading the tracking framework to emit structured telemetry payloads directly to external visualization dashboards.
* **Network Emulation Layer**: Introducing artificial socket latency matrices to test how the orchestrator reacts under strict packet drop and jitter profiles.
