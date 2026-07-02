# Agent Chaos Framework
### A framework for studying congestion and fault propagation in asynchronous queue-based systems.

## 📌 Project Concept
The Agent Chaos Framework is a python-based testbed designed to simulate how backend microservices handle concurrent load spikes, resource constraints, and network instability. 

Instead of hiding application layers behind broad abstractions, this tool orchestrates hundreds of concurrent worker tasks communicating across a single bounded queue layer. This makes it possible to isolate, monitor, and record exactly how systemic failures propagate through an application runtime in real-time.

## 🧱 Architecture Diagram
