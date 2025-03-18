#!/usr/bin/env python3
"""Command-line interface for mcp-llms-txt server."""

import argparse
import json
import sys
from typing import List, Dict

import yaml

from mcpdoc.main import create_server, DocSource


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="MCP LLMS-TXT Documentation Server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Allow combining multiple doc source methods
    parser.add_argument(
        "--yaml", "-y", type=str, help="Path to YAML config file with doc sources"
    )
    parser.add_argument(
        "--json", "-j", type=str, help="Path to JSON config file with doc sources"
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
        choices=["stdio", "http", "websocket"],
        help="Transport protocol for MCP server",
    )

    return parser.parse_args()


def load_config_file(file_path: str, file_format: str) -> List[Dict[str, str]]:
    """Load configuration from a file.

    Args:
        file_path: Path to the config file
        file_format: Format of the config file ("yaml" or "json")

    Returns:
        List of doc source configurations
    """
    try:
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
    except (FileNotFoundError, yaml.YAMLError, json.JSONDecodeError) as e:
        print(f"Error loading config file: {e}", file=sys.stderr)
        sys.exit(1)


def create_doc_sources_from_urls(urls: List[str]) -> List[DocSource]:
    """Create doc sources from a list of URLs with optional names.

    Args:
        urls: List of llms.txt URLs with optional names (format: 'url' or 'name:url')

    Returns:
        List of DocSource objects
    """
    doc_sources = []
    for entry in urls:
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
    args = parse_args()

    # Load doc sources based on command-line arguments
    doc_sources: List[DocSource] = []

    # Check if any source options were provided
    if not (args.yaml or args.json or args.urls):
        print(
            "Error: At least one source option (--yaml, --json, or --urls) is required",
            file=sys.stderr,
        )
        sys.exit(1)

    # Merge doc sources from all provided methods
    if args.yaml:
        doc_sources.extend(load_config_file(args.yaml, "yaml"))
    if args.json:
        doc_sources.extend(load_config_file(args.json, "json"))
    if args.urls:
        doc_sources.extend(create_doc_sources_from_urls(args.urls))

    # Create and run the server
    server = create_server(
        doc_sources,
        follow_redirects=args.follow_redirects,
        timeout=args.timeout,
    )

    print(
        f"Starting MCP LLMS-TXT server with {len(doc_sources)} doc sources",
        file=sys.stderr,
    )
    server.run(transport=args.transport)


if __name__ == "__main__":
    main()
