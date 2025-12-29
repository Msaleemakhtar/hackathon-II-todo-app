#!/usr/bin/env python3
"""
Export OpenAPI schema to JSON and YAML files.

Usage:
    python scripts/export_openapi.py
    # Or with uv:
    uv run python scripts/export_openapi.py
"""

import json

# Add parent directory to path to import app
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


def export_openapi():
    """Export OpenAPI schema to JSON and YAML."""
    # Get OpenAPI schema
    openapi_schema = app.openapi()

    # Create docs directory if it doesn't exist
    docs_dir = Path(__file__).parent.parent / "docs"
    docs_dir.mkdir(exist_ok=True)

    # Export to JSON
    json_path = docs_dir / "openapi.json"
    with open(json_path, "w") as f:
        json.dump(openapi_schema, f, indent=2)
    print(f"✓ Exported OpenAPI schema to {json_path}")

    # Export to YAML (if pyyaml is available)
    try:
        import yaml

        yaml_path = docs_dir / "openapi.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(openapi_schema, f, default_flow_style=False, sort_keys=False)
        print(f"✓ Exported OpenAPI schema to {yaml_path}")
    except ImportError:
        print("⚠ pyyaml not installed - skipping YAML export")
        print("  Install with: uv add pyyaml")

    # Create API documentation markdown
    md_path = docs_dir / "API.md"
    with open(md_path, "w") as f:
        f.write(generate_api_docs(openapi_schema))
    print(f"✓ Generated API documentation at {md_path}")


def generate_api_docs(schema: dict) -> str:
    """Generate markdown API documentation from OpenAPI schema."""
    md = [
        f"# {schema['info']['title']}",
        "",
        f"**Version**: {schema['info']['version']}",
        "",
        schema['info']['description'],
        "",
        "## Base URL",
        "",
        "```",
        "http://localhost:8000",
        "```",
        "",
        "## Endpoints",
        "",
    ]

    # Group endpoints by tags
    endpoints_by_tag = {}
    for path, methods in schema['paths'].items():
        for method, details in methods.items():
            if method in ['get', 'post', 'put', 'delete', 'patch']:
                tags = details.get('tags', ['Default'])
                for tag in tags:
                    if tag not in endpoints_by_tag:
                        endpoints_by_tag[tag] = []
                    endpoints_by_tag[tag].append({
                        'path': path,
                        'method': method.upper(),
                        'details': details
                    })

    # Generate documentation for each tag
    for tag, endpoints in endpoints_by_tag.items():
        md.append(f"### {tag}")
        md.append("")

        for endpoint in endpoints:
            md.append(f"#### `{endpoint['method']} {endpoint['path']}`")
            md.append("")
            md.append(endpoint['details'].get('summary', 'No description'))
            md.append("")

            # Parameters
            if 'parameters' in endpoint['details']:
                md.append("**Parameters:**")
                md.append("")
                for param in endpoint['details']['parameters']:
                    required = "required" if param.get('required') else "optional"
                    md.append(f"- `{param['name']}` ({param['in']}, {required}): {param.get('description', 'No description')}")
                md.append("")

            # Request body
            if 'requestBody' in endpoint['details']:
                md.append("**Request Body:**")
                md.append("")
                md.append("```json")
                md.append(json.dumps(endpoint['details']['requestBody'], indent=2))
                md.append("```")
                md.append("")

            # Responses
            if 'responses' in endpoint['details']:
                md.append("**Responses:**")
                md.append("")
                for code, response in endpoint['details']['responses'].items():
                    md.append(f"- `{code}`: {response.get('description', 'No description')}")
                md.append("")

            md.append("---")
            md.append("")

    return "\n".join(md)


if __name__ == "__main__":
    export_openapi()
