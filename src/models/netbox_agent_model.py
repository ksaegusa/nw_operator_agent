from pydantic import BaseModel, Field

class ReflectionResult(BaseModel):
    advice: str = Field(
        ...,
        description=(
            "評価がNGの場合は、別のツールを試す、なぜNGなのかとどうしたら改善できるかを考えアドバイスを作成してください。",
            "アドバイスの内容は過去のアドバイスと計画内の他のタスクと重複しないようにしてください。",
            "アドバイスの内容をもとにツール選択・実行からやり直します。",
        ),
    )
    is_completed: bool = Field(
        ...,
        description="ツールの実行結果と回答から、タスクに対して正しく回答できているかの評価結果",
    )
