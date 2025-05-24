# MCP Architecture

## Client-Server Architecture

```mermaid
graph LR
    subgraph Host
        A1[MCP Client]
        A2[MCP Client]
        A3[MCP Client]
    end

    B1[MCP Server]
    B2[MCP Server]
    B3[MCP Server]

    A1 -- MCP Protocol --> B1
    A2 -- MCP Protocol --> B2
    A3 -- MCP Protocol --> B3
```

# Dictionary

## Host 
LLM applications that want to access data through MCP (ex: Claude Desktop, IDEs, AI Agents, etc.)

## MCP Server
Lightweight programs that each expose specific capabilities through MCP (ex: file system, web browser, etc.)

## MCP Client
Maintain 1:1 connections with servers, inside the host application.

## Tools
Function and tools that can be invoked by the client
  - Retrieve / search
  - Send a message
  - Update DB records

## Resources
Read-only data or exposed by the server
  - Files
  - Database Records
  - API Response 

## Prompt Templates
Pre-defined templates for AI interactions
  - Document Question Answering
  - Code Generation
  - Summarization
  - Output as JSON


# MC Transport

How messages are sent between MCP Clients and MCP Servers
![Screenshot 2025-05-23 at 12 58 34](https://github.com/user-attachments/assets/a04c6c9b-8995-4d39-972c-eebbf35ae7a1)

1. For servers running locally: stdio (standard input/output)
2. For servers running remotely:
  - HTTP + SSE (Server Sent Events) (from protocol version 2024-11-05)
  - Streamable HTTP (from protocol version 2025-03-26) 

## Stdio
Client launches the server as a sub process, and the server process writes to stdout and reads from stdin.
![Screenshot 2025-05-23 at 13 04 56](https://github.com/user-attachments/assets/69e5b0f1-3d6d-4846-bf60-85a8b5e90742)

## HTTP + SSE / Streamable HTTP
Client makes HTTP requests to the server, and the server sends responses back to the client.
![Screenshot 2025-05-23 at 13 10 15](https://github.com/user-attachments/assets/198b5313-c2da-467e-9f6d-1d4d6ea70be4)



