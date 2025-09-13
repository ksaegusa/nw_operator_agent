PLAN = """
利用かなうなツールから計画を練ってください
ツールは利用せず計画の身を練ります
Input:
{question}
"""
TOOL_SELCT = """
下記課題を解決するためのツールを選択してください
{question}
"""

REFLECTION_TEMPLATE = """
Input:
内省してくださいな
{messages}

Output:
{format_instructions}"""

CREATE_LAST_ANSWER="""
計画に対して目的が達成できているか最終報告をしてください。

計画:
{plan}

実行結果:
{question}
"""