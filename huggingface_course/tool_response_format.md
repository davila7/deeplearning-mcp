# Tool Response Format in MCP Python SDK

When you have a tool that calls an API, the response from the tool to the model must follow the MCP protocol structure. Here's the format:

1. CallToolResult Structure
The final response is wrapped in a CallToolResult object which contains:

content: A list of content objects (TextContent, ImageContent, or EmbeddedResource)
isError: A boolean indicating if the operation failed (defaults to False)
2. Content Types
Your tool can return any of these content types: