# MCP LLMS-TXT Documentation Server

## Overview

[llms.txt](https://llmstxt.org/) is an index of website contents for LLMs. As an example, [LangGraph's llms.txt](https://langchain-ai.github.io/langgraph/llms.txt) provides a list of LangGraph doc URLs with descriptions. An LLM can use this file to decide which docs to read when accomplishing tasks, which pairs well with IDE agents like Cursor and Windsurf or apps like Claude Code/Desktop.

However, these apps use different built-in tools to read and process files like `llms.txt`; sometimes IDEs will reflect on the `llms.txt` file and use it for formulate *web search queries* rather than just retrieving the URLs listed! More broadly, there can be poor visibility into what apps are doing with their built-in retrieval / search tools.

[MCP](https://github.com/modelcontextprotocol) offers a way for developers to define tools that give *full control* over how context is retrieved and displayed to LLMs in these apps. Here, we create [a simple MCP server](https://github.com/modelcontextprotocol) that defines a few **tools** that these apps can use, such as a `list_doc_sources` to load any `llms.txt` you provide and a `fetch_docs` tool read any URLs within `llms.txt`. This simple MCP server has two benefits: (1) it allows the user to customize context retrieval and (2) it allows the user to audit each tool call as well as the context returned. 

![Screenshot 2025-03-18 at 12 55 51 PM](https://github.com/user-attachments/assets/a7440c71-6cbc-472e-9243-3bfc371bb173)

## Quickstart

Install uv:
* Please see [official uv docs](https://docs.astral.sh/uv/getting-started/installation/#installation-methods) for other ways to install `uv`.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Select an `llms.txt` file to use. 
* For example, [here's](https://langchain-ai.github.io/langgraph/llms.txt) the LangGraph `llms.txt` file.

Run the MCP server locally with your `llms.txt` file of choice:
```bash
uvx --from mcpdoc mcpdoc \
    --urls LangGraph:https://langchain-ai.github.io/langgraph/llms.txt \
    --transport sse \
    --port 8082 \
    --host localhost
```

* This should run at: http://localhost:8082

![Screenshot 2025-03-18 at 3 29 30 PM](https://github.com/user-attachments/assets/24a3d483-cd7a-4c7e-a4f7-893df70e888f)

Run [MCP inspector](https://modelcontextprotocol.io/docs/tools/inspector) and connect to the running server:
```bash
npx @modelcontextprotocol/inspector
```

![Screenshot 2025-03-18 at 3 30 30 PM](https://github.com/user-attachments/assets/14645d57-1b52-4a5e-abfe-8e7756772704)

Here, you can test the `tool` calls. 

Finally, add the server to any MCP host applications of interest.

Below, we walk through each one, but here are the the config files that are updated for each:

```
*Cursor*
`~/.cursor/mcp.json` 

*Windsurf*
`~/.codeium/windsurf/mcp_config.json`
 
*Claude Desktop*
`~/Library/Application\ Support/Claude/claude_desktop_config.json`
 
*Claude Code*
`~/.claude.json`
```

These will be updated with our server, as shown below.

> NOTE: It appears that `stdio` transport is required for Windsurf and Cursor.

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

## Usage

### Cursor 

Setup:
* `Settings -> MCP` to add a server.
* Update `~/.cursor/mcp.json` with `langgraph-docs-mcp` as noted above.
* `Settings -> MCP` to confirm that the server is connected.
* `Control-L` to open chat.
* Ensure `agent` is selected. 

![Screenshot 2025-03-18 at 1 56 54 PM](https://github.com/user-attachments/assets/0dd747d0-7ec0-43d2-b6ef-cdcf5a2a30bf)

Then, try an example prompt:
```
use the langgraph-docs-mcp server to answer any LangGraph questions -- 
+ call get_docs tool to get the available llms.txt file
+ call fetch_docs tool to read it
+ reflect on the urls in llms.txt 
+ reflect on the input question 
+ call fetch_docs on any urls relevant to the question
+ use this to answer the question

what are types of memory in LangGraph?
```

* It will ask to approve tool calls as it processes your question.

![Screenshot 2025-03-18 at 1 58 38 PM](https://github.com/user-attachments/assets/180966b5-ab03-4b78-8b5d-bab43f5954ed)

* Consider adding some of these instructions to [Cursor Rules](https://docs.cursor.com/context/rules-for-ai).

### Windsurf

Setup:
* `Control-L` to open Cascade and click `Configure MCP` to open the config file.
* Update `~/.codeium/windsurf/mcp_config.json` with `langgraph-docs-mcp` as noted above.
* `Control-L` to open Cascade and refresh MCP servers.
* Available MCP servers will be listed, showing `langgraph-docs-mcp` as connected.

![Screenshot 2025-03-18 at 2 02 12 PM](https://github.com/user-attachments/assets/5a29bd6a-ad9a-4c4a-a4d5-262c914c5276)

Then, try the example prompt:
* It will perform your tool calls.

![Screenshot 2025-03-18 at 2 03 07 PM](https://github.com/user-attachments/assets/0e24e1b2-dc94-4153-b4fa-495fd768125b)

### Claude Desktop

Setup:
* Open `Settings -> Developer` to update `~/Library/Application\ Support/Claude/claude_desktop_config.json`.
* Restart Claude.

![Screenshot 2025-03-18 at 2 05 54 PM](https://github.com/user-attachments/assets/228d96b6-8fb3-4385-8399-3e42fa08b128)

* You will see your tools visible in the bottom right of your chat input.

![Screenshot 2025-03-18 at 2 05 39 PM](https://github.com/user-attachments/assets/71f3c507-91b2-4fa7-9bd1-ac9cbed73cfb)

Then, try the example prompt:

* It will ask to approve tool calls as it processes your request.

![Screenshot 2025-03-18 at 2 06 54 PM](https://github.com/user-attachments/assets/59b3a010-94fa-4a4d-b650-5cd449afeec0)

### Claude Code

Setup:
* In a terminal after installing [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview), run to add the MCP server to your project:
```
claude mcp add-json langgraph-docs '{"type":"stdio","command":"uvx" ,"args":["--from", "mcpdoc", "mcpdoc", "--urls", "langgraph:https://langchain-ai.github.io/langgraph/llms.txt"]}' -s project
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

The `mcpdoc` command provides a simple CLI for launching the documentation server. You can specify documentation sources in three ways, and these can be combined:

1. Using a YAML config file:

```bash
mcpdoc --yaml sample_config.yaml
```

This will load the LangGraph Python documentation from the sample_config.yaml file.

2. Using a JSON config file:

```bash
mcpdoc --json sample_config.json
```

This will load the LangGraph Python documentation from the sample_config.json file.

3. Directly specifying llms.txt URLs with optional names:

```bash
mcpdoc --urls https://langchain-ai.github.io/langgraph/llms.txt LangGraph:https://langchain-ai.github.io/langgraph/llms.txt
```

URLs can be specified either as plain URLs or with optional names using the format `name:url`.

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

Both YAML and JSON configuration files should contain a list of documentation sources. Each source must include an `llms_txt` URL and can optionally include a `name`:

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
