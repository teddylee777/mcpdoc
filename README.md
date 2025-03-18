# MCP LLMS-TXT Documentation Server

## Overview

[llms.txt](https://llmstxt.org/) is a standard index of website contents to help LLMs. As an example, [LangGraph's llms.txt](https://langchain-ai.github.io/langgraph/llms.txt) provides a curated list of LangGraph doc URLs with a short description of each one. An LLM can use this file to decide which pages to read when accomplishing tasks, and pairs well with IDEs like Cursor and Windsurf or applications like Claude Code/Desktop.

However, these applications use different built-in tools to read and process files like `llms.txt`; sometimes IDEs will reflect on the `llms.txt` file and use it for formulate *web search queries* rather than retrieving the specific URLs listed! More broadly, there can be poor visibility into what applications are doing with their built-in retrieval / search tools.

[MCP](https://github.com/modelcontextprotocol) offers a way for developers to define tools that give us *full control* over how documentation is retrieved and displayed to LLMs in these applications. Here, we create [a simple MCP server](https://github.com/modelcontextprotocol) that defines a few basical external **tools** that these applications can use: 1) to tool to load `llms.txt` and 2) fetch specific URLs within `llms.txt`. When these tools are used, the user can customize retrieval and audit the tool calls / the context returned to better understand what is happening under the hood. 

![Screenshot 2025-03-18 at 12 55 51 PM](https://github.com/user-attachments/assets/a7440c71-6cbc-472e-9243-3bfc371bb173)

## Quickstart

Create a virtual environment and install uv:
```bash
python3 -m venv venv
source .venv/bin/activate
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install the package:
```bash
uv pip install mcpdoc
```

Select an `llms.txt` file to use. For example, here's the LangGraph `llms.txt` 
```bash
https://langchain-ai.github.io/langgraph/llms.txt  
```

Run the MCP server locally with whatever `llms.txt` file you want to use:
```bash
uvx --from mcpdoc mcpdoc \
    --urls LangGraph:https://langchain-ai.github.io/langgraph/llms.txt \
    --transport sse \
    --port 8081 \
    --host localhost
```

Run MCP inspector and connect to the running server via SSE at http://localhost:8081/sse:
```bash
npx @modelcontextprotocol/inspector
```

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

These will be updated with our server specification, as shown below.

> NOTE: It appears that `stdio` transport required for Windsurf and Cursor.

```
{
  "mcpServers": {
    "langgraph-docs-mcp": {
      "command": "/Users/rlm/.local/bin/uvx",
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
* Ensure `~/.cursor/mcp.json` is updated to include the server.
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

* It will ask to approve tool calls.

![Screenshot 2025-03-18 at 1 58 38 PM](https://github.com/user-attachments/assets/180966b5-ab03-4b78-8b5d-bab43f5954ed)

### Windsurf

Setup:
* Ensure `~/.codeium/windsurf/mcp_config.json` is updated to include the server.
* `Control-L` to open Cascade.
* Available MCP servers will be listed. 

![Screenshot 2025-03-18 at 2 02 12 PM](https://github.com/user-attachments/assets/5a29bd6a-ad9a-4c4a-a4d5-262c914c5276)

Then, try the example prompt:
* It will perform your tool calls.

![Screenshot 2025-03-18 at 2 03 07 PM](https://github.com/user-attachments/assets/0e24e1b2-dc94-4153-b4fa-495fd768125b)

### Claude Desktop

Setup:
* Open `Settings -> Developer` to update the config.
* Restart Claude.

![Screenshot 2025-03-18 at 2 05 54 PM](https://github.com/user-attachments/assets/228d96b6-8fb3-4385-8399-3e42fa08b128)

* You will see your tools.

![Screenshot 2025-03-18 at 2 05 39 PM](https://github.com/user-attachments/assets/71f3c507-91b2-4fa7-9bd1-ac9cbed73cfb)

Then, try the example prompt:

* It will ask to approve tool calls.

![Screenshot 2025-03-18 at 2 06 54 PM](https://github.com/user-attachments/assets/59b3a010-94fa-4a4d-b650-5cd449afeec0)

### Claude Code

Setup:
* Shortcut to add the MCP server to your project:
```
claude mcp add-json langgraph-docs '{"type":"stdio","command":"uvx" ,"args":["--from", "mcpdoc", "mcpdoc", "--urls", "langgraph:https://langchain-ai.github.io/langgraph/llms.txt"]}' -s project
```
* Test
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
