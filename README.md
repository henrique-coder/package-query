# package-query

Query the latest package versions from **PyPI**, **npm**, **crates.io**, **Docker Hub**, and **GitHub Actions** — directly from Python or as an MCP server for AI agents.

## Installation

```bash
# Core library only
uv pip install package-query

# With MCP server support
uv pip install "package-query[mcp]"
```

## Python Usage

```python
import asyncio
from package_query import PackageQuery, PackageInfo

async def main():
    pq = PackageQuery()

    info: PackageInfo = await pq.query("pypi", "requests")
    print(f"{info.name}=={info.version}")

    info = await pq.query("npm", "express")
    print(f"{info.name}=={info.version}")

    info = await pq.query("github-actions", "actions/checkout")
    print(f"{info.name}=={info.version}")

asyncio.run(main())
```

### Supported Registries

| Registry         | Example Package    |
| ---------------- | ------------------ |
| `pypi`           | `requests`         |
| `npm`            | `express`          |
| `crates`         | `serde`            |
| `docker`         | `nginx`            |
| `github-actions` | `actions/checkout` |

## MCP Server

The MCP server allows AI agents (Claude, Copilot, Cursor, etc.) to query package versions without web search.

### Running the Server

```bash
# If installed with [mcp] extra
package-query-mcp

# Or from source
uv run --extra mcp package-query-mcp
```

### IDE Configuration

#### VS Code / Cursor

Add to your `settings.json`:

```json
{
  "mcp": {
    "servers": {
      "package-query": {
        "command": "uvx",
        "args": ["--from", "package-query[mcp]", "package-query-mcp"]
      }
    }
  }
}
```

Or if installed globally:

```json
{
  "mcp": {
    "servers": {
      "package-query": {
        "command": "package-query-mcp"
      }
    }
  }
}
```

#### Claude Desktop

Add to `~/.config/Claude/claude_desktop_config.json` (Linux) or equivalent:

```json
{
  "mcpServers": {
    "package-query": {
      "command": "uvx",
      "args": ["--from", "package-query[mcp]", "package-query-mcp"]
    }
  }
}
```

#### Antigravity IDE

Add to `~/.gemini/antigravity/mcp_config.json`:

```json
{
  "mcpServers": {
    "package-query": {
      "command": "uvx",
      "args": ["--from", "package-query[mcp]", "package-query-mcp"]
    }
  }
}
```

### Available Tools

| Tool                  | Description                         |
| --------------------- | ----------------------------------- |
| `get_package_version` | Get the latest version of a package |

**Parameters:**

- `registry` (string): One of `pypi`, `npm`, `crates`, `docker`, `github-actions`
- `package` (string): Package name
- `include_prerelease` (bool, optional): Include pre-release versions

## Development

```bash
# Clone and install all dependencies
git clone https://github.com/henrique-coder/package-query.git
cd package-query
uv sync --upgrade --all-groups --all-extras
just lint
just format
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
