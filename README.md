# MCP Courses

A comprehensive collection of courses and tutorials for learning the **Model Context Protocol (MCP)** - an open protocol that standardizes how AI applications connect to external tools and data sources.

## 🎯 What is MCP?

The Model Context Protocol (MCP) enables AI models to connect with external data sources, tools, and environments, allowing for seamless transfer of information and capabilities between AI systems and the broader digital world. MCP transforms the complex M×N integration problem into a simple M+N solution by providing a standard interface.

### Key Benefits:
- **For Users**: Simpler and more consistent experiences across AI applications
- **For Developers**: Easy integration with a growing ecosystem of tools and data sources  
- **For Tool Providers**: Single implementation that works with multiple AI applications
- **For Ecosystem**: Increased interoperability, innovation, and reduced fragmentation

## 📚 Course Structure

### 🚀 Deep Learning Course
**Status: ✅ Available**

A comprehensive course covering MCP implementation with practical examples using Streamlit, Wikipedia, and arXiv integrations.

#### Course Contents:

**📖 Fundamentals & Tool Integration**
- `3_streamlit_tool_use_arxiv.py` - Streamlit app with arXiv paper search functionality
- `3_arxiv_mcp_server.py` - MCP server for arXiv paper search and information extraction
- `4_streamlit_tool_use_wikipedia.py` - Streamlit app with Wikipedia integration
- `4_wikipedia_mcp_server_sse.py` - Wikipedia MCP server with SSE transport
- `4_wikipedia_mcp_server_stdio.py` - Wikipedia MCP server with STDIO transport

**🔗 MCP Client Implementation**
- `5_mcp_client.py` - Basic MCP client implementation
- `5_streamlit_mcp_client.py` - Streamlit interface for single MCP server connection
- `6_streamlit_mcp_client_multiple.py` - Advanced multi-server MCP client with Streamlit UI

**🌐 Advanced Server Implementations**
- `7_wikipedia_mcp_server_stdio_prompts_resources.py` - Full-featured Wikipedia server with prompts and resources
- `7_wikipedia_mcp_client_prompts_resources_stdio.py` - Client for advanced Wikipedia server
- `7_wikipedia_mcp_server_prompts_resources_sse copy.py` - SSE version with prompts and resources
- `7_wikipedia_mcp_server_prompts_resources_streamable-http.py` - HTTP streamable version (Production recommended)

#### Key Features Covered:
- **Transport Protocols**: STDIO, SSE, and Streamable HTTP
- **Tool Integration**: Search, content retrieval, and data processing
- **Multi-Server Architecture**: Connect to multiple MCP servers simultaneously
- **Interactive UI**: Streamlit-based chat interfaces
- **Resource Management**: Prompts, tools, and resources handling
- **Game Generation**: Interactive educational content creation

#### Configuration:
- `server_config.json` - Multi-server configuration file
- Pre-configured data directories for papers and wiki articles

### 📊 DataCamp Course
**Status: 🔄 Coming Soon**

Advanced data science and analytics integration with MCP protocol.

### 🤗 Hugging Face Course  
**Status: 🔄 Coming Soon**

Machine learning model integration and deployment using MCP with Hugging Face ecosystem.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js (for filesystem server)
- UV package manager (recommended)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/davila7/mcp-courses.git
cd mcp-courses
pip install -r requirements.txt
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Copy and configure your API keys
cp .env.example .env
# Edit .env with your API keys (Anthropic, Brave Search, etc.)
```

## Quick Start - Deep Learning Course
1. Run a basic MCP server:
```bash
# Start Wikipedia MCP server with STDIO
python deeplearning_course/4_wikipedia_mcp_server_stdio.py
```

2. Launch Streamlit client:
```bash
# Single server client
streamlit run deeplearning_course/5_streamlit_mcp_client.py

# Multi-server client (recommended)
streamlit run deeplearning_course/6_streamlit_mcp_client_multiple.py
```

3. Configure servers:
- Edit deeplearning_course/server_config.json to add your server configurations
- The multi-server client supports filesystem and Wikipedia servers out of the box

## 🏗️ Architecture Overview
Transport Protocols Supported:
- STDIO: Direct process communication (development)
- SSE: Server-Sent Events over HTTP (web applications)
- Streamable HTTP: Modern HTTP with bidirectional streaming (production recommended)

## Core Components:
- MCP Servers: Expose tools, resources, and prompts
- MCP Clients: Connect to servers and manage communication
- Streamlit UIs: Interactive web interfaces for testing and demonstration
- Configuration Management: JSON-based server configuration


## 📖 Learning Path
1. Start with Tool Integration (3_*.py files)
- Learn basic tool calling with Streamlit
- Understand arXiv and Wikipedia API integration

2. Explore MCP Servers (4_*.py files)
- Implement MCP servers with different transport protocols
- Compare STDIO vs SSE implementations

3. Build MCP Clients (5_*.py and 6_*.py files)
- Create single and multi-server clients
- Master session management and tool orchestration

4. Advanced Features (7_*.py files)
- Implement prompts and resources
- Build production-ready servers with Streamable HTTP

### Project Structure:
```bash
mcp-courses/
├── deeplearning_course/           # Complete MCP course materials
│   ├── papers/                    # arXiv paper storage
│   ├── wiki_articles/             # Wikipedia article cache
│   └── server_config.json         # Multi-server configuration
├── main.py                        # Repository entry point
├── requirements.txt               # Python dependencies
└── pyproject.toml                 # Project configuration
```

# Contributing
Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

# 📄 License
This project is open source and available under the MIT License.

# 🔗 Resources
- MCP Official Documentation: [Model Context Protocol](https://modelcontextprotocol.io/introduction)
- Anthropic Tool use:  [Tool use Documentation](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview)
- Anthropic MCP Guide: [MCP Documentation](https://docs.anthropic.com/en/docs/agents-and-tools/mcp)