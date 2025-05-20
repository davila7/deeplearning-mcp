# Why Model Context Protocol?

**Models are only as good as the data given to them**

MCP is an open protocol that standardizes the way how your LLM aplication connect to and work with your **Tools and Data Sources**.

# Protocols

### Rest APIs
Standardize how web app interact with the backend.

### LSP
Standardize how IDEs interact with Language-specific tools.

### MCP
Standardize how LLM apps interact with external systems.

# Whitout MCP: Fragmented AI Development

```mermaid
graph LR
    %% AI App 1
    App1[AI App 1] --> A1[Custom implementation] --> B1[Custom prompt logic] --> C1[Custom tool calls] --> D1[Custom data access]

    %% AI App 2
    App2[AI App 2] --> A2[Custom implementation] --> B2[Custom prompt logic] --> C2[Custom tool calls] --> D2[Custom data access]

    %% AI App 3
    App3[AI App 3] --> A3[Custom implementation] --> B3[Custom prompt logic] --> C3[Custom tool calls] --> D3[Custom data access]

```

# With MCP: Standardized AI Development

```mermaid
graph LR
    subgraph MCP_Compatible_Application [MCP Compatible Application]
        LLM[LLM]
    end

    MCP_Compatible_Application --> DSMCP[Data Store MCP]
    MCP_Compatible_Application --> CRMMCP[CRM MCP Server]
    MCP_Compatible_Application --> VCSMCP[Version Control MCP Server]

    DSMCP --> DS[Data Store]
    CRMMCP --> CRMS[CRM Systems]
    VCSMCP --> VCS[Version Control Software]
```

MCP Servers are reusable by varius AI applications.

- For AI application developers: Coonect your app to any MCP server with 0 additional work.
- For tool or API developers: Build an MCP server once which can be adopted everywhere.
- For AI Application users: AI Application have extensive capabilities.
- For enterprises: Clear separation of concerns between AI product teams.

## Common Questions

- Who authors the MCP Server?
Anyon! Often the service provider itself will make their own MCP implementation. You can make a MCP server to wrap up access to some service.

- How is using an MCP Server different from just calling a service's API directly?
MCP servers provide tool schemas + functions.
If you want to directly call an API, you will be authoring those on your own.

- Sound like MCP Servers and tool use are the same thing?
MCP Servers provide tool schemas + functions already defined for you.