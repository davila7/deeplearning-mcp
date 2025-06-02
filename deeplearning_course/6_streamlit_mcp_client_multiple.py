# File: deeplearning_course/6_streamlit_mcp_client_multiple.py
import streamlit as st
from dotenv import load_dotenv
from anthropic import Anthropic
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from typing import List, Dict
import asyncio
import json
import time
from contextlib import AsyncExitStack
import traceback
import os

load_dotenv()

class StreamlitMCPChatBot:
    """
    ChatBot that connects to multiple MCP servers and allows using their tools
    through Claude AI in a Streamlit interface.
    """
    
    def __init__(self):
        self.anthropic = Anthropic()
        # Stores active sessions with each MCP server
        self.sessions: List[ClientSession] = []
        # Maps each tool to its corresponding session
        self.tool_to_session: Dict[str, ClientSession] = {}
        # List of all available tools
        self.available_tools: List[dict] = []
        # Maps tools to their origin servers
        self.tool_server_map: Dict[str, str] = {}
        self.exit_stack = None
        
    async def connect_to_server(self, server_name: str, server_config: dict) -> None:
        """Connects to an individual MCP server."""
        try:
            # Configure stdio connection with the server
            server_params = StdioServerParameters(**server_config)
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport
            
            # Establish session with the server
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()
            self.sessions.append(session)
            
            # Get available tools from the server
            response = await session.list_tools()
            tools = response.tools
            print(f"Connected to {server_name} with tools:", [t.name for t in tools])
            
            # Register each tool and its server
            for tool in tools:
                self.tool_to_session[tool.name] = session
                self.tool_server_map[tool.name] = server_name
                self.available_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                })
                
        except Exception as e:
            print(f"Error connecting to {server_name}: {e}")
            raise

    async def connect_to_servers(self):
        """Connects to all servers configured in server_config.json."""
        try:
            self.exit_stack = AsyncExitStack()
            
            # Load server configuration
            with open("server_config.json", "r") as file:
                data = json.load(file)
            
            servers = data.get("mcpServers", {})
            
            # Connect to each configured server
            for server_name, server_config in servers.items():
                await self.connect_to_server(server_name, server_config)
                
        except Exception as e:
            print(f"Error loading configuration: {e}")
            if self.exit_stack:
                await self.exit_stack.aclose()
            raise

    async def execute_tool(self, tool_name: str, tool_args: dict):
        """Executes a specific tool using the appropriate session."""
        if tool_name not in self.tool_to_session:
            raise ValueError(f"Tool {tool_name} not found")
        
        session = self.tool_to_session[tool_name]
        
        try:
            print(f"Executing {tool_name} with arguments: {tool_args}")
            result = await session.call_tool(tool_name, arguments=tool_args)
            return result
        except Exception as e:
            print(f"Error executing {tool_name}: {e}")
            raise

    async def process_query_with_tools(self, query: str):
        """
        Processes a user query using Claude AI and available MCP tools.
        Handles the complete conversation cycle including tool calls.
        """
        messages = [{'role': 'user', 'content': query}]
        
        # Request initial response from Claude with access to tools
        response = self.anthropic.messages.create(
            max_tokens=2024,
            model='claude-3-7-sonnet-20250219',
            tools=self.available_tools,
            messages=messages
        )
        
        full_response = ""
        
        # Process response and handle tool calls
        while True:
            assistant_content = []
            
            for content in response.content:
                # Normal text content
                if content.type == 'text':
                    full_response += content.text
                    assistant_content.append(content)
                    
                # Claude wants to use a tool
                elif content.type == 'tool_use':
                    assistant_content.append(content)
                    
                    # Show tool information in the UI
                    tool_server = self.tool_server_map.get(content.name, "Unknown")
                    st.markdown(f"### 🛠️ Using: {content.name} (Server: {tool_server})")
                    st.json(content.input)
                    
                    # Execute the tool
                    progress_placeholder = st.empty()
                    progress_placeholder.info(f"🔄 Executing {content.name}...")
                    
                    try:
                        start_time = time.time()
                        result = await self.execute_tool(content.name, content.input)
                        elapsed = time.time() - start_time
                        
                        progress_placeholder.success(f"✅ Completed in {elapsed:.1f}s")
                        
                        # Show the result
                        st.markdown("### Result:")
                        if hasattr(result, 'content'):
                            st.markdown(str(result.content))
                        else:
                            st.write(str(result))
                            
                    except Exception as tool_error:
                        elapsed = time.time() - start_time
                        progress_placeholder.error(f"❌ Error after {elapsed:.1f}s")
                        st.error(f"Error: {str(tool_error)}")
                        
                        # Create error result to continue conversation
                        result = type('ErrorResult', (), {
                            'content': f"Error executing {content.name}: {str(tool_error)}"
                        })()
                    
                    st.divider()
                    
                    # Update conversation with tool result
                    messages.append({'role': 'assistant', 'content': assistant_content})
                    messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result.content if hasattr(result, 'content') else str(result)
                        }]
                    })
                    
                    # Get next response from Claude
                    response = self.anthropic.messages.create(
                        max_tokens=2024,
                        model='claude-3-7-sonnet-20250219',
                        tools=self.available_tools,
                        messages=messages
                    )
                    break
            else:
                # No more tools to use, end the cycle
                break
        
        return full_response

    def disconnect_all(self):
        """Disconnects from all servers and cleans up resources."""
        try:
            if self.exit_stack:
                asyncio.run(self.exit_stack.aclose())
        except Exception as e:
            print(f"Error during disconnection: {e}")
        finally:
            # Clear all references
            self.sessions.clear()
            self.tool_to_session.clear()
            self.available_tools.clear()
            self.tool_server_map.clear()
            self.exit_stack = None

