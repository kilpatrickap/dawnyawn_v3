# DawnYawn Autonomous Agent

This project is a modular autonomous agent named **DawnYawn**. It separates the agent's "brain" (planning and reasoning) from its "hands" (tool execution), mirroring the advanced architecture from the diagram.

This version is configured to use a **local LLM** (like Llama 3.1) served via an OpenAI-compatible API, such as Ollama.

### Architecture Flow

1.  **`main.py`**: The user provides a high-level goal.
2.  **`AgentScheduler`**: Uses the local LLM to break the goal into a series of logical `TaskNode` steps.
3.  **`TaskManager`**: Manages the overall state and executes the tasks in sequence.
4.  **`ThoughtEngine`**: For each task, it uses the LLM to determine *which tool to use* (e.g., `os_command`) and formulates the precise input for that tool.
5.  **`ToolManager`**: Selects the correct tool.
6.  **`OsCommandTool`**: Uses the `MCPClient` to send the command to the external `kali_execution_server`.
7.  The server executes the command in a secure Docker container and returns the result.
8.  The result is summarized by the LLM, added to the task's context, and the `TaskManager` moves to the next step.

### Setup & Usage

You need a local LLM server and two separate terminals.

**1. Run a Local LLM Server (Ollama)**

- Install [Ollama](https://ollama.com/).
- Pull the model: `ollama pull llama3.1:8b`
- The Ollama server will be running in the background at `http://localhost:11434`.

**2. Run the Kali Execution Server (Terminal 1)**

- Follow the instructions in the `kali_execution_server` directory.
- **Crucially, build the Docker image with the correct name**:
  ```bash
  docker build -t dawnyawn-kali-agent .