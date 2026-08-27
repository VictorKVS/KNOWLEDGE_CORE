# 4-stream launch note

The four deterministic work queues are now registered in-repo:

- S1: SHA 0-3
- S2: SHA 4-7
- S3: SHA 8-b
- S4: SHA c-f

This registration is the control-plane start only. It does not claim background model execution from GitHub by itself. Actual document mastery requires a worker/agent runtime with access to the local source pack for GOST binaries and authoritative web sources for currentness verification.
