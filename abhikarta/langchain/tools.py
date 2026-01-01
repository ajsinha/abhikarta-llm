"""
LangChain Tools - Tool creation and MCP tool integration for LangChain agents.

Supports:
- MCP Tool Server integration (dynamic tools from external servers)
- Code Fragment execution
- Custom Python tools
- Built-in tools (web search, file operations, etc.)

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List, Callable, Type
from pydantic import BaseModel, Field, create_model

logger = logging.getLogger(__name__)


def create_langchain_tool(name: str, description: str, func: Callable, 
                          args_schema: Type[BaseModel] = None) -> Any:
    """
    Create a LangChain tool from a function.
    
    Args:
        name: Tool name
        description: Tool description
        func: Function to execute
        args_schema: Optional Pydantic model for arguments
        
    Returns:
        LangChain Tool instance
    """
    try:
        from langchain_core.tools import Tool, StructuredTool
    except ImportError:
        raise ImportError("langchain-core is required. Install with: pip install langchain-core")
    
    if args_schema:
        return StructuredTool.from_function(
            func=func,
            name=name,
            description=description,
            args_schema=args_schema
        )
    else:
        return Tool(
            name=name,
            description=description,
            func=func
        )


class MCPToolAdapter:
    """
    Adapter that converts MCP Tool Server tools into LangChain tools.
    
    Fetches tool definitions from MCP servers and creates LangChain-compatible
    tools that can be used with agents.
    """
    
    def __init__(self, db_facade=None):
        self.db_facade = db_facade
        self._cached_tools = {}
    
    def get_tools_from_server(self, server_config: Dict[str, Any]) -> List[Any]:
        """
        Fetch tools from an MCP server and convert to LangChain tools.
        
        Args:
            server_config: Server configuration dict
            
        Returns:
            List of LangChain Tool instances
        """
        try:
            from langchain_core.tools import StructuredTool
        except ImportError:
            raise ImportError("langchain-core is required")
        
        tools = []
        cached_tools = server_config.get('cached_tools', '[]')
        
        if isinstance(cached_tools, str):
            cached_tools = json.loads(cached_tools)
        
        for tool_def in cached_tools:
            try:
                tool = self._create_mcp_tool(tool_def, server_config)
                tools.append(tool)
            except Exception as e:
                logger.warning(f"Failed to create tool {tool_def.get('name')}: {e}")
        
        return tools
    
    def get_all_active_tools(self) -> List[Any]:
        """
        Get all tools from all active MCP servers.
        
        Returns:
            List of LangChain Tool instances
        """
        if not self.db_facade:
            return []
        
        tools = []
        servers = self.db_facade.fetch_all(
            "SELECT * FROM mcp_tool_servers WHERE is_active = 1"
        ) or []
        
        for server in servers:
            try:
                server_tools = self.get_tools_from_server(dict(server))
                tools.extend(server_tools)
            except Exception as e:
                logger.warning(f"Failed to load tools from {server.get('name')}: {e}")
        
        return tools
    
    def _create_mcp_tool(self, tool_def: Dict, server_config: Dict) -> Any:
        """Create a single LangChain tool from an MCP tool definition."""
        from langchain_core.tools import StructuredTool
        
        name = tool_def.get('name', 'unknown_tool')
        description = tool_def.get('description', 'No description')
        input_schema = tool_def.get('inputSchema', {})
        
        # Create Pydantic model from JSON Schema
        args_schema = self._json_schema_to_pydantic(name, input_schema)
        
        # Create the execution function
        def execute_mcp_tool(**kwargs) -> str:
            return self._call_mcp_tool(server_config, name, kwargs)
        
        return StructuredTool.from_function(
            func=execute_mcp_tool,
            name=name,
            description=description,
            args_schema=args_schema
        )
    
    def _json_schema_to_pydantic(self, name: str, schema: Dict) -> Type[BaseModel]:
        """Convert JSON Schema to Pydantic model."""
        properties = schema.get('properties', {})
        required = set(schema.get('required', []))
        
        field_definitions = {}
        
        for prop_name, prop_def in properties.items():
            prop_type = prop_def.get('type', 'string')
            prop_desc = prop_def.get('description', '')
            default = prop_def.get('default', ...)
            
            # Map JSON schema types to Python types
            type_mapping = {
                'string': str,
                'integer': int,
                'number': float,
                'boolean': bool,
                'array': list,
                'object': dict
            }
            
            python_type = type_mapping.get(prop_type, str)
            
            if prop_name in required:
                field_definitions[prop_name] = (python_type, Field(description=prop_desc))
            else:
                if default == ...:
                    default = None
                field_definitions[prop_name] = (Optional[python_type], Field(default=default, description=prop_desc))
        
        # Create dynamic Pydantic model
        model_name = f"{name.replace('-', '_').replace('.', '_')}Input"
        return create_model(model_name, **field_definitions)
    
    def _call_mcp_tool(self, server_config: Dict, tool_name: str, 
                       arguments: Dict) -> str:
        """
        Call an MCP tool on the server.
        
        Args:
            server_config: Server configuration
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result as string
        """
        base_url = server_config.get('base_url', '').rstrip('/')
        
        # MCP standard tool call endpoint
        call_endpoint = f"{base_url}/api/tools/call"
        timeout = server_config.get('timeout_seconds', 30) or 30
        
        try:
            # Build request
            request_data = {
                'name': tool_name,
                'arguments': arguments
            }
            
            req = urllib.request.Request(
                call_endpoint,
                data=json.dumps(request_data).encode('utf-8'),
                method='POST'
            )
            req.add_header('Content-Type', 'application/json')
            req.add_header('Accept', 'application/json')
            
            # Add auth headers
            auth_type = server_config.get('auth_type', 'none')
            if auth_type and auth_type != 'none':
                auth_config = json.loads(server_config.get('auth_config', '{}'))
                if auth_type == 'bearer' and 'token' in auth_config:
                    req.add_header('Authorization', f"Bearer {auth_config['token']}")
                elif auth_type == 'api_key' and 'key' in auth_config and 'header' in auth_config:
                    req.add_header(auth_config['header'], auth_config['key'])
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                # Extract result content
                if isinstance(result, dict):
                    if 'content' in result:
                        content = result['content']
                        if isinstance(content, list) and len(content) > 0:
                            # Handle MCP content array format
                            text_parts = [c.get('text', str(c)) for c in content if isinstance(c, dict)]
                            return '\n'.join(text_parts) if text_parts else json.dumps(result)
                        return str(content)
                    elif 'result' in result:
                        return json.dumps(result['result']) if isinstance(result['result'], (dict, list)) else str(result['result'])
                    elif 'error' in result:
                        return f"Error: {result['error']}"
                
                return json.dumps(result)
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else str(e)
            return f"HTTP Error {e.code}: {error_body[:500]}"
        except urllib.error.URLError as e:
            return f"Connection Error: {e.reason}"
        except Exception as e:
            return f"Error calling tool: {str(e)}"


class CodeFragmentTool:
    """
    LangChain tool for executing code fragments.
    """
    
    def __init__(self, db_facade, code_loader=None):
        self.db_facade = db_facade
        self.code_loader = code_loader
    
    def create_tool(self, fragment_id: str) -> Any:
        """Create a LangChain tool from a code fragment."""
        from langchain_core.tools import Tool
        
        fragment = self.db_facade.fetch_one(
            "SELECT * FROM code_fragments WHERE fragment_id = ? AND is_active = 1",
            (fragment_id,)
        )
        
        if not fragment:
            raise ValueError(f"Code fragment not found: {fragment_id}")
        
        name = fragment.get('name', fragment_id)
        description = fragment.get('description', 'Execute code fragment')
        
        def execute_fragment(input_data: str = "") -> str:
            try:
                # Parse input as JSON if possible
                try:
                    params = json.loads(input_data) if input_data else {}
                except:
                    params = {'input': input_data}
                
                # Load and execute the code
                if self.code_loader:
                    result = self.code_loader.execute_fragment(fragment_id, params)
                    return json.dumps(result) if isinstance(result, (dict, list)) else str(result)
                else:
                    return "Code loader not configured"
            except Exception as e:
                return f"Error: {str(e)}"
        
        return Tool(
            name=name,
            description=description,
            func=execute_fragment
        )


class ToolFactory:
    """
    Factory for creating various types of LangChain tools.
    """
    
    def __init__(self, db_facade=None, code_loader=None):
        self.db_facade = db_facade
        self.code_loader = code_loader
        self.mcp_adapter = MCPToolAdapter(db_facade)
        self.code_fragment_tool = CodeFragmentTool(db_facade, code_loader) if db_facade else None
    
    def get_mcp_tools(self, server_id: str = None) -> List[Any]:
        """
        Get MCP tools, optionally from a specific server.
        
        Args:
            server_id: Optional specific server ID
            
        Returns:
            List of LangChain tools
        """
        if server_id:
            server = self.db_facade.fetch_one(
                "SELECT * FROM mcp_tool_servers WHERE server_id = ? AND is_active = 1",
                (server_id,)
            )
            if server:
                return self.mcp_adapter.get_tools_from_server(dict(server))
            return []
        
        return self.mcp_adapter.get_all_active_tools()
    
    def get_code_fragment_tool(self, fragment_id: str) -> Any:
        """Get a code fragment as a LangChain tool."""
        if not self.code_fragment_tool:
            raise ValueError("Code loader not configured")
        return self.code_fragment_tool.create_tool(fragment_id)
    
    def get_builtin_tools(self, tool_names: List[str] = None) -> List[Any]:
        """
        Get built-in LangChain tools.
        
        Available tools:
        - web_search: Search the web (requires Tavily API key)
        - web_fetch: Fetch content from a URL
        - wikipedia: Search Wikipedia
        - python_repl: Execute Python code
        - shell: Execute shell commands
        - requests: Make HTTP requests
        
        Args:
            tool_names: List of tool names to get, or None for all
            
        Returns:
            List of LangChain tools
        """
        from langchain_core.tools import Tool, StructuredTool
        
        tools = []
        available = tool_names or ['wikipedia']
        
        for name in available:
            try:
                if name == 'web_search':
                    from langchain_community.tools import TavilySearchResults
                    tools.append(TavilySearchResults(max_results=5))
                elif name == 'web_fetch':
                    # Create a simple web fetch tool
                    tools.append(self._create_web_fetch_tool())
                elif name == 'wikipedia':
                    from langchain_community.tools import WikipediaQueryRun
                    from langchain_community.utilities import WikipediaAPIWrapper
                    tools.append(WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()))
                elif name == 'python_repl':
                    from langchain_experimental.tools import PythonREPLTool
                    tools.append(PythonREPLTool())
                elif name == 'shell':
                    from langchain_community.tools import ShellTool
                    tools.append(ShellTool())
                elif name == 'requests':
                    from langchain_community.tools import RequestsGetTool
                    from langchain_community.utilities import TextRequestsWrapper
                    tools.append(RequestsGetTool(requests_wrapper=TextRequestsWrapper()))
            except ImportError as e:
                logger.warning(f"Could not load built-in tool {name}: {e}")
            except Exception as e:
                logger.warning(f"Error creating built-in tool {name}: {e}")
        
        return tools
    
    def _create_web_fetch_tool(self) -> Any:
        """Create a web fetch tool for fetching URL content."""
        from langchain_core.tools import Tool
        
        def fetch_url(url: str) -> str:
            """Fetch content from a URL."""
            import urllib.request
            import urllib.error
            
            try:
                # Clean the URL
                url = url.strip()
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                req = urllib.request.Request(
                    url,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                )
                
                with urllib.request.urlopen(req, timeout=30) as response:
                    content = response.read().decode('utf-8', errors='ignore')
                    
                    # Try to extract text from HTML
                    try:
                        from html.parser import HTMLParser
                        
                        class TextExtractor(HTMLParser):
                            def __init__(self):
                                super().__init__()
                                self.text_parts = []
                                self.skip_tags = {'script', 'style', 'nav', 'footer', 'header'}
                                self.current_tag = None
                            
                            def handle_starttag(self, tag, attrs):
                                self.current_tag = tag
                            
                            def handle_endtag(self, tag):
                                self.current_tag = None
                            
                            def handle_data(self, data):
                                if self.current_tag not in self.skip_tags:
                                    text = data.strip()
                                    if text:
                                        self.text_parts.append(text)
                            
                            def get_text(self):
                                return ' '.join(self.text_parts)
                        
                        parser = TextExtractor()
                        parser.feed(content)
                        text = parser.get_text()
                        
                        # Limit response size
                        if len(text) > 10000:
                            text = text[:10000] + "... [truncated]"
                        
                        return text if text else content[:5000]
                        
                    except Exception:
                        # Return raw content if parsing fails
                        return content[:5000]
                        
            except urllib.error.HTTPError as e:
                return f"HTTP Error {e.code}: {e.reason}"
            except urllib.error.URLError as e:
                return f"URL Error: {e.reason}"
            except Exception as e:
                return f"Error fetching URL: {str(e)}"
        
        return Tool(
            name="web_fetch",
            description="Fetch and extract text content from a URL. Input should be a valid URL.",
            func=fetch_url
        )
    
    def get_tool_by_name(self, tool_name: str, server_id: str = None) -> Any:
        """
        Get a specific tool by name.
        
        Searches in order:
        1. Built-in tools
        2. MCP tools from specified server
        3. MCP tools from all servers
        
        Args:
            tool_name: Name of the tool
            server_id: Optional specific MCP server ID
            
        Returns:
            LangChain tool or None if not found
        """
        # Check built-in tools first
        builtin_names = ['web_search', 'web_fetch', 'wikipedia', 'python_repl', 'shell', 'requests']
        if tool_name in builtin_names:
            tools = self.get_builtin_tools([tool_name])
            if tools:
                return tools[0]
        
        # Check MCP tools
        mcp_tools = self.get_mcp_tools(server_id)
        for tool in mcp_tools:
            if tool.name == tool_name:
                return tool
        
        return None
    
    def create_custom_tool(self, name: str, description: str, 
                          func: Callable, args_schema: Type[BaseModel] = None) -> Any:
        """Create a custom LangChain tool."""
        return create_langchain_tool(name, description, func, args_schema)
    
    def get_all_tools(self, include_mcp: bool = True, 
                     include_builtin: List[str] = None,
                     code_fragments: List[str] = None) -> List[Any]:
        """
        Get all configured tools.
        
        Args:
            include_mcp: Whether to include MCP server tools
            include_builtin: List of built-in tools to include
            code_fragments: List of code fragment IDs to include
            
        Returns:
            Combined list of LangChain tools
        """
        tools = []
        
        if include_mcp and self.db_facade:
            tools.extend(self.get_mcp_tools())
        
        if include_builtin:
            tools.extend(self.get_builtin_tools(include_builtin))
        
        if code_fragments and self.code_fragment_tool:
            for frag_id in code_fragments:
                try:
                    tools.append(self.get_code_fragment_tool(frag_id))
                except Exception as e:
                    logger.warning(f"Failed to load code fragment {frag_id}: {e}")
        
        return tools
