# NATS Subject Hierarchy for AP2 Swarm Architecture

This document defines the NATS subject hierarchy for communication between the different agent swarms in the AP2 ecosystem. A consistent and well-defined subject hierarchy is crucial for scalability, maintainability, and observability of the system.

## 1. Base Structure

The proposed structure follows a dot-separated convention, which allows for flexible and hierarchical organization.

**General Pattern:**
`ap2.swarms.<swarm_name>.<message_type>.<context>`

- `ap2.swarms`: A constant prefix to namespace all swarm-related communication.
- `<swarm_name>`: The name of the target or source swarm (e.g., `investigation`, `analysis`).
- `<message_type>`: The nature of the message. This can be one of:
    - `requests`: For command-like, point-to-point, or RPC-style interactions.
    - `responses`: For replies to `requests`.
    - `events`: For asynchronous, one-to-many notifications (publish-subscribe).
    - `telemetry`: For operational metrics and health status.
- `<context>`: A specific, hierarchical description of the message's content or purpose.

---

## 2. Swarm Names

The following swarm names are defined based on the proposed architecture:

- `investigation`
- `detection`
- `analysis`
- `dimensioning`
- `recommendation`
- `lead_management`
- `feedback`
- `artifact_service` (for interacting with the artifact storage)

---

## 3. Message Types and Context Examples

### 3.1. Requests & Responses (RPC-style)

Requests are used when one swarm needs another to perform a specific task and expects a direct response. The response subject should include a unique reply-to identifier.

- **Pattern:**
    - Request: `ap2.swarms.<target_swarm>.requests.<task_name>`
    - Response: The `reply-to` field in the NATS message header will be used for the response.

- **Example: Requesting a solar viability analysis.**
    1. **Requester** (e.g., `investigation` swarm) sends a message:
        - **Subject:** `ap2.swarms.dimensioning.requests.compute_viability`
        - **Reply-To:** `ap2.swarms.investigation.responses.cb-12345` (a unique subject for the callback)
        - **Payload:** `{ "contractId": "xyz-abc", "location": { ... }, ... }`

    2. **Responder** (`dimensioning` swarm) processes the request and sends the result to the reply-to subject:
        - **Subject:** `ap2.swarms.investigation.responses.cb-12345`
        - **Payload:** `{ "contractId": "xyz-abc", "status": "success", "results": { ... } }`

### 3.2. Events (Publish-Subscribe)

Events are used for broadcasting state changes or significant occurrences to any interested listeners without knowledge of who they are.

- **Pattern:** `ap2.swarms.<source_swarm>.events.<domain>.<event_name>`

- **Example: A new high-potential lead is identified.**
    - The `analysis` swarm publishes an event after processing data.
    - **Subject:** `ap2.swarms.analysis.events.leads.high_potential_identified`
    - **Payload:** `{ "contractId": "xyz-abc", "customer_id": "cust-789", "potential_score": 0.92 }`
    - The `lead_management` swarm would be subscribed to `ap2.swarms.analysis.events.leads.*` to receive this notification and act on it.

- **Example: An artifact is created.**
    - The `artifact_service` publishes an event after a new contract is saved.
    - **Subject:** `ap2.swarms.artifact_service.events.contracts.created`
    - **Payload:** `{ "contractId": "xyz-abc", "timestamp": "..." }`

### 3.3. Telemetry

Telemetry subjects are used for monitoring, logging, and operational insights.

- **Pattern:** `ap2.swarms.<source_swarm>.telemetry.<metric_type>`

- **Example: Reporting task execution time.**
    - The `dimensioning` swarm publishes its performance metrics.
    - **Subject:** `ap2.swarms.dimensioning.telemetry.performance`
    - **Payload:** `{ "task": "compute_viability", "duration_ms": 1540, "success": true, "contractId": "xyz-abc" }`

- **Example: Reporting health status.**
    - Any swarm can publish a heartbeat to indicate it's alive.
    - **Subject:** `ap2.swarms.analysis.telemetry.heartbeat`
    - **Payload:** `{ "status": "healthy", "timestamp": "...", "active_tasks": 5 }`

---

## 4. Wildcard Subscriptions

This hierarchy allows for powerful use of wildcards for subscriptions:

- `ap2.swarms.*.events.leads.high_potential_identified`: Listen for high-potential leads from **any** swarm.
- `ap2.swarms.analysis.events.leads.*`: Listen for **all** lead-related events from the `analysis` swarm.
- `ap2.swarms.dimensioning.requests.*`: A monitoring tool could subscribe to all requests sent to the `dimensioning` swarm.
- `ap2.swarms.*.telemetry.performance`: Aggregate performance metrics from **all** swarms.

This structure provides a robust foundation for the complex, asynchronous communication required by the proposed swarm architecture.
