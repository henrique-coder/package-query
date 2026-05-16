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
from asyncio import run
from package_query import PackageQuery, PackageInfo

async def main():
    pq = PackageQuery()

    # Single query — format_pinned() returns the registry-native pinning format
    info: PackageInfo = await pq.query("pypi", "requests")
    print(info.format_pinned())  # [pypi] requests==2.32.3

    info = await pq.query("npm", "express")
    print(info.format_pinned())  # [npm] express@5.2.1

    info = await pq.query("github-actions", "actions/checkout")
    print(info.format_pinned())  # [github-actions] actions/checkout@v4

    # Batch query — all resolved concurrently
    packages = [
        {"registry": "pypi", "package": "flask"},
        {"registry": "npm", "package": "typescript"},
        {"registry": "crates", "package": "tokio"},
        {"registry": "docker", "package": "nginx"},
        {"registry": "github-actions", "package": "actions/setup-python"},
    ]
    results = await pq.query_batch(packages)
    print(pq.format_batch(packages, results))
    # [pypi] flask==3.1.1
    # [npm] typescript@5.8.3
    # [crates] tokio = "=1.45.0"
    # [docker] nginx:stable-alpine3.23
    # [github-actions] actions/setup-python@v5

run(main())
```

### Output Format

Each registry uses its ecosystem-standard version-pinning format, prefixed with `[registry]`:

| Registry         | Format                            | Example                                |
| ---------------- | --------------------------------- | -------------------------------------- |
| `pypi`           | `[pypi] name==version`            | `[pypi] requests==2.32.3`              |
| `npm`            | `[npm] name@version`              | `[npm] express@5.2.1`                  |
| `crates`         | `[crates] name = "=version"`      | `[crates] serde = "=1.0.228"`          |
| `docker`         | `[docker] name:tag`               | `[docker] nginx:stable-alpine3.23`     |
| `github-actions` | `[github-actions] owner/repo@tag` | `[github-actions] actions/checkout@v4` |

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

| Tool                   | Description                                                  |
| ---------------------- | ------------------------------------------------------------ |
| `get_package_version`  | Get the latest version of a single package                   |
| `get_package_versions` | Get versions for multiple packages in one call (recommended) |

#### `get_package_version`

- `registry` (string): One of `pypi`, `npm`, `crates`, `docker`, `github-actions`
- `package` (string): Package name (e.g. `"requests"`, `"actions/checkout"`)
- `include_prerelease` (bool, optional): Include pre-release versions

Returns a single line like `[pypi] requests==2.32.3`.

#### `get_package_versions` _(batch — preferred)_

- `packages` (list): Array of objects with `"registry"` and `"package"` keys
- `include_prerelease` (bool, optional): Apply to all queries

All queries run concurrently. Returns one line per package:

```
[pypi] requests==2.32.3
[npm] express@5.2.1
[crates] serde = "=1.0.228"
[docker] nginx:stable-alpine3.23
[github-actions] actions/checkout@v4
[pypi] nonexistent: error: Package 'nonexistent' not found on PyPI
```

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
