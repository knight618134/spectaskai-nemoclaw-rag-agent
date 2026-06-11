# Router Demo Spec

## GNSS

GNSS is an optional timing source for the demo radio unit. When enabled, the system should report lock state, holdover state, and timing source priority.

## Timing

PTP is the primary timing source. If PTP quality degrades and GNSS is locked, the recovery agent may recommend switching timing priority after human approval.

## Alarm Handling

Critical timing alarms must include the impacted node, current timing source, packet loss, latency, and the last configuration change.

## Recovery

Recovery actions should be reversible. The agent should run in dry-run mode first, request approval, and record the final action in the incident report.
