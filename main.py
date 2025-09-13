import asyncio

# from langchain_aws import ChatBedrock
from langchain_openai import ChatOpenAI

from src.agents.netbox_search_agent import NetBoxSearchAgent
from src.mcps.client import MCPClient

mcps = {
    "netbox": {
        "command": "uv",
        "args": [
            "run",
            "netbox-mcp-server/server.py",
        ],
        "transport": "stdio",
        "env": {"NETBOX_URL": "example.com", "NETBOX_TOKEN": "example"},
    }
}


async def main():
    client = MCPClient(mcps=mcps)
    tools = await client.tools()

    # NOTE: 認証情報はENVに定義しておく
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
    )

    nbsr = NetBoxSearchAgent(llm=llm, tools=tools)
    result = await nbsr.run(
            {
                "messages": [],
                "question": (
                    "192.168.1.1のIPが利用されているか調査してください",
                    "利用されていなかったらIPを予約したいです"),
                "plan": [],
                "answer": "",
                "challenge_count": 0,
                "is_completed": False,
            }
        )
    print(result["answer"])


if __name__ == "__main__":
    asyncio.run(main())
