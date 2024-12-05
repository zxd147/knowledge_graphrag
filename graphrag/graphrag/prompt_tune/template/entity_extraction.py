# 版权所有 (c) 2024 Microsoft Corporation.
# 根据 MIT 许可证授权

"""为实体提取微调提示词。"""

GRAPH_EXTRACTION_PROMPT = """
-目标-
给定一个与此活动可能相关的文本文件和一系列实体类型，从文本中识别出这些类型的所有实体，并识别出识别出的实体之间的所有关系。

-步骤-
1. 识别所有实体。对于每个识别出的实体，提取以下信息：
- entity_name：实体的名称，大写
- entity_type：以下类型之一：[{entity_types}]
- entity_description：实体属性和活动的全面描述
将每个实体格式化为 ("entity"{{tuple_delimiter}}<entity_name>{{tuple_delimiter}}<entity_type>{{tuple_delimiter}}<entity_description>)

2. 从步骤1中识别出的实体中，识别所有（source_entity, target_entity）对，它们彼此*明显相关*。
对于每一对相关实体，提取以下信息：
- source_entity：源实体的名称，如步骤1中识别的
- target_entity：目标实体的名称，如步骤1中识别的
- relationship_description：解释为什么你认为源实体和目标实体彼此相关
- relationship_strength：1到10之间的整数分数，表示源实体和目标实体之间的关系强度
将每个关系格式化为 ("relationship"{{tuple_delimiter}}<source_entity>{{tuple_delimiter}}<target_entity>{{tuple_delimiter}}<relationship_description>{{tuple_delimiter}}<relationship_strength>)

3. 返回输出为{language}语言，作为步骤1和2中识别出的所有实体和关系的单一列表。使用**{{record_delimiter}}**作为列表分隔符。

4. 如果需要翻译成{language}语言，只翻译描述，其他内容不变！

5. 完成后，输出{{completion_delimiter}}。

-示例-
######################
{examples}

-实际数据-
######################
entity_types: [{entity_types}]
text: {{input_text}}
######################
output:"""

GRAPH_EXTRACTION_JSON_PROMPT = """
-目标-
给定一个与此活动可能相关的文本文件和一系列实体类型，从文本中识别出这些类型的所有实体，并识别出识别出的实体之间的所有关系。

-步骤-
1. 识别所有实体。对于每个识别出的实体，提取以下信息：
- entity_name：实体的名称，大写
- entity_type：以下类型之一：[{entity_types}]
- entity_description：实体属性和活动的全面描述
将每个实体输出格式化为以下格式的JSON条目：

{{"name": <entity name>, "type": <type>, "description": <entity description>}}

2. 从步骤1中识别出的实体中，识别所有（source_entity, target_entity）对，它们彼此*明显相关*。
对于每一对相关实体，提取以下信息：
- source_entity：源实体的名称，如步骤1中识别的
- target_entity：目标实体的名称，如步骤1中识别的
- relationship_description：解释为什么你认为源实体和目标实体彼此相关
- relationship_strength：1到10之间的整数分数，表示源实体和目标实体之间的关系强度
将每个关系格式化为以下格式的JSON条目：

{{"source": <source_entity>, "target": <target_entity>, "relationship": <relationship_description>, "relationship_strength": <relationship_strength>}}

3. 返回输出为{language}语言，作为步骤1和2中识别出的所有JSON实体和关系的单一列表。

4. 如果需要翻译成{language}语言，只翻译描述，其他内容不变！

-示例-
######################
{examples}

-实际数据-
######################
entity_types: {entity_types}
text: {{input_text}}
######################
output:"""

EXAMPLE_EXTRACTION_TEMPLATE = """
示例 {n}：

entity_types: [{entity_types}]
text:
{input_text}
------------------------
output:
{output}
#############################

"""

UNTYPED_EXAMPLE_EXTRACTION_TEMPLATE = """
示例 {n}：

text:
{input_text}
------------------------
output:
{output}
#############################

"""


UNTYPED_GRAPH_EXTRACTION_PROMPT = """
-目标-
给定一个与此活动可能相关的文本文件，首先从文本中识别出所有必要的实体，以捕获文本中的信息和想法。
接下来，报告识别出的实体之间的所有关系。

-步骤-
1. 识别所有实体。对于每个识别出的实体，提取以下信息：
- entity_name：实体的名称，大写
- entity_type：为实体提出几个标签或类别。类别不应太具体，应尽可能通用。
- entity_description：实体属性和活动的全面描述
将每个实体格式化为 ("entity"{{tuple_delimiter}}<entity_name>{{tuple_delimiter}}<entity_type>{{tuple_delimiter}}<entity_description>)

2. 从步骤1中识别出的实体中，识别所有（source_entity, target_entity）对，它们彼此*明显相关*。
对于每一对相关实体，提取以下信息：
- source_entity：源实体的名称，如步骤1中识别的
- target_entity：目标实体的名称，如步骤1中识别的
- relationship_description：解释为什么你认为源实体和目标实体彼此相关
- relationship_strength：一个数值分数，表示源实体和目标实体之间的关系强度
将每个关系格式化为 ("relationship"{{tuple_delimiter}}<source_entity>{{tuple_delimiter}}<target_entity>{{tuple_delimiter}}<relationship_description>{{tuple_delimiter}}<relationship_strength>)

3. 返回输出为{language}语言，作为步骤1和2中识别出的所有实体和关系的单一列表。使用**{{record_delimiter}}**作为列表分隔符。

4. 如果需要翻译成{language}语言，只翻译描述，其他内容不变！

5. 完成后，输出{{completion_delimiter}}。

-示例-
######################
{examples}

-实际数据-
######################
text: {{input_text}}
######################
output:
"""
