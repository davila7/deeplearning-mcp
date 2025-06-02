# File: deeplearning_course/5_streamlit_mcp_client.py
import streamlit as st
from dotenv import load_dotenv
from anthropic import Anthropic
from mcp import ClientSession
from mcp.client.sse import sse_client
from typing import List
import asyncio
import json
import time

load_dotenv()

class StreamlitMCPChatBot:
    def __init__(self):
        self.anthropic = Anthropic()
        
    # Get available tools
    async def get_available_tools(self, server_url: str):
        """Get list of available tools from server"""
        async with sse_client(server_url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                response = await session.list_tools()
                
                return [{
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                } for tool in response.tools]

    # Execute Tool
    async def execute_tool(self, server_url: str, tool_name: str, tool_args: dict):
        """Execute a single tool call"""
        async with sse_client(server_url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                return await session.call_tool(tool_name, arguments=tool_args)

    async def process_query_with_tools(self, server_url: str, query: str, available_tools: List[dict]):
        """Process a query using available tools"""
        messages = [{'role': 'user', 'content': query}]
        
        response = self.anthropic.messages.create(
            max_tokens=2024,
            model='claude-3-7-sonnet-20250219',
            tools=available_tools,
            messages=messages
        )
        
        full_response = ""
        
        while True:
            assistant_content = []
            
            for content in response.content:
                if content.type == 'text':
                    full_response += content.text
                    assistant_content.append(content)
                    
                elif content.type == 'tool_use':
                    assistant_content.append(content)
                    
                    # Show tool usage in UI
                    with st.expander(f"🛠️ Using tool: {content.name}", expanded=True):
                        st.markdown(f"**Tool ID:** `{content.id}`")
                        st.markdown("**Arguments:**")
                        st.json(content.input)
                        
                        progress_placeholder = st.empty()
                        progress_placeholder.info(f"🔄 Executing {content.name}...")
                        
                        start_time = time.time()
                        result = await self.execute_tool(server_url, content.name, content.input)
                        elapsed = time.time() - start_time
                        
                        progress_placeholder.success(f"✅ {content.name} completed in {elapsed:.1f}s")
                        
                        st.markdown("### Result:")
                        try:
                            json_content = json.loads(result.content)
                            st.json(json_content)
                        except (json.JSONDecodeError, TypeError):
                            st.markdown(str(result.content))
                    
                    # Add messages for tool interaction
                    messages.append({'role': 'assistant', 'content': assistant_content})
                    messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result.content
                        }]
                    })
                    
                    # Get next response
                    response = self.anthropic.messages.create(
                        max_tokens=2024,
                        model='claude-3-7-sonnet-20250219',
                        tools=available_tools,
                        messages=messages
                    )
                    break
            else:
                # No tool use found, we're done
                break
        
        return full_response

def main():
    st.set_page_config(
        page_title="MCP Client",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 MCP Client (SSE)")
    
    # Initialize session state
    if 'available_tools' not in st.session_state:
        st.session_state.available_tools = []
        st.session_state.connected = False
        st.session_state.messages = []
        st.session_state.server_url = "http://localhost:8000/sse"
    
    # Sidebar for connection and tools
    with st.sidebar:
        st.header("🔧 MCP Configuration")
        
        server_url = st.text_input("MCP server URL", st.session_state.server_url)
        st.session_state.server_url = server_url
        
        if not st.session_state.connected:
            if st.button("🔌 Connect to MCP server"):
                with st.spinner("Connecting to MCP server..."):
                    try:
                        chatbot = StreamlitMCPChatBot()
                        tools = asyncio.run(chatbot.get_available_tools(server_url))
                        
                        st.session_state.available_tools = tools
                        st.session_state.connected = True
                        st.session_state.chatbot = chatbot
                        st.success("✅ Connected successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")
        else:
            st.success("✅ Connected to MCP server")
            
            if st.button("🔌 Disconnect"):
                st.session_state.available_tools = []
                st.session_state.connected = False
                st.session_state.messages = []
                st.session_state.chatbot = None
                st.success("🔌 Disconnected successfully!")
                st.rerun()
            
            st.subheader("📋 Available Tools:")
            for tool in st.session_state.available_tools:
                with st.expander(f"🛠️ {tool['name']}"):
                    st.write(f"**Description:** {tool['description']}")
                    if 'properties' in tool['input_schema']:
                        st.write("**Parameters:**")
                        for param, details in tool['input_schema']['properties'].items():
                            st.write(f"- `{param}`: {details.get('description', 'No description')}")
    
    # Main chat interface
    if not st.session_state.connected:
        st.info("👈 Please connect to the MCP server using the button in the sidebar to get started.")
    else:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Type your message here..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate assistant response
            with st.chat_message("assistant"):
                try:
                    response = asyncio.run(
                        st.session_state.chatbot.process_query_with_tools(
                            st.session_state.server_url,
                            prompt,
                            st.session_state.available_tools
                        )
                    )
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"❌ Error processing query: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()