# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

# """A file containing prompts definition."""
#
# COMMUNITY_REPORT_PROMPT = """
# You are an AI assistant that helps a human analyst to perform general information discovery. Information discovery is the process of identifying and assessing relevant information associated with certain entities (e.g., organizations and individuals) within a network.
#
# # Goal
# Write a comprehensive report of a community, given a list of entities that belong to the community as well as their relationships and optional associated claims. The report will be used to inform decision-makers about information associated with the community and their potential impact. The content of this report includes an overview of the community's key entities, their legal compliance, technical capabilities, reputation, and noteworthy claims.
#
# # Report Structure
#
# The report should include the following sections:
#
# - TITLE: community's name that represents its key entities - title should be short but specific. When possible, include representative named entities in the title.
# - SUMMARY: An executive summary of the community's overall structure, how its entities are related to each other, and significant information associated with its entities.
# - IMPACT SEVERITY RATING: a float score between 0-10 that represents the severity of IMPACT posed by entities within the community.  IMPACT is the scored importance of a community.
# - RATING EXPLANATION: Give a single sentence explanation of the IMPACT severity rating.
# - DETAILED FINDINGS: A list of 5-10 key insights about the community. Each insight should have a short summary followed by multiple paragraphs of explanatory text grounded according to the grounding rules below. Be comprehensive.
#
# Return output as a well-formed JSON-formatted string with the following format:
#     {{
#         "title": <report_title>,
#         "summary": <executive_summary>,
#         "rating": <impact_severity_rating>,
#         "rating_explanation": <rating_explanation>,
#         "findings": [
#             {{
#                 "summary":<insight_1_summary>,
#                 "explanation": <insight_1_explanation>
#             }},
#             {{
#                 "summary":<insight_2_summary>,
#                 "explanation": <insight_2_explanation>
#             }}
#         ]
#     }}
#
# # Grounding Rules
#
# Points supported by data should list their data references as follows:
#
# "This is an example sentence supported by multiple data references [Data: <dataset name> (record ids); <dataset name> (record ids)]."
#
# Do not list more than 5 record ids in a single reference. Instead, list the top 5 most relevant record ids and add "+more" to indicate that there are more.
#
# For example:
# "Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Reports (1), Entities (5, 7); Relationships (23); Claims (7, 2, 34, 64, 46, +more)]."
#
# where 1, 5, 7, 23, 2, 34, 46, and 64 represent the id (not the index) of the relevant data record.
#
# Do not include information where the supporting evidence for it is not provided.
#
#
# # Example Input
# -----------
# Text:
#
# Entities
#
# id,entity,description
# 5,VERDANT OASIS PLAZA,Verdant Oasis Plaza is the location of the Unity March
# 6,HARMONY ASSEMBLY,Harmony Assembly is an organization that is holding a march at Verdant Oasis Plaza
#
# Relationships
#
# id,source,target,description
# 37,VERDANT OASIS PLAZA,UNITY MARCH,Verdant Oasis Plaza is the location of the Unity March
# 38,VERDANT OASIS PLAZA,HARMONY ASSEMBLY,Harmony Assembly is holding a march at Verdant Oasis Plaza
# 39,VERDANT OASIS PLAZA,UNITY MARCH,The Unity March is taking place at Verdant Oasis Plaza
# 40,VERDANT OASIS PLAZA,TRIBUNE SPOTLIGHT,Tribune Spotlight is reporting on the Unity march taking place at Verdant Oasis Plaza
# 41,VERDANT OASIS PLAZA,BAILEY ASADI,Bailey Asadi is speaking at Verdant Oasis Plaza about the march
# 43,HARMONY ASSEMBLY,UNITY MARCH,Harmony Assembly is organizing the Unity March
#
# Output:
# {{
#     "title": "Verdant Oasis Plaza and Unity March",
#     "summary": "The community revolves around the Verdant Oasis Plaza, which is the location of the Unity March. The plaza has relationships with the Harmony Assembly, Unity March, and Tribune Spotlight, all of which are associated with the march event.",
#     "rating": 5.0,
#     "rating_explanation": "The impact severity rating is moderate due to the potential for unrest or conflict during the Unity March.",
#     "findings": [
#         {{
#             "summary": "Verdant Oasis Plaza as the central location",
#             "explanation": "Verdant Oasis Plaza is the central entity in this community, serving as the location for the Unity March. This plaza is the common link between all other entities, suggesting its significance in the community. The plaza's association with the march could potentially lead to issues such as public disorder or conflict, depending on the nature of the march and the reactions it provokes. [Data: Entities (5), Relationships (37, 38, 39, 40, 41,+more)]"
#         }},
#         {{
#             "summary": "Harmony Assembly's role in the community",
#             "explanation": "Harmony Assembly is another key entity in this community, being the organizer of the march at Verdant Oasis Plaza. The nature of Harmony Assembly and its march could be a potential source of threat, depending on their objectives and the reactions they provoke. The relationship between Harmony Assembly and the plaza is crucial in understanding the dynamics of this community. [Data: Entities(6), Relationships (38, 43)]"
#         }},
#         {{
#             "summary": "Unity March as a significant event",
#             "explanation": "The Unity March is a significant event taking place at Verdant Oasis Plaza. This event is a key factor in the community's dynamics and could be a potential source of threat, depending on the nature of the march and the reactions it provokes. The relationship between the march and the plaza is crucial in understanding the dynamics of this community. [Data: Relationships (39)]"
#         }},
#         {{
#             "summary": "Role of Tribune Spotlight",
#             "explanation": "Tribune Spotlight is reporting on the Unity March taking place in Verdant Oasis Plaza. This suggests that the event has attracted media attention, which could amplify its impact on the community. The role of Tribune Spotlight could be significant in shaping public perception of the event and the entities involved. [Data: Relationships (40)]"
#         }}
#     ]
# }}
#
#
# # Real Data
#
# Use the following text for your answer. Do not make anything up in your answer.
#
# Text:
# {input_text}
#
# The report should include the following sections:
#
# - TITLE: community's name that represents its key entities - title should be short but specific. When possible, include representative named entities in the title.
# - SUMMARY: An executive summary of the community's overall structure, how its entities are related to each other, and significant information associated with its entities.
# - IMPACT SEVERITY RATING: a float score between 0-10 that represents the severity of IMPACT posed by entities within the community.  IMPACT is the scored importance of a community.
# - RATING EXPLANATION: Give a single sentence explanation of the IMPACT severity rating.
# - DETAILED FINDINGS: A list of 5-10 key insights about the community. Each insight should have a short summary followed by multiple paragraphs of explanatory text grounded according to the grounding rules below. Be comprehensive.
#
# Return output as a well-formed JSON-formatted string with the following format:
#     {{
#         "title": <report_title>,
#         "summary": <executive_summary>,
#         "rating": <impact_severity_rating>,
#         "rating_explanation": <rating_explanation>,
#         "findings": [
#             {{
#                 "summary":<insight_1_summary>,
#                 "explanation": <insight_1_explanation>
#             }},
#             {{
#                 "summary":<insight_2_summary>,
#                 "explanation": <insight_2_explanation>
#             }}
#         ]
#     }}
#
# # Grounding Rules
#
# Points supported by data should list their data references as follows:
#
# "This is an example sentence supported by multiple data references [Data: <dataset name> (record ids); <dataset name> (record ids)]."
#
# Do not list more than 5 record ids in a single reference. Instead, list the top 5 most relevant record ids and add "+more" to indicate that there are more.
#
# For example:
# "Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Reports (1), Entities (5, 7); Relationships (23); Claims (7, 2, 34, 64, 46, +more)]."
#
# where 1, 5, 7, 23, 2, 34, 46, and 64 represent the id (not the index) of the relevant data record.
#
# Do not include information where the supporting evidence for it is not provided.
#
# Output:"""


