# MCP Architecture


## Client-Server Architecture


```mermaid
graph LR
    subgraph Host [Host]
        MC1[MC Client]
        MC2[MC Client]
        MC3[MC Client]
    end

    Proto1[MCP Protocol]
    Proto2[MCP Protocol]
    Proto3[MCP Protocol]

    Server1[MCP Server]
    Server2[MCP Server]
    Server3[MCP Server]

    Proto1 --> MC1
    Proto2 --> MC2
    Proto3 --> MC3

    Proto1 --> Server1
    Proto2 --> Server2
    Proto3 --> Server3

```

