# Why Model Context Protocol?

**Models are only as good as the data given to them**

MCP is an open protocol that standardizes the way how your LLM aplication connect to and work with your **Tools and Data Sources**.

# Protocols

## Rest APIs
Standardize how web app interact with the backend.

## LSP
Standardize how IDEs interact with Language-specific tools.

## MCP
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

    %% For spacing and alignment
    App2 -->| | App3
```