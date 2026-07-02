# Agent Chaos Framework
### A testing tool for exploring congestion and fault propagation in asynchronous queue-based systems.

Modern distributed backends and AI agent swarms frequently experience highly variable load spikes. This framework explores how single-host asynchronous architectures behave as workload generation approaches or exceeds queue processing capacity.

## 🧱 Architectural Topology

[Workload Generator (Agents)]
│
▼
[Async Queue] <─── (Backpressure Feedback Loop)
│
▼
[Worker Pool]
│
▼
[Fault Injector]
│
▼
[Event Stream]
│
▼
[Telemetry Engine]
│
▼
[Collapse Detector] ─── (Triggers Throttle)
│
▼
[Final Experiment Report]


## 📁 Repository Structure
* **`core/`**: Manages event types and controls asynchronous execution loops via `asyncio`.
* **`fault_model/`**: Houses pseudo-random fault injection routines simulating service degradation.
* **`observability/`**: Processes streaming metrics to evaluate p95 latency anomalies and compute queue derivatives.
* **`experiments/`**: Script runner that executes reproducible scenarios based on JSON profiles.

## 📐 Conceptual Stability Model
The framework models execution boundaries using traditional fluid queue dynamics:

$$\frac{d(\text{Queue})}{dt} = \lambda(t) - \mu(t)$$

Where $\lambda(t)$ represents the incoming traffic arrival rate from independent agents, and $\mu(t)$ represents the worker processing rate. 

The background detector flags an unstable state when the monitored parameters meet specific limits:
1. The queue growth derivative $d(\text{Queue})/dt$ stays continuously positive as buffer saturation passes $85\%$.
2. The rolling $p95$ latency calculations cross a $1.0\times$ ($100\%$) growth interval within a single monitoring window.

## 📊 Recorded Validation Benchmarks
The platform was evaluated across three baseline profiles using fixed random seeds to ensure exact reproducibility across multiple runs.

| Scenario Profile | Simulated Agents | Base Workers | Bounded Buffer Size | Observed Avg Latency | Observed p95 Latency | Error Rate | Resolved System State |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EXP-001 (Control)** | 80 | 12 | 200 | 0.012s | 0.015s | 0.00% | **STABLE** |
| **EXP-002 (Congestion)** | 400 | 4 | 80 | 0.145s | 0.284s | 14.20% | **DEGRADED** |
| **EXP-003 (Saturation)** | 1000 | 2 | 50 | 0.412s | 0.892s | 42.65% | **COLLAPSED** |

*Analysis Summary:* The recorded test runs suggest that application degradation is non-linear. When queue saturation passes a critical threshold, the feedback loop between queuing latency and pressure-driven faults accelerates structural collapse.

## 🛡️ Assumptions & Limitations
* **Single-Host Context**: The runtime maps operations on a single host event loop; it does not emulate network splits, clock drift, or distributed RPC consensus across independent hardware.
* **In-Memory Buffering**: Tasks traverse memory boundaries using an `asyncio.Queue` block, bypassing physical device serialization or hardware socket layer stacks.
* **Workload Modeling**: Ingestion behaviors assume cooperative client workloads generating tasks independently rather than modeling adversarial network conditions.

## 🚀 Future Work
* **OpenTelemetry Exporting**: Integrating telemetry exporters to pipeline structured tracking events to external monitoring platforms.
* **Network Emulation**: Introducing artificial network jitter, socket timeout drops, and connection pool exhaustion states.

## 📚 References
* Python `asyncio` Concurrency Documentation
* Fluid Flow Models & Basic Queueing Theory Relationships
* Google Site Reliability Engineering Handbook (Congestion Mitigation Patterns)

## 📄 License
This project is licensed under the MIT License.
