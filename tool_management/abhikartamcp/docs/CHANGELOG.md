# Changelog

All notable changes to the Abhikarta MCP Integration project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2025-11-12

### Fixed
- **CRITICAL:** Fixed examples to properly handle ToolResult objects
  - Added `extract_data()` helper function to handle both ToolResult objects and dictionaries
  - Examples were using `.get()` on ToolResult objects, causing AttributeError
  - Now works correctly with the actual tool_management framework
  - Fixed in both `yahoo_finance_example.py` and `duckdb_tools_example.py`

## [1.0.1] - 2025-11-12

### Fixed
- **CRITICAL:** Fixed off-by-one error in tool name extraction
  - Suffix `:abhikartamcp` is 13 characters, not 14
  - Tool names were being sent to MCP server with last character missing
  - Example: `yahoo_search_symbols` was sent as `yahoo_search_symbol`
  - All tools now work correctly
- Added verification test in `tests/test_suffix_fix.py`

### Changed
- Updated `abhikarta_base_tool.py` line 64: `name[:-14]` → `name[:-13]`
- Added `BUG_FIX_NOTICE.md` documentation

## [1.0.0] - 2025-01-01

### Added
- Initial release of Abhikarta MCP Integration
- `AbhikartaMCPToolBuilder` singleton class for tool discovery and caching
- `AbhikartaBaseTool` class extending BaseTool with ABHIKARTAMCP type
- `MCPRegistryIntegration` for automatic tool registration
- `MCPAutoSync` service for background synchronization
- JSON-RPC 2.0 protocol support over HTTP
- Token-based authentication with automatic renewal
- Periodic tool cache refresh (configurable interval)
- Health check support via ping method
- Comprehensive parameter validation using JSON schemas
- Both synchronous and asynchronous tool execution modes
- Automatic tool naming with `:abhikartamcp` suffix
- Complete documentation and examples
- Technical documentation with architecture details
- Configuration examples for various environments

### Features
- Dynamic tool discovery from MCP server
- Intelligent caching with periodic refresh
- Automatic registry synchronization
- Authentication token management
- Schema-based parameter validation
- Async/await support throughout
- Error handling and recovery
- Comprehensive logging
- Health monitoring
- Tool grouping and tagging

### Documentation
- README.md with quick start guide
- TECHNICAL.md with detailed architecture
- Code examples (basic and advanced usage)
- Configuration examples
- API reference documentation

### Security
- Token-based authentication
- Automatic token renewal
- Secure credential handling
- No sensitive data in logs
- HTTPS support

## [Unreleased]

### Planned
- Connection pooling for multiple MCP servers
- Redis-based caching support
- Prometheus metrics integration
- OpenTelemetry tracing support
- Retry logic with exponential backoff
- Circuit breaker pattern implementation
- Batch tool execution support
- WebSocket transport support
- Tool execution history tracking
- Advanced error recovery strategies

---

Copyright © 2025-2030, All Rights Reserved  
Ashutosh Sinha (ajsinha@gmail.com)