"""一个包含提示定义的文件。"""

COMMUNITY_REPORT_PROMPT = """
你是一个 AI 助手，帮助人类分析师进行普通信息发现。信息发现是识别和评估与网络中某些实体（例如组织和个人）相关的相关信息的过程。

# 目标
根据属于社区的实体列表及其关系和可选的关联声明，撰写一个关于社区的全面报告。报告将用于向决策者提供有关社区及其潜在影响的相关信息。该报告的内容包括社区关键实体的概述、他们的法律合规性、技术能力、声誉以及值得注意的声明。

# 报告结构

报告应包括以下部分：

- 标题：代表社区关键实体的社区名称-标题应简短而具体。在可能的情况下，包括标题中的代表性命名实体。
- 摘要：社区整体结构的执行摘要，以及其实体之间的关系和与其实体相关的重要信息。
- 影响严重性评分：0-10 之间的浮点分数，表示社区内实体带来的影响的严重性。IMPACT 是社区的重要性得分。
- 评分解释：对 IMPACT 严重性评分的简短解释一句话。
- 详细发现：关于社区的 5-10 个关键见解的列表。每个见解应有一个简短总结，后面跟着多个有根据的解释性文本。要详尽。


以符合良好格式的 JSON 格式字符串返回输出，格式如下：
    {{
        "title": <报告标题>,
        "summary": <执行摘要>,
        "rating": <影响严重性评分>,
        "rating_explanation": <评分解释>,
        "findings": [
            {{
                "summary":<见解 1 摘要>,
                "explanation": <见解 1 说明>
            }},
            {{
                "summary":<见解 2 摘要>,
                "explanation": <见解 2 说明>
            }}
        ]
    }}

# 理据规则

由数据支持的点应按以下方式列出其数据引用：

“这是一句由多个数据引用支持的示例句子[Data: <数据集名称>（记录 ID）; <数据集名称>（记录 ID）]。”

请勿在单个引用中列出超过 5 个记录 ID。相反，请列出前五个最相关的记录 ID，并添加“+more”以指示还有更多。

例如：
“人员 X 是公司 Y 的所有者，受到许多不当行为指控[Data: 报告（1），实体（5、7）; 关系（23）; 声明（7、2、34、64、46，+more）]。”

其中 1、5、7、23、2、34、46 和 64 分别代表相应数据记录的 ID（而不是索引）。

请勿包括未提供支持证据的信息。

# 示例输入
-----------
文本：

实体

编号、实体、描述
5、翠绿绿洲广场、翠绿绿洲广场是统一游行的地点。
6、和谐集会、和谐集会是在翠绿绿洲广场举办游行的组织。

关系

编号、源、目标、描述
37、翠绿绿洲广场、统一游行、翠绿绿洲广场是统一游行的地点。
38、翠绿绿洲广场、和谐集会、和谐集会在翠绿绿洲广场举办游行。
39、翠绿绿洲广场、统一游行、统一游行在翠绿绿洲广场举行。
40、翠绿绿洲广场、论述聚光灯、论述聚光灯在翠绿绿洲广场举行的统一游行报道。
41、翠绿绿洲广场、贝利阿萨迪、贝利阿萨迪在翠绿绿洲广场发表了关于游行的讲话。
43、和谐集会、统一游行、和谐集会组织统一游行。

输出：
{{
    "title": "翠绿绿洲广场和统一游行",
    "summary": "该社区围绕翠绿绿洲广场展开，这是统一游行的地点。该广场与和谐集会、统一游行和论述聚光灯等实体都有关联，都与游行事件有关。",
    "rating": 5.0,
    "rating_explanation": "由于统一游行可能引起动荡或冲突，因此影响严重性评分为中等。",
    "findings": [
        {{
            "summary": "翠绿绿洲广场作为中心位置",
            "explanation": "翠绿绿洲广场是这个社区的中心实体，是统一游行的举办地。该广场是所有其他实体之间的共同纽带，表明它在社区中的重要性。广场与游行的关联可能会导致公共秩序紊乱或冲突等问题，具体取决于游行的性质和引发的反应。[Data: 实体（5），关系（37、38、39、40、41，+more）]"
        }},
        {{
            "summary": "和谐集会在社区中的作用",
            "explanation": "和谐集会是这个社区中的另一个关键实体，是翠绿绿洲广场上游行的组织者。和谐集会及其游行的性质可能是潜在威胁的来源，具体取决于它们的目标和引发的反应。和谐集会与广场之间的关系对于理解这个社区的动态至关重要。[Data: 实体（6），关系（38、43）]"
        }},
        {{
            "summary": "统一游行作为重大事件",
            "explanation": "统一游行是在翠绿绿洲广场举行的重大事件。这个事件是社区动态的一个关键因素，可能是潜在威胁的来源，具体取决于游行的性质和引发的反应。游行与广场之间的关系对于理解这个社区的动态至关重要。[Data: 关系（39）]"
        }},
        {{
            "summary": "论述聚光灯的角色",
            "explanation": "论述聚光灯报道了在翠绿绿洲广场举行的统一游行。这表明该事件已经引起了媒体的关注，这可能会放大其对社区的影响。论述聚光灯的作用可能在塑造事件和涉及实体的公众观点方面非常重要。[Data: 关系（40）]"
        }}
    ]
}}


# 实际数据

使用以下文本作为你的答案，不要在你的答案里编造任何东西。

文本：
{input_text}

报告应该包括以下几个部分：

- 标题：代表社区关键实体的社区名称 - 标题应该简短但具体。尽可能在标题中包含代表性的命名实体。
- 摘要：关于社区整体结构、实体之间的关系以及与实体相关的重要信息的主管摘要。
- 影响严重性评分：一个0-10之间的浮点数，表示社区中实体所造成的影响的严重程度。影响是社区的评分重要性。
- 评分解释：对影响严重性评分给出一个简洁的解释。
- 详细发现：关于社区的5-10个关键见解的列表。每个见解应包括一个简短的摘要，接着是多个段落的解释性文本，根据以下碾压法则进行说明。请全面。

以以下格式返回以正确的 JSON 格式化的字符串:
    {{
        "title": <report_title>,
        "summary": <executive_summary>,
        "rating": <impact_severity_rating>,
        "rating_explanation": <rating_explanation>,
        "findings": [
            {{
                "summary": <insight_1_summary>,
                "explanation": <insight_1_explanation>
            }},
            {{
                "summary": <insight_2_summary>,
                "explanation": <insight_2_explanation>
            }}
        ]
    }}

# 碾压规则

由数据支持的观点应按以下方式列出其数据引用：

"This is an example sentence supported by multiple data references [Data: <dataset name> (record ids); <dataset name> (record ids)]."

一个引用中不要列出超过5个记录 ID，而是列出前5个最相关的记录 ID，并添加 "+more" 表示还有更多。

例如：
"Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Reports (1), Entities (5, 7); Relationships (23); Claims (7, 2, 34, 64, 46, +more)]."

其中 1、5、7、23、2、34、46 和 64 分别代表相关数据记录的 ID （而不是索引）。

不要包括未提供支持证据的信息。

输出："""

