import argparse
import json
import sys
from typing import List, Dict

import yaml
import requests  # 추가: HTTP 요청을 위해 requests 모듈 사용

from mcpdoc._version import __version__
from mcpdoc.main import create_server, DocSource
from mcpdoc.splash import SPLASH


class CustomFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    # Custom formatter to preserve epilog formatting while showing default values
    pass


EPILOG = """
Examples:
  # Directly specifying llms.txt URLs with optional names
  mcpdoc --urls LangGraph:https://langchain-ai.github.io/langgraph/llms.txt
  
  # Using a YAML config file
  mcpdoc --yaml sample_config.yaml

  # Using a JSON config file
  mcpdoc --json sample_config.json

  # Combining multiple documentation sources
  mcpdoc --yaml sample_config.yaml --json sample_config.json --urls LangGraph:https://langchain-ai.github.io/langgraph/llms.txt

  # Using SSE transport with default host (127.0.0.1) and port (8000)
  mcpdoc --yaml sample_config.yaml --transport sse
  
  # Using SSE transport with custom host and port
  mcpdoc --yaml sample_config.yaml --transport sse --host 0.0.0.0 --port 9000
  
  # Using SSE transport with additional HTTP options
  mcpdoc --yaml sample_config.yaml --follow-redirects --timeout 15 --transport sse --host localhost --port 8080
"""


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="MCP LLMS-TXT Documentation Server",
        formatter_class=CustomFormatter,
        epilog=EPILOG,
    )

    parser.add_argument(
        "--yaml",
        "-y",
        type=str,
        help="Path or URL to YAML config file with doc sources",
    )
    parser.add_argument(
        "--json",
        "-j",
        type=str,
        help="Path or URL to JSON config file with doc sources",
    )
    parser.add_argument(
        "--urls",
        "-u",
        type=str,
        nargs="+",
        help="List of llms.txt URLs with optional names (format: 'url' or 'name:url')",
    )

    parser.add_argument(
        "--follow-redirects",
        action="store_true",
        help="Whether to follow HTTP redirects",
    )
    parser.add_argument(
        "--timeout", type=float, default=10.0, help="HTTP request timeout in seconds"
    )
    parser.add_argument(
        "--transport",
        type=str,
        default="stdio",
        choices=["stdio", "sse"],
        help="Transport protocol for MCP server",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        help=(
            "Log level for the server. Use one on the following: DEBUG, INFO, "
            "WARNING, ERROR."
            " (only used with --transport sse)"
        ),
    )

    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind the server to (only used with --transport sse)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (only used with --transport sse)",
    )

    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=f"mcpdoc {__version__}",
        help="Show version information and exit",
    )

    return parser.parse_args()


def load_config_file(file_path: str, file_format: str) -> List[Dict[str, str]]:
    """Load configuration from a file or URL.

    Args:
        file_path: Local path or URL to the config file.
        file_format: Format of the config file ("yaml" or "json").

    Returns:
        List of doc source configurations.
    """
    print(f"[DEBUG] Loading config from URL: {file_path}")
    try:
        print(f"[DEBUG] Loading config from URL: {file_path}")
        # URL 감지를 위해 소문자로 변환한 문자열로 비교
        if file_path.lower().startswith("http://") or file_path.lower().startswith(
            "https://"
        ):

            import requests  # 필요한 경우 함수 내부에서 임포트

            response = requests.get(file_path, timeout=10)
            response.raise_for_status()
            content = response.text
            if file_format.lower() == "yaml":
                config = yaml.safe_load(content)
            elif file_format.lower() == "json":
                config = json.loads(content)
            else:
                raise ValueError(f"Unsupported file format: {file_format}")
        else:
            with open(file_path, "r", encoding="utf-8") as file:
                if file_format.lower() == "yaml":
                    config = yaml.safe_load(file)
                elif file_format.lower() == "json":
                    config = json.load(file)
                else:
                    raise ValueError(f"Unsupported file format: {file_format}")

        if not isinstance(config, list):
            raise ValueError("Config file must contain a list of doc sources")

        return config
    except (
        FileNotFoundError,
        yaml.YAMLError,
        json.JSONDecodeError,
        requests.RequestException,
        ValueError,
    ) as e:
        print(f"Error loading config file: {e}", file=sys.stderr)
        sys.exit(1)


def create_doc_sources_from_urls(urls: List[str]) -> List[DocSource]:
    """Create doc sources from a list of URLs with optional names.

    Args:
        urls: List of llms.txt URLs with optional names (format: 'url' or 'name:url').

    Returns:
        List of DocSource objects.
    """
    doc_sources = []
    for entry in urls:
        if not entry.strip():
            continue
        if ":" in entry and not entry.startswith(("http:", "https:")):
            # Format is name:url
            name, url = entry.split(":", 1)
            doc_sources.append({"name": name, "llms_txt": url})
        else:
            # Format is just url
            doc_sources.append({"llms_txt": entry})
    return doc_sources


def main() -> None:
    """Main entry point for the CLI."""
    print(f"Starting MCPDOC server with {len(sys.argv)} arguments")
    if len(sys.argv) == 1:
        help_parser = argparse.ArgumentParser(
            description="MCP LLMS-TXT Documentation Server",
            formatter_class=CustomFormatter,
            epilog=EPILOG,
        )
        help_parser.add_argument(
            "--version",
            "-V",
            action="version",
            version=f"mcpdoc {__version__}",
            help="Show version information and exit",
        )
        help_parser.print_help()
        sys.exit(0)

    args = parse_args()

    doc_sources: List[DocSource] = []

    if not (args.yaml or args.json or args.urls):
        print(
            "Error: At least one source option (--yaml, --json, or --urls) is required",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.yaml:
        doc_sources.extend(load_config_file(args.yaml, "yaml"))
    if args.json:
        doc_sources.extend(load_config_file(args.json, "json"))
    if args.urls:
        doc_sources.extend(create_doc_sources_from_urls(args.urls))

    settings = {
        "host": args.host,
        "port": args.port,
        "log_level": "INFO",
    }

    server = create_server(
        doc_sources,
        follow_redirects=args.follow_redirects,
        timeout=args.timeout,
        settings=settings,
    )

    if args.transport == "sse":
        print()
        print(SPLASH)
        print()

        print(
            f"Launching MCPDOC server with {len(doc_sources)} doc sources",
        )

    server.run(transport=args.transport)


if __name__ == "__main__":
    main()
