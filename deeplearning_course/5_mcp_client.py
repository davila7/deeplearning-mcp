from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdioimport import stdio_client

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="uv", # Executable
    args=["run", "research_server.py"], # Optional commnad line arguments
    env=None, # Optional enviroment variable
)

async def run():
    # Launch the server as subprocess
    # read is the stream that the client will use to read msgs from the server
    # write is the stream that client will use to write msgs to the server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection (1:1 connection with the server)
            await session.initialize()

            # List available tools
            tools = await session.list_tools()