# MCP LLMS-TXT Documentation Server

The MCP LLMS-TXT Documentation Server is a specialized Model Control Protocol (MCP) server that delivers documentation directly from llms.txt files. It serves as a testbed for integrating documentation into IDEs via external **tools**, rather than relying solely on built-in features. While future IDEs may offer robust native support for llms.txt files, this server allows us to experiment with alternative methods, giving us full control over how documentation is retrieved and displayed.

## Usage

### Cursor

1. Install Cursor: https://www.cursor.com/en 
2. Launch the MCP server in **SSE** transport.
 
   ```shell
   uvx --from mcpdoc mcpdoc \
       --urls LangGraph:https://langchain-ai.github.io/langgraph/llms.txt \ 
       --transport sse \
       --port 8081
       --host localhost
   ```

3. Add the mcp server to Cursor. Remember to put the URL as **[host]/sse** for example **http://localhost:8081/sse**.

4. You should be able to use it within composer now.

### Claude Code

1. Install Claude Code: https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview
2. Install [uv](https://github.com/astral-sh/uv). This step is required if you want to run the MCP server in using `uvx` command. This is generally recommended as it'll simplify all the dependency management for you.
3. Configure the MCP server with claude code

    ```shell
    claude mcp add-json langgraph-docs  '{"type":"stdio","command":"uvx" ,"args":["--from", "mcpdoc", "mcpdoc", "--urls", "langgraph:https://langchain-ai.github.io/langgraph/llms.txt"]}' -s user
    ```

4. Launch claude code

    ```shell
    claude code
    ```
   
    Verify that the server is running by typing `/mcp` in the chat window.

   ```
   > /mcp
   ```

5. Test it out! 

   ```
   > Write a langgraph application with two agents that debate the merits of taking a shower.
   ```
 
 
This MCP server was only configured with LangGraph documentation, but you can add more documentation sources by adding more `--urls` arguments or loading it from a JSON file or a YAML file.






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
