# Uumpa AI - OpenCode Agent

## Local Development Workflow

```
AGENT_USER_ID=$(uai logbook create-agent-user)

uai logbook create-agent-task opencode cli '{"prompt":"Do something..."}' --agent-user-id $AGENT_USER &&\
uai agents handle-next-task $AGENT_USER_ID
```