def load_server_config():
    """Loads server configuration from JSON file."""
    config_file = "server_config.json"
    
    # Default configuration if file doesn't exist
    default_config = {
        "mcpServers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"]
            },
            "brave-search": {
                "command": "npx", 
                "args": ["-y", "@modelcontextprotocol/server-brave-search"],
                "env": {
                    "BRAVE_API_KEY": "your-api-key"
                }
            }
        }
    }
    
    try:
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as file:
                return json.load(file)
        else:
            # Create file with default configuration
            with open(config_file, "w", encoding="utf-8") as file:
                json.dump(default_config, file, indent=2, ensure_ascii=False)
            return default_config
    except Exception as e:
        st.error(f"Error loading configuration: {e}")
        return default_config

def save_server_config(config):
    """Saves server configuration to JSON file."""
    try:
        with open("server_config.json", "w", encoding="utf-8") as file:
            json.dump(config, file, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error saving configuration: {e}")
        return False

def render_config_editor():
    """Renders the configuration editor in the sidebar."""
    
    # Load current configuration
    current_config = load_server_config()
    
    # Accordion for configuration
    with st.expander("⚙️ Server Configuration", expanded=False):
        # Text editor for configuration
        config_text = st.text_area(
            "Edit configuration:",
            value=json.dumps(current_config, indent=2, ensure_ascii=False),
            height=300,
            help="Edit JSON configuration directly. Make sure to maintain valid format."
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Save"):
                try:
                    # Validate JSON
                    new_config = json.loads(config_text)
                    
                    # Save configuration
                    if save_server_config(new_config):
                        st.success("✅ Configuration saved!")
                        st.rerun()
                    
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON: {e}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        with col2:
            if st.button("🔄 Reload"):
                st.rerun()


def main():
    """Main function that configures and runs the Streamlit interface."""
    
    st.set_page_config(
        page_title="MCP ChatBot Multi-Server",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 MCP ChatBot Multi-Server")
    
    # Initialize session state
    if 'connected' not in st.session_state:
        st.session_state.connected = False
        st.session_state.messages = []
        st.session_state.chatbot = None
        st.session_state.available_tools = []
        st.session_state.connected_servers = []
    
    # Sidebar for configuration
    with st.sidebar:
        
        # Configuration editor
        render_config_editor()
        
        st.divider()
        
        # Connection status and controls
        if not st.session_state.connected:
            st.subheader("🔌 Connection")
            
            # Button to connect to servers
            if st.button("🚀 Connect to MCP servers"):
                with st.spinner("Connecting to servers..."):
                    try:
                        chatbot = StreamlitMCPChatBot()
                        asyncio.run(chatbot.connect_to_servers())
                        
                        # Save information in session state
                        st.session_state.chatbot = chatbot
                        st.session_state.available_tools = chatbot.available_tools
                        st.session_state.connected = True
                        st.session_state.connected_servers = list(set(chatbot.tool_server_map.values()))
                        
                        st.success("✅ Connected successfully!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")
        else:
            st.subheader("✅ Status: Connected")
            st.success(f"Connected to {len(st.session_state.connected_servers)} server(s)")
            
            # List of connected servers
            st.markdown("**Active servers:**")
            for server in st.session_state.connected_servers:
                st.markdown(f"• {server}")
            
            # Disconnect button
            if st.button("🔌 Disconnect", type="secondary"):
                if st.session_state.chatbot:
                    st.session_state.chatbot.disconnect_all()
                
                # Reset state
                st.session_state.connected = False
                st.session_state.messages = []
                st.session_state.chatbot = None
                st.session_state.available_tools = []
                st.session_state.connected_servers = []
                st.rerun()
            
            st.divider()
            
            # Available tools
            with st.expander("🛠️ Available Tools", expanded=False):
                if st.session_state.available_tools:
                    # Create data for table
                    tools_data = []
                    for tool in st.session_state.available_tools:
                        server_name = st.session_state.chatbot.tool_server_map.get(tool['name'], 'Unknown')
                        tools_data.append({
                            "Tool": tool['name'],
                            "Server": server_name,
                            "Description": tool['description']
                        })
                    
                    # Show table
                    st.table(tools_data)
                else:
                    st.info("No tools available")

    
    # Main chat interface
    if not st.session_state.connected:
        st.info("👈 Configure and connect to MCP servers to begin.")
        
    else:
        # Chat interface
        st.subheader("💬 AI Chat")
        
        # Show previous messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Input for new messages
        if prompt := st.chat_input("Write your message..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    # Create and connect chatbot in the same event loop
                    async def handle_prompt(prompt):
                        chatbot = StreamlitMCPChatBot()
                        await chatbot.connect_to_servers()
                        response = await chatbot.process_query_with_tools(prompt)
                        return response

                    response = asyncio.run(handle_prompt(prompt))
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"❌ Error processing message: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()
