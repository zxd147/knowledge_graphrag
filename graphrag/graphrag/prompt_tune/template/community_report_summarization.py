# 版权所有 (c) 2024 Microsoft Corporation.
# 根据 MIT 许可证授权

"""为社区报告摘要微调提示词。"""

COMMUNITY_REPORT_SUMMARIZATION_PROMPT = """
{persona}

# 目标
以{role}的身份撰写一份全面的社区评估报告。报告内容包括社区的关键实体和关系概览。

# 报告结构
报告应包括以下部分：
- 标题：代表社区关键实体的社区名称 - 标题应简短但具体。如果可能，标题中包括代表性的命名实体。
- 摘要：社区整体结构的执行摘要，其实体如何相互关联，以及与其实体相关的重大点。
- 报告评级：{report_rating_description}
- 评级解释：给出评级的单句解释。
- 详细发现：关于社区的5-10个关键见解的列表。每个见解应有一个简短的摘要，然后是多段解释性文本，根据下面的依据规则进行。要全面。

将输出作为格式良好的 JSON 格式字符串返回。不要使用任何不必要的转义序列。输出应为一个可以被 json.loads 解析的单个 JSON 对象。
    {{
        "title": "<报告标题>",
        "summary": "<执行摘要>",
        "rating": <威胁严重性评级>,
        "rating_explanation": "<评级解释>"
        "findings": "[{{"summary":"<见解1摘要>", "explanation": "<见解1解释"}}, {{"summary":"<见解2摘要>", "explanation": "<见解2解释"}}]"
    }}

# 依据规则
每个段落后都应添加数据记录引用，如果段落的内容源自一个或多个数据记录。引用格式为：[records: <记录来源> (<记录ID列表>, ...<记录来源> (<记录ID列表>)]。如果有超过10个数据记录，显示最相关的前10个记录。
每个段落应包含多个解释性句子和具体的例子以及特定的命名实体。所有段落都必须在开始和结束时有这些引用。如果没有相关的角色或记录，使用"NONE"。一切内容应使用{language}语言。

示例段落，包含引用添加：
这是输出文本的一个段落 [records: 实体 (1, 2, 3), 声明 (2, 5), 关系 (10, 12)]

# 示例输入
-----------
文本：

实体

id, 实体, 描述
5, ABILA CITY PARK, Abila City Park 是 POK 集会的地点

关系

id, 来源, 目标, 描述
37, ABILA CITY PARK, POK RALLY, Abila City Park 是 POK 集会的地点
38, ABILA CITY PARK, POK, POK 正在 Abila City Park 举行集会
39, ABILA CITY PARK, POKRALLY, POK 集会正在 Abila City Park 举行
40, ABILA CITY PARK, CENTRAL BULLETIN, Central Bulletin 正在报道在 Abila City Park 举行的 POK 集会

输出：
{{
    "title": "Abila City Park 和 POK 集会",
    "summary": "该社区围绕 Abila City Park 展开，这里是 POK 集会的地点。公园与 POK、POKRALLY 和 Central Bulletin 有关联，所有这些都与集会事件有关。",
    "rating": 5.0,
    "rating_explanation": "由于 POK 集会期间可能出现的不安或冲突，影响评级为中等。",
    "findings": [
        {{
            "summary": "Abila City Park 作为中心地点",
            "explanation": "Abila City Park 是这个社区的中心实体，是 POK 集会的地点。这个公园是所有其他实体的共同联系点，表明其在社区中的重要性。公园与集会的关联可能会导致诸如公共秩序混乱或冲突等问题，这取决于集会的性质和它所引发的反应。[records: 实体 (5), 关系 (37, 38, 39, 40)]"
        }},
        {{
            "summary": "POK 在社区中的角色",
            "explanation": "POK 是这个社区的另一个关键实体，是 Abila City Park 集会的组织者。POK 及其集会的性质可能是潜在的威胁源，这取决于他们的目标和所引发反应。POK 与公园之间的关系对于理解这个社区的动态至关重要。[records: 关系 (38)]"
        }},
        {{
            "summary": "POKRALLY 作为重大事件",
            "explanation": "POKRALLY 是在 Abila City Park 举行的重大事件。这个事件是社区动态的关键因素，可能是潜在的威胁源，这取决于集会的性质和它所引发的反应。集会与公园之间的关系对于理解这个社区的动态至关重要。[records: 关系 (39)]"
        }},
        {{
            "summary": "Central Bulletin 的角色",
            "explanation": "Central Bulletin 正在报道在 Abila City Park 举行的 POK 集会。这表明该事件已经吸引了媒体的注意，这可能会放大其对社区的影响。Central Bulletin 在塑造公众对事件和涉及实体的看法方面可能具有重要作用。[records: 关系 (40)]"
        }}
    ]
}}

# 实际数据

使用以下文本作为您回答的依据。不要在回答中编造任何内容。

文本：
{{input_text}}
输出："""