# Transport Protocols in MCP (Model Context Protocol)


## 1. STDIO (Standard Input/Output)

### Characteristics:
- Direct communication through process stdin/stdout
- Simplest and most direct protocol
- Bidirectional communication via JSON-RPC over text streams
- No network configuration required
- Ideal for local processes

### When to use:
- Local development and testing
- Command-line tool integration
- When server and client are on the same machine
- Applications requiring maximum simplicity

### Advantages:
- Minimal latency
- No network overhead
- Easy debugging (messages directly visible)
- Perfect for development

### Disadvantages:
- Only works locally
- One client per server
- Limited for distributed applications


## 2. SSE (Server-Sent Events)

### Characteristics:
- HTTP-based with unidirectional server-to-client streaming
- Uses two endpoints: GET for receiving events, POST for sending messages
- Maintains persistent connection for real-time events
- Compatible with standard web browsers

### When to use:
- Web applications needing real-time updates
- When browser compatibility is needed
- Scenarios where server needs to send frequent notifications

### Advantages:
- Native web standard
- Automatic reconnection
- Works through HTTP proxies

### Disadvantages:
- Being replaced by Streamable HTTP
- Less efficient than WebSockets for bidirectional communication
- Limitations with some proxies/firewalls

## 3. Streamable HTTP ⭐ RECOMMENDED FOR PRODUCTION

### Characteristics:
- Modern HTTP protocol with bidirectional streaming support
- Supports both JSON responses and SSE streams
- Session management with unique IDs
- Support for resumability (reconnection and event replay)
- Stateful and stateless modes
- Support for multiple nodes (horizontal scaling)

### When to use:
- Production applications (RECOMMENDED)
- Distributed systems
- When horizontal scalability is needed
- Applications requiring high availability
- Systems with multiple server instances

### Advantages:
- Best for production
- Horizontal scalability
- Connection resumability
- Load balancer support
- Response format flexibility (JSON/SSE)
- Robust error handling

### Disadvantages:
- More complex to implement
- Higher overhead than STDIO
- Architecture Diagram

```mermaid
graph TB
    subgraph "MCP Client"
        C[Client Application]
        CS[ClientSession]
        CT1[STDIO Transport]
        CT2[SSE Transport] 
        CT3[Streamable HTTP Transport]
    end
    
    subgraph "Transport Layer"
        STDIO[STDIO Protocol<br/>stdin/stdout]
        SSE[SSE Protocol<br/>HTTP GET/POST]
        SHTTP[Streamable HTTP<br/>HTTP with Sessions]
    end
    
    subgraph "MCP Server"
        ST1[STDIO Server]
        ST2[SSE Server]
        ST3[Streamable HTTP Server]
        SS[ServerSession]
        S[Server Application<br/>Tools/Resources/Prompts]
    end
    
    subgraph "LLM Integration"
        LLM[Large Language Model<br/>Claude, GPT, etc.]
    end
    
    %% Client connections
    C --> CS
    CS --> CT1
    CS --> CT2  
    CS --> CT3
    
    %% Transport connections
    CT1 <--> STDIO
    CT2 <--> SSE
    CT3 <--> SHTTP
    
    %% Server connections
    STDIO <--> ST1
    SSE <--> ST2
    SHTTP <--> ST3
    
    ST1 --> SS
    ST2 --> SS
    ST3 --> SS
    SS --> S
    
    %% LLM integration
    C <--> LLM
    
    %% Styling
    classDef recommended fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    classDef transport fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef server fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef client fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class SHTTP,ST3,CT3 recommended
    class STDIO,SSE,SHTTP transport
    class ST1,ST2,ST3,SS,S server
    class C,CS,CT1,CT2,CT3 client
```

# Data Flow and Execution

## 1. Connection Initialization

```mermaid

sequenceDiagram
    participant LLM
    participant Client
    participant Transport
    participant Server
    participant Tools
    
    Note over Client,Server: Initialization Phase
    Client->>Transport: Connect (stdio/sse/http)
    Transport->>Server: Establish Connection
    Client->>Server: Initialize Request
    Server->>Client: Initialize Response (capabilities)
    Note over Client,Server: Connection Ready
```

## 2. Tool Execution Flow

```mermaid

sequenceDiagram
    participant LLM
    participant Client
    participant Transport
    participant Server
    participant Tools
    
    Note over LLM,Tools: Tool Execution Flow
    
    LLM->>Client: Request available tools
    Client->>Transport: list_tools request (JSON-RPC)
    Transport->>Server: Forward request
    Server->>Tools: Get available tools
    Tools->>Server: Return tool definitions
    Server->>Transport: tools response (JSON-RPC)
    Transport->>Client: Forward response
    Client->>LLM: Available tools list
    
    Note over LLM,Tools: Tool Call Execution
    
    LLM->>Client: Call specific tool
    Client->>Transport: call_tool request (JSON-RPC)
    Note over Transport: Format: {"jsonrpc":"2.0","method":"tools/call","params":{"name":"tool_name","arguments":{...}}}
    Transport->>Server: Forward tool call
    Server->>Tools: Execute tool function
    Tools->>Tools: Process arguments & execute
    Tools->>Server: Return results
    Server->>Transport: tool result (JSON-RPC)
    Note over Transport: Format: {"jsonrpc":"2.0","result":{"content":[{"type":"text","text":"result"}]}}
    Transport->>Client: Forward results
    Client->>LLM: Tool execution results
```

## 3. Data Format
JSON-RPC Messages:

```json

// Request
{
  "jsonrpc": "2.0",
  "id": "req-123",
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {
      "location": "Madrid",
      "units": "celsius"
    }
  }
}

// Response
{
  "jsonrpc": "2.0",
  "id": "req-123",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Temperature in Madrid: 22°C, Sunny"
      }
    ]
  }
}
```

## 4. **Protocol Differences**

| Aspect | STDIO | SSE | Streamable HTTP |
|---------|-------|-----|-----------------|
| **Transport** | stdin/stdout | HTTP GET/POST | HTTP with sessions |
| **Format** | Line-by-line JSON-RPC | JSON-RPC over HTTP | JSON-RPC + SSE streams |
| **Sessions** | Implicit (process) | UUID in query params | Session ID in headers |
| **Scalability** | 1:1 process | Limited | Horizontal (multiple nodes) |
| **Resumability** | No | No | Yes (with EventStore) |
| **Production** | Not recommended | Deprecated | **RECOMMENDED** |

## 5. **Execution Location**

- **Functions/Tools**: Execute in the **MCP server process**
- **Validation**: Both client and server validate JSON-RPC messages
- **Serialization**: Data is serialized to JSON in transport
- **LLM**: Receives processed and formatted results from the client

**Production Recommendation:** Use **Streamable HTTP** for its robustness, scalability, and support for advanced features like resumability and distributed session handling.
