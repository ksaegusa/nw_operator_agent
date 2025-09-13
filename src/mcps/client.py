from langchain_mcp_adapters.client import MultiServerMCPClient

class MCPClient():
    def __init__(self, mcps):
        self.client = MultiServerMCPClient(mcps)

    async def tools(self):
        return await self.client.get_tools()
