# MCP LLMS-TXT Documentation Server

## Overview

[llms.txt](https://llmstxt.org/) is a website index for LLMs, providing background information, guidance, and links to detailed markdown files. IDEs like Cursor and Windsurf or apps like Claude Code/Desktop can use `llms.txt` to retrieve context for tasks. However, these apps use different built-in tools to read and process files like `llms.txt`. The retrieval process can be opaque, and there is not always a way to audit the tool calls or the context returned.

[MCP](https://github.com/modelcontextprotocol) offers a way for developers to have *full control* over tools used by these applications. Here, we create [an open source MCP server](https://github.com/modelcontextprotocol) to provide MCP host applications (e.g., Cursor, Windsurf, Claude Code/Desktop) with (1) a user-defined list of `llms.txt` files and (2) a simple  `fetch_docs` tool read URLs within any of the provided `llms.txt` files. This allows the user to audit each tool call as well as the context returned. 

![mcpdoc](https://github.com/user-attachments/assets/736f8f55-833d-4200-b833-5fca01a09e1b)

## Quickstart

#### Install uv
* Please see [official uv docs](https://docs.astral.sh/uv/getting-started/installation/#installation-methods) for other ways to install `uv`.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Choose an `llms.txt` file to use. 
* For example, [here's](https://langchain-ai.github.io/langgraph/llms.txt) the LangGraph `llms.txt` file.

#### (Optional) Test the MCP server locally with your `llms.txt` file of choice:
```bash
uvx --from mcpdoc mcpdoc \
    --urls LangGraph:https://langchain-ai.github.io/langgraph/llms.txt \
    --transport sse \
    --port 8082 \
    --host localhost
```

* This should run at: http://localhost:8082

![Screenshot 2025-03-18 at 3 29 30 PM](https://github.com/user-attachments/assets/24a3d483-cd7a-4c7e-a4f7-893df70e888f)

* Run [MCP inspector](https://modelcontextprotocol.io/docs/tools/inspector) and connect to the running server:
```bash
npx @modelcontextprotocol/inspector
```

![Screenshot 2025-03-18 at 3 30 30 PM](https://github.com/user-attachments/assets/14645d57-1b52-4a5e-abfe-8e7756772704)

* Here, you can test the `tool` calls. 

#### Connect to Cursor 

* Open `Cursor Settings` and `MCP` tab.
* This will open the `~/.cursor/mcp.json` file.

![Screenshot 2025-03-19 at 11 01 31 AM](https://github.com/user-attachments/assets/3d1c8eb3-4d40-487f-8bad-3f9e660f770a)

* Paste the following into the file (we use the `langgraph-docs-mcp` name and link to the LangGraph `llms.txt`).

```
{
  "mcpServers": {
    "langgraph-docs-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "mcpdoc",
        "mcpdoc",
        "--urls",
        "LangGraph:https://langchain-ai.github.io/langgraph/llms.txt",
        "--transport",
        "stdio",
        "--port",
        "8081",
        "--host",
        "localhost"
      ]
    }
  }
}
```

* Confirm that the server is running in your `Cursor Settings/MCP` tab.
* `CMD+L` (on Mac) to open chat.
* Ensure `agent` is selected. 

![Screenshot 2025-03-18 at 1 56 54 PM](https://github.com/user-attachments/assets/0dd747d0-7ec0-43d2-b6ef-cdcf5a2a30bf)

Then, try an example prompt, such as:
```
use the langgraph-docs-mcp server to answer any LangGraph questions -- 
+ call list_doc_sources tool to get the available llms.txt file
+ call fetch_docs tool to read it
+ reflect on the urls in llms.txt 
+ reflect on the input question 
+ call fetch_docs on any urls relevant to the question
+ use this to answer the question

what are types of memory in LangGraph?
```

![Screenshot 2025-03-18 at 1 58 38 PM](https://github.com/user-attachments/assets/180966b5-ab03-4b78-8b5d-bab43f5954ed)

### Connect to Windsurf

* Open Cascade with `CMD+L` (on Mac).
* Click `Configure MCP` to open the config file, `~/.codeium/windsurf/mcp_config.json`.
* Update with `langgraph-docs-mcp` as noted above.

![Screenshot 2025-03-19 at 11 02 52 AM](https://github.com/user-attachments/assets/d45b427c-1c1e-4602-820a-7161a310af24)

* `CMD+L` (on Mac) to open Cascade and refresh MCP servers.
* Available MCP servers will be listed, showing `langgraph-docs-mcp` as connected.

![Screenshot 2025-03-18 at 2 02 12 PM](https://github.com/user-attachments/assets/5a29bd6a-ad9a-4c4a-a4d5-262c914c5276)

Then, try the example prompt:
* It will perform your tool calls.

![Screenshot 2025-03-18 at 2 03 07 PM](https://github.com/user-attachments/assets/0e24e1b2-dc94-4153-b4fa-495fd768125b)

### Connect to Claude Desktop

* Open `Settings/Developer` to update `~/Library/Application\ Support/Claude/claude_desktop_config.json`.
* Update with `langgraph-docs-mcp` as noted above.
* Restart Claude Desktop app.

![Screenshot 2025-03-18 at 2 05 54 PM](https://github.com/user-attachments/assets/228d96b6-8fb3-4385-8399-3e42fa08b128)

* You will see your tools visible in the bottom right of your chat input.

![Screenshot 2025-03-18 at 2 05 39 PM](https://github.com/user-attachments/assets/71f3c507-91b2-4fa7-9bd1-ac9cbed73cfb)

Then, try the example prompt:

* It will ask to approve tool calls as it processes your request.

![Screenshot 2025-03-18 at 2 06 54 PM](https://github.com/user-attachments/assets/59b3a010-94fa-4a4d-b650-5cd449afeec0)

### Connect to Claude Code

* In a terminal after installing [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview), run this command to add the MCP server to your project:
```
claude mcp add-json langgraph-docs '{"type":"stdio","command":"uvx" ,"args":["--from", "mcpdoc", "mcpdoc", "--urls", "langgraph:https://langchain-ai.github.io/langgraph/llms.txt"]}' -s local
```
* You will see `~/.claude.json` updated.
* Test by launching Claude Code and running to view your tools:
```
$ Claude
$ /mcp 
```

![Screenshot 2025-03-18 at 2 13 49 PM](https://github.com/user-attachments/assets/eb876a0e-27b4-480e-8c37-0f683f878616)

Then, try the example prompt:

* It will ask to approve tool calls.

![Screenshot 2025-03-18 at 2 14 37 PM](https://github.com/user-attachments/assets/5b9a2938-ea69-4443-8d3b-09061faccad0)

## Command-line Interface

The `mcpdoc` command provides a simple CLI for launching the documentation server. 

You can specify documentation sources in three ways, and these can be combined:

1. Using a YAML config file:

* This will load the LangGraph Python documentation from the `sample_config.yaml` file in this repo.

```bash
mcpdoc --yaml sample_config.yaml
```

2. Using a JSON config file:

* This will load the LangGraph Python documentation from the `sample_config.json` file in this repo.

```bash
mcpdoc --json sample_config.json
```

3. Directly specifying llms.txt URLs with optional names:

* URLs can be specified either as plain URLs or with optional names using the format `name:url`.
* This is how we loaded `llms.txt` for the MCP server above.

```bash
mcpdoc --urls LangGraph:https://langchain-ai.github.io/langgraph/llms.txt
```

You can also combine these methods to merge documentation sources:

```bash
mcpdoc --yaml sample_config.yaml --json sample_config.json --urls https://langchain-ai.github.io/langgraph/llms.txt
```

## Additional Options

- `--follow-redirects`: Follow HTTP redirects (defaults to False)
- `--timeout SECONDS`: HTTP request timeout in seconds (defaults to 10.0)

Example with additional options:

```bash
mcpdoc --yaml sample_config.yaml --follow-redirects --timeout 15
```

This will load the LangGraph Python documentation with a 15-second timeout and follow any HTTP redirects if necessary.

## Configuration Format

Both YAML and JSON configuration files should contain a list of documentation sources. 

Each source must include an `llms_txt` URL and can optionally include a `name`:

### YAML Configuration Example (sample_config.yaml)

```yaml
# Sample configuration for mcp-mcpdoc server
# Each entry must have a llms_txt URL and optionally a name
- name: LangGraph Python
  llms_txt: https://langchain-ai.github.io/langgraph/llms.txt
```

### JSON Configuration Example (sample_config.json)

```json
[
  {
    "name": "LangGraph Python",
    "llms_txt": "https://langchain-ai.github.io/langgraph/llms.txt"
  }
]
```

## Programmatic Usage

```python
from mcpdoc.main import create_server

# Create a server with documentation sources
server = create_server(
    [
        {
            "name": "LangGraph Python",
            "llms_txt": "https://langchain-ai.github.io/langgraph/llms.txt",
        },
        # You can add multiple documentation sources
        # {
        #     "name": "Another Documentation",
        #     "llms_txt": "https://example.com/llms.txt",
        # },
    ],
    follow_redirects=True,
    timeout=15.0,
)

# Run the server
server.run(transport="stdio")
```
