# VersionOne MCP Server

A simplified Model Context Protocol (MCP) server using [FastMCP](https://github.com/modelcontextprotocol/python-sdk) for VersionOne API integration. This server enables AI assistants to query VersionOne for stories, features (epics), and their details with structured output.

## Features

The server provides four main tools with structured Pydantic models:

1. **get_stories** - Get a list of stories from VersionOne
2. **get_story_details** - Get detailed information about a specific story by ID
3. **get_features** - Get a list of features (Epics) from VersionOne
4. **get_feature_details** - Get detailed information about a specific feature by ID

## Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- VersionOne access token
- Your VersionOne instance URL

## Installation

1. Install uv (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone or download this project:
```bash
cd versionone-mcp-server
```

3. Install dependencies with uv:
```bash
uv sync
```

4. Configure your VersionOne credentials:
```bash
cp env-template.txt .env
```

5. Edit `.env` with your actual VersionOne details:
```bash
# Your VersionOne base URL (e.g., https://www7.v1host.com/V1Instance)
VERSIONONE_BASE_URL=https://your-v1-host.com/YourInstance

# Your VersionOne access token (recommended)
VERSIONONE_ACCESS_TOKEN=your-access-token-here
```

## Getting Your VersionOne Access Token

1. Log into your VersionOne instance
2. Navigate to your profile settings
3. Go to the Applications page
4. Create a new access token
5. Copy the token to your `.env` file

## Configuration

### Environment Variables

- `VERSIONONE_BASE_URL`: Your VersionOne instance URL (e.g., `https://www7.v1host.com/V1Instance`)
- `VERSIONONE_ACCESS_TOKEN`: Your VersionOne access token (recommended method)

### MCP Configuration

Add this server to your MCP client configuration:

```json
{
  "mcpServers": {
    "versionone": {
      "command": "uv",
      "args": ["run", "server", "stdio"],
      "cwd": "/path/to/versionone-mcp-server",
      "env": {
        "VERSIONONE_BASE_URL": "https://your-v1-host.com/YourInstance",
        "VERSIONONE_ACCESS_TOKEN": "your-access-token-here"
      }
    }
  }
}
```

## Usage

### Running the Server

```bash
uv run server stdio
```

### Available Tools

#### 1. get_stories

Get a list of stories from VersionOne with optional filtering.

**Parameters:**
- `filters` (optional): Object containing query filters
  - `where`: Where clause for filtering (e.g., `'AssetState!="Dead"'`)
  - `sel`: Comma-separated list of attributes to select (e.g., `'Name,Number,Description'`)
  - `sort`: Sort order (e.g., `'Name'`)
- `page_size` (optional): Number of items per page (default: 20)
- `page_start` (optional): Starting page number (default: 0)

**Example:**
```json
{
  "name": "get_stories",
  "arguments": {
    "filters": {
      "where": "AssetState!=\"Dead\"",
      "sel": "Name,Number,Description,Status"
    },
    "page_size": 10
  }
}
```

#### 2. get_story_details

Get detailed information about a specific story by ID.

**Parameters:**
- `story_id` (required): The ID of the story (e.g., `"Story:1234"`)
- `attributes` (optional): List of specific attributes to retrieve

**Example:**
```json
{
  "name": "get_story_details",
  "arguments": {
    "story_id": "Story:1234",
    "attributes": ["Name", "Description", "Status", "Owner"]
  }
}
```

#### 3. get_features

Get a list of features (Epics) from VersionOne with optional filtering.

**Parameters:**
- `filters` (optional): Object containing query filters
  - `where`: Where clause for filtering
  - `sel`: Comma-separated list of attributes to select
  - `sort`: Sort order
- `page_size` (optional): Number of items per page (default: 20)
- `page_start` (optional): Starting page number (default: 0)

**Example:**
```json
{
  "name": "get_features",
  "arguments": {
    "filters": {
      "where": "AssetState!=\"Dead\"",
      "sel": "Name,Number,Description,Status"
    }
  }
}
```

#### 4. get_feature_details

Get detailed information about a specific feature by ID.

**Parameters:**
- `feature_id` (required): The ID of the feature/epic (e.g., `"Epic:1234"`)
- `attributes` (optional): List of specific attributes to retrieve

**Example:**
```json
{
  "name": "get_feature_details",
  "arguments": {
    "feature_id": "Epic:1234",
    "attributes": ["Name", "Description", "Status", "Owner"]
  }
}
```

## VersionOne API Reference

This MCP server is built on top of the VersionOne REST API. For more detailed information about:

- Asset types and their relationships
- Available attributes for filtering and selection
- Query syntax and filtering options
- Authentication methods

Please refer to the official VersionOne API documentation at: https://versionone.github.io/api-docs/

### Common Asset Types

- **Story**: User stories and backlog items
- **Epic**: Features and large work items
- **Defect**: Bugs and issues
- **Task**: Development tasks
- **Test**: Test cases
- **Scope**: Projects
- **Timebox**: Sprints/Iterations

### Common Attributes

- `Name`: The title/name of the item
- `Number`: The auto-generated number (e.g., S-1001)
- `Description`: Detailed description
- `Status`: Current status of the item
- `Owner`: Assigned team member
- `AssetState`: State of the asset (Active, Closed, etc.)
- `CreateDate`: When the item was created
- `ChangeDate`: When the item was last modified

## Error Handling

The server includes comprehensive error handling for:

- Network connectivity issues
- Authentication failures
- Invalid API requests
- Missing or malformed parameters

Errors are logged and returned in a user-friendly format.

## Development

### Running in Development Mode

```bash
# Install development dependencies
uv sync --dev

# Run with debug logging
uv run server stdio
```

### Testing

You can test the server using any MCP-compatible client or by running individual functions with the VersionOne API directly.

## Security

- Always use access tokens instead of username/password when possible
- Keep your access tokens secure and rotate them regularly
- Use environment variables for sensitive configuration
- Never commit credentials to version control

## Troubleshooting

### Common Issues

1. **"VersionOne client not initialized"**
   - Check that your environment variables are set correctly
   - Verify your VersionOne URL format
   - Ensure your access token is valid

2. **Authentication errors (401)**
   - Verify your access token is correct and not expired
   - Check that your VersionOne URL is correct
   - Try creating a new access token

3. **Network timeouts**
   - Check your internet connection
   - Verify the VersionOne server is accessible
   - Try increasing the timeout in the code if needed

### Debugging

Enable debug logging by setting the log level in the server code:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is provided as-is for educational and development purposes.

## Support

For issues related to:
- This MCP server: Create an issue in this repository
- VersionOne API: Refer to VersionOne documentation or support
- MCP protocol: Refer to the MCP specification documentation 