# MCP LLMS-TXT Documentation Server

A Model Control Protocol (MCP) server for serving documentation from llms.txt files.

## Installation

```bash
pip install mcpdoc
```

## Usage

### Command-line Interface

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

### Additional Options

- `--follow-redirects`: Follow HTTP redirects (defaults to False)
- `--timeout SECONDS`: HTTP request timeout in seconds (defaults to 10.0)

Example with additional options:

```bash
mcpdoc --yaml sample_config.yaml --follow-redirects --timeout 15
```

This will load the LangGraph Python documentation with a 15-second timeout and follow any HTTP redirects if necessary.

### Configuration Format

Both YAML and JSON configuration files should contain a list of documentation sources. Each source must include an `llms_txt` URL and can optionally include a `name`:

#### YAML Configuration Example (sample_config.yaml)

```yaml
# Sample configuration for mcp-mcpdoc server
# Each entry must have a llms_txt URL and optionally a name
- name: LangGraph Python
  llms_txt: https://langchain-ai.github.io/langgraph/llms.txt
```

#### JSON Configuration Example (sample_config.json)

```json
[
  {
    "name": "LangGraph Python",
    "llms_txt": "https://langchain-ai.github.io/langgraph/llms.txt"
  }
]
```

### Programmatic Usage

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
