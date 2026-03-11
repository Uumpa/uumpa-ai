# Uumpa AI

Agents orchestration framework.

## Architecture

### Entrypoints

Interaction points between the orchestrator and the end user. There could be different kinds of entrypoints, for example:
 
* Chat apps like Zulip/Slack
* API / MCP calls from other systems
* scheduled tasks
* tasks that should be initiated by an agent - the entrypoint will check when an interaction should occur
* Secure entrypoint for direct communication without AI - for security confirmations.
* Issues / pull request - get requests from webhook from issue / comments

The entrypoints handle all the logic relating to communication with the outside world.

### Orchestrator

* Manages task lifecycle, policy, approvals, and routing.
* Does not involve LLM / AI.
* Manages security / approvals.
* Uses secure entrypoints for security approvals or sensitive data which does not reach the AI agents.
* Creates tasks in the log book and starts agents to handle them.
* Creates log book users for the task agents.

### Router

* Routes tasks to agents based on task type, agent capabilities, and policies.

### Log Book

The log book stores all state, keeps track of tasks progress, stores artifacts, keeps all memory for the agents and orchestrator.

* Task management - each task has a related task in the log book, updates are saved to the task, status is updated
* Knowledgebase - stores memories / documentation
* Code - Git repositories containing code the agents work on
* Users - humans have their users, orchestrator can create and assign users to agents

### Agents

* Agent instance assigned to a task.
* Usually handled by LLM but not required.
* Agents only communicate with the orchestrator or the log book via their assigned user.
* Agent implementation and tools assumed to be handled by existing agents like Opencode / Claude

### Tools

It's preferred that most tools will be defined in the agent, but tools that require permissions or interaction with the orchestrator will be defined here.

### Catalog

Repository of items like agent types, entrypoints, tools. catalog tool allows agents to find items in the catalog.
