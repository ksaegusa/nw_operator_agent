from typing import TypedDict, Literal

from src.agents.base import BaseAgent
from src.models.netbox_agent_model import (
    ReflectionResult,
)
from src.prompts.prompt import *  # TODO: 読み込み方いまいちかなー
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from langgraph.constants import Send
from langgraph.graph.state import StateGraph, START, END
from langgraph.pregel import Pregel
from langgraph.prebuilt import ToolNode, tools_condition


# --------------------------------------------------------------------
# NOTE: Agentのステート
class NBRSAgentState(TypedDict):
    messages: list
    question: str
    plan: list
    answer: str
    challenge_count: int
    is_completed: bool

MAX_CHALLENGE_COUNT = 3
# --------------------------------------------------------------------
class NetBoxSearchAgent(BaseAgent):
    """NETBOXから情報収集をするエージェント"""

    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools

    # NOTE: nodeの定義ブロック ----------------------------------------
    #       NodeはreturnでStateを更新する
    def create_plan(self, state: NBRSAgentState):
        """情報取得計画を作成する"""
        messages = state["messages"]
        prompt_template = PromptTemplate.from_template(PLAN)

        chain = prompt_template | self.llm.bind_tools(self.tools)
        response = chain.invoke({"question": state["question"]})
        messages.append(response)

        return {"plan": response.content, "messages": messages}

    def execute_tool(self, state: NBRSAgentState):
        """ツールを利用する"""
        messages = state["messages"]
        prompt_template = PromptTemplate.from_template(TOOL_SELCT)

        chain = prompt_template | self.llm.bind_tools(self.tools)
        response = chain.invoke({"question": state["plan"]})
        messages.append(response)

        return {"messages": messages}

    def should_continue_exec_task_flow(self, state: NBRSAgentState) -> Literal["create_answer", "continue"]:
        """内省ループ"""
        if state["is_completed"] or state["challenge_count"] >= MAX_CHALLENGE_COUNT:
            return "create_answer"
        else:
            return "continue"

    def reflection_answer(self, state: NBRSAgentState):
        """回答を内省する"""
        messages = state["messages"]
        parser = PydanticOutputParser(pydantic_object=ReflectionResult)
        format_instructions = parser.get_format_instructions()
        prompt_template = PromptTemplate.from_template(REFLECTION_TEMPLATE)
        prompt = prompt_template.partial(format_instructions=format_instructions)

        chain = prompt | self.llm | parser
        reflection_result = chain.invoke({"messages": messages})

        return {
            "answer": state["messages"][-1].content,
            "is_completed": reflection_result.is_completed,
            "challenge_count": state["challenge_count"] + 1
        }

    def create_answer(self, state: NBRSAgentState):
        """最終回答を生成する"""
        prompt_template = PromptTemplate.from_template(CREATE_LAST_ANSWER)
        chain = prompt_template | self.llm
        response = chain.invoke({"question": state["answer"], "plan": state["plan"]})
        return {"answer": response.content}

    # NOTE: graph生成/実行ブロック ------------------------------------
    def create_graph(self) -> Pregel:
        graph = StateGraph(NBRSAgentState)

        # NOTE: ノード定義
        graph.add_node("create_plan", self.create_plan)
        graph.add_node("execute_tool", self.execute_tool)
        graph.add_node("tools", ToolNode(self.tools))
        graph.add_node("create_answer", self.create_answer)
        graph.add_node("reflection_answer", self.reflection_answer)

        # NOTE: エッジ定義
        graph.add_edge(START, "create_plan")
        graph.add_edge("create_plan", "execute_tool")
        graph.add_conditional_edges("execute_tool", tools_condition)
        graph.add_edge("tools", "reflection_answer")
        graph.add_conditional_edges(
            "reflection_answer",
            self.should_continue_exec_task_flow,
            {"continue": "execute_tool", "create_answer": "create_answer"},
        )
        graph.add_edge("create_answer", END)

        # NOTE: コンパイル
        app = graph.compile()

        return app

    async def run(self, input):
        app = self.create_graph()
        return await app.ainvoke(input)
