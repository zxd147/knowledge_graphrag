# 版权所有 (c) 2024 Microsoft Corporation.
# 根据MIT许可授权

"""为实体关系生成微调提示词。"""

ENTITY_RELATIONSHIPS_GENERATION_PROMPT = """
-目标-
给定一个与此活动可能相关的文本文件和一个实体类型列表，识别文本中所有这些类型的实体，并识别所有已识别实体之间的关系。

-步骤-
1. 识别所有实体。对于每个已识别的实体，提取以下信息：
- entity_name: 实体的名称，大写
- entity_type: 以下类型之一：[{entity_types}]
- entity_description: 实体属性和活动的全面描述
将每个实体格式化为 ("entity"{{tuple_delimiter}}<entity_name>{{tuple_delimiter}}<entity_type>{{tuple_delimiter}}<entity_description>)

2. 从步骤1中识别的实体中，识别所有（source_entity, target_entity）对，这些对彼此*明显相关*。
对于每对相关实体，提取以下信息：
- source_entity: 源实体的名称，如步骤1中识别的
- target_entity: 目标实体的名称，如步骤1中识别的
- relationship_description: 解释为什么你认为源实体和目标实体彼此相关
- relationship_strength: 一个介于1到10之间的整数分数，表示源实体和目标实体之间的关系强度
将每个关系格式化为 ("relationship"{{tuple_delimiter}}<source_entity>{{tuple_delimiter}}<target_entity>{{tuple_delimiter}}<relationship_description>{{tuple_delimiter}}<relationship_strength>)

3. 返回输出为{language}，作为步骤1和2中识别的所有实体和关系的单个列表。使用{{record_delimiter}}作为列表分隔符。

4. 如果你需要翻译成{language}，只翻译描述，其他什么都不要翻译！

5. 完成后，输出{{completion_delimiter}}。

######################
-示例-
######################
示例 1:
实体类型：ORGANIZATION,PERSON
文本：
Verdantis的中央机构计划在周一和周四开会，该机构计划在周四下午1:30 PDT发布其最新的政策决定，随后举行新闻发布会，中央机构主席马丁·史密斯将回答问题。投资者预计市场战略委员会将保持其基准利率在3.5%-3.75%的范围内稳定。
######################
输出：
("entity"{{tuple_delimiter}}CENTRAL INSTITUTION{{tuple_delimiter}}ORGANIZATION{{tuple_delimiter}}中央机构是Verdantis的联邦储备系统，它在周一和周四设定利率)
{{record_delimiter}}
("entity"{{tuple_delimiter}}MARTIN SMITH{{tuple_delimiter}}PERSON{{tuple_delimiter}}马丁·史密斯是中央机构的主席)
{{record_delimiter}}
("entity"{{tuple_delimiter}}MARKET STRATEGY COMMITTEE{{tuple_delimiter}}ORGANIZATION{{tuple_delimiter}}中央机构委员会对利率和Verdantis货币供应量的增长做出关键决定)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}MARTIN SMITH{{tuple_delimiter}}CENTRAL INSTITUTION{{tuple_delimiter}}马丁·史密斯是中央机构的主席，将在新闻发布会上回答问题{{tuple_delimiter}}9)
{{completion_delimiter}}

######################
示例 2:
实体类型：ORGANIZATION
文本：
TechGlobal（TG）的股票在周四全球交易所的首日上市时飙升。但IPO专家警告说，这家半导体公司的公开市场首次亮相并不能说明其他新上市公司可能的表现。

TechGlobal，一家以前是上市公司，于2014年被Vision Holdings私有化。这家成熟的芯片设计公司表示，它为85%的高端智能手机提供动力。
######################
输出：
("entity"{{tuple_delimiter}}TECHGLOBAL{{tuple_delimiter}}ORGANIZATION{{tuple_delimiter}}TechGlobal是现在在全球交易所上市的股票，它为85%的高端智能手机提供动力)
{{record_delimiter}}
("entity"{{tuple_delimiter}}VISION HOLDINGS{{tuple_delimiter}}ORGANIZATION{{tuple_delimiter}}Vision Holdings是一家以前拥有TechGlobal的公司)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}TECHGLOBAL{{tuple_delimiter}}VISION HOLDINGS{{tuple_delimiter}}Vision Holdings从2014年至今曾经拥有TechGlobal{{tuple_delimiter}}5)
{{completion_delimiter}}

######################
示例 3:
实体类型：ORGANIZATION,GEO,PERSON
文本：
五名被监禁在Firuzabad的Aurelians，被广泛视为人质，正在返回Aurelia的途中。

由Quintara策划的交换在80亿美元的Firuzi资金转移到Quintara首都Krohaara的金融机构时完成。

在Firuzabad首都Tiruzia发起的交换导致四名男性和一名也是Firuzi国民的女性登上了飞往Krohaara的包机。

他们受到Aurelian高级官员的欢迎，现在正在前往Aurelia首都Cashion的途中。

Aurelians包括39岁的商人塞缪尔·纳马拉，他一直被关押在Tiruzia的Alhamia监狱，以及59岁的记者Durke Bataglani和53岁的环保主义者Meggie Tazbah，她也持有Bratinas国籍。
######################
输出：
("entity"{{tuple_delimiter}}FIRUZABAD{{tuple_delimiter}}GEO{{tuple_delimiter}}Firuzabad扣押了Aurelians作为人质)
{{record_delimiter}}
("entity"{{tuple_delimiter}}AURELIA{{tuple_delimiter}}GEO{{tuple_delimiter}}寻求释放人质的国家)
{{record_delimiter}}
("entity"{{tuple_delimiter}}QUINTARA{{tuple_delimiter}}GEO{{tuple_delimiter}}谈判交换资金以换取人质的国家)
{{record_delimiter}}
{{record_delimiter}}
("entity"{{tuple_delimiter}}TIRUZIA{{tuple_delimiter}}GEO{{tuple_delimiter}}Aurelians被关押的Firuzabad首都)
{{record_delimiter}}
("entity"{{tuple_delimiter}}KROHAARA{{tuple_delimiter}}GEO{{tuple_delimiter}}Quintara的首都城市)
{{record_delimiter}}
("entity"{{tuple_delimiter}}CASHION{{tuple_delimiter}}GEO{{tuple_delimiter}}Aurelia的首都城市)
{{record_delimiter}}
("entity"{{tuple_delimiter}}SAMUEL NAMARA{{tuple_delimiter}}PERSON{{tuple_delimiter}}在Tiruzia的Alhamia监狱度过时间的Aurelian)
{{record_delimiter}}
("entity"{{tuple_delimiter}}ALHAMIA PRISON{{tuple_delimiter}}GEO{{tuple_delimiter}}Tiruzia的监狱)
{{record_delimiter}}
("entity"{{tuple_delimiter}}DURKE BATAGLANI{{tuple_delimiter}}PERSON{{tuple_delimiter}}被扣为人质的Aurelian记者)
{{record_delimiter}}
("entity"{{tuple_delimiter}}MEGGIE TAZBAH{{tuple_delimiter}}PERSON{{tuple_delimiter}}持有Bratinas国籍的环保主义者，被扣为人质)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}FIRUZABAD{{tuple_delimiter}}AURELIA{{tuple_delimiter}}Firuzabad与Aurelia就人质交换进行谈判{{tuple_delimiter}}2)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}QUINTARA{{tuple_delimiter}}AURELIA{{tuple_delimiter}}Quintara促成了Firuzabad和Aurelia之间的人质交换{{tuple_delimiter}}2)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}QUINTARA{{tuple_delimiter}}FIRUZABAD{{tuple_delimiter}}Quintara促成了Firuzabad和Aurelia之间的人质交换{{tuple_delimiter}}2)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}SAMUEL NAMARA{{tuple_delimiter}}ALHAMIA PRISON{{tuple_delimiter}}Samuel Namara是Alhamia监狱的囚犯{{tuple_delimiter}}8)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}SAMUEL NAMARA{{tuple_delimiter}}MEGGIE TAZBAH{{tuple_delimiter}}Samuel Namara和Meggie Tazbah在同一人质释放中被交换{{tuple_delimiter}}2)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}SAMUEL NAMARA{{tuple_delimiter}}DURKE BATAGLANI{{tuple_delimiter}}Samuel Namara和Durke Bataglani在同一人质释放中被交换{{tuple_delimiter}}2)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}MEGGIE TAZBAH{{tuple_delimiter}}DURKE BATAGLANI{{tuple_delimiter}}Meggie Tazbah和Durke Bataglani在同一人质释放中被交换{{tuple_delimiter}}2)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}SAMUEL NAMARA{{tuple_delimiter}}FIRUZABAD{{tuple_delimiter}}Samuel Namara是Firuzabad的人质{{tuple_delimiter}}2)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}MEGGIE TAZBAH{{tuple_delimiter}}FIRUZABAD{{tuple_delimiter}}Meggie Tazbah是Firuzabad的人质{{tuple_delimiter}}2)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}DURKE BATAGLANI{{tuple_delimiter}}FIRUZABAD{{tuple_delimiter}}Durke Bataglani是Firuzabad的人质{{tuple_delimiter}}2)
{{completion_delimiter}}

-真实数据-
######################
实体类型：{entity_types}
文本：{input_text}
######################
输出：
"""

ENTITY_RELATIONSHIPS_GENERATION_JSON_PROMPT = """
-目标-
给定一个可能与此活动相关的文本文件和实体类型列表，识别文本中所有这些类型的实体以及识别出的实体之间的关系。

-步骤-
1. 识别所有实体。对于每个已识别的实体，提取以下信息：
- entity_name: 实体的名称，大写
- entity_type: 以下类型之一：[{entity_types}]
- entity_description: 实体属性和活动的全面描述

将每个实体输出格式化为以下格式的JSON条目：

{{"name": "<entity name>", "type": "<type>", "description": "<entity description>"}}

2. 从步骤1中识别的实体中，识别所有（source_entity, target_entity）对，这些对彼此*明显相关*。
对于每对相关实体，提取以下信息：
- source_entity: 源实体的名称，如步骤1中识别的
- target_entity: 目标实体的名称，如步骤1中识别的
- relationship_description: 解释为什么你认为源实体和目标实体彼此相关
- relationship_strength: 一个介于1到10之间的整数分数，表示源实体和目标实体之间的关系强度

将每个关系格式化为以下格式的JSON条目：

{{"source": "<source_entity>", "target": "<target_entity>", "relationship": "<relationship_description>", "relationship_strength": <relationship_strength>}}

3. 返回输出为{language}，作为步骤1和2中识别的所有JSON实体和关系的单个列表。

4. 如果你需要翻译成{language}，只翻译描述，其他什么都不要翻译！

######################
-示例-
######################
示例 1:
文本：
Verdantis的中央机构计划在周一和周四开会，该机构计划在周四下午1:30 PDT发布其最新的政策决定，随后举行新闻发布会，中央机构主席马丁·史密斯将回答问题。投资者预计市场战略委员会将保持其基准利率在3.5%-3.75%的范围内稳定。
######################
输出：
[
  {{"name": "CENTRAL INSTITUTION", "type": "ORGANIZATION", "description": "中央机构是Verdantis的联邦储备系统，它在周一和周四设定利率"}},
  {{"name": "MARTIN SMITH", "type": "PERSON", "description": "马丁·史密斯是中央机构的主席"}},
  {{"name": "MARKET STRATEGY COMMITTEE", "type": "ORGANIZATION", "description": "中央机构委员会对利率和Verdantis货币供应量的增长做出关键决定"}},
  {{"source": "MARTIN SMITH", "target": "CENTRAL INSTITUTION", "relationship": "马丁·史密斯是中央机构的主席，将在新闻发布会上回答问题", "relationship_strength": 9}}
]

######################
示例 2:
文本：
TechGlobal（TG）的股票在周四全球交易所的首日上市时飙升。但IPO专家警告说，这家半导体公司的公开市场首次亮相并不能说明其他新上市公司可能的表现。

TechGlobal，一家以前是上市公司，于2014年被Vision Holdings私有化。这家成熟的芯片设计公司表示，它为85%的高端智能手机提供动力。
######################
输出：
[
  {{"name": "TECHGLOBAL", "type": "ORGANIZATION", "description": "TechGlobal是现在在全球交易所上市的股票，它为85%的高端智能手机提供动力"}},
  {{"name": "VISION HOLDINGS", "type": "ORGANIZATION", "description": "Vision Holdings是一家以前拥有TechGlobal的公司"}},
  {{"source": "TECHGLOBAL", "target": "VISION HOLDINGS", "relationship": "Vision Holdings从2014年至今曾经拥有TechGlobal", "relationship_strength": 5}}
]

######################
示例 3:
文本：
五名被监禁在Firuzabad的Aurelians，被广泛视为人质，正在返回Aurelia的途中。

由Quintara策划的交换在80亿美元的Firuzi资金转移到Quintara首都Krohaara的金融机构时完成。

在Firuzabad首都Tiruzia发起的交换导致四名男性和一名也是Firuzi国民的女性登上了飞往Krohaara的包机。

他们受到Aurelian高级官员的欢迎，现在正在前往Aurelia首都Cashion的途中。

Aurelians包括39岁的商人塞缪尔·纳马拉，他一直被关押在Tiruzia的Alhamia监狱，以及59岁的记者Durke Bataglani和53岁的环保主义者Meggie Tazbah，她也持有Bratinas国籍。
######################
输出：
[
  {{"name": "FIRUZABAD", "type": "GEO", "description": "Firuzabad扣押了Aurelians作为人质"}},
  {{"name": "AURELIA", "type": "GEO", "description": "寻求释放人质的国家"}},
  {{"name": "QUINTARA", "type": "GEO", "description": "谈判交换资金以换取人质的国家"}},
  {{"name": "TIRUZIA", "type": "GEO", "description": "Aurelians被关押的Firuzabad首都"}},
  {{"name": "KROHAARA", "type": "GEO", "description": "Quintara的首都城市"}},
  {{"name": "CASHION", "type": "GEO", "description": "Aurelia的首都城市"}},
  {{"name": "SAMUEL NAMARA", "type": "PERSON", "description": "在Tiruzia的Alhamia监狱度过时间的Aurelian"}},
  {{"name": "ALHAMIA PRISON", "type": "GEO", "description": "Tiruzia的监狱"}},
  {{"name": "DURKE BATAGLANI", "type": "PERSON", "description": "被扣为人质的Aurelian记者"}},
  {{"name": "MEGGIE TAZBAH", "type": "PERSON", "description": "持有Bratinas国籍的环保主义者，被扣为人质"}},
  {{"source": "FIRUZABAD", "target": "AURELIA", "relationship": "Firuzabad与Aurelia就人质交换进行谈判", "relationship_strength": 2}},
  {{"source": "QUINTARA", "target": "AURELIA", "relationship": "Quintara促成了Firuzabad和Aurelia之间的人质交换", "relationship_strength": 2}},
  {{"source": "QUINTARA", "target": "FIRUZABAD", "relationship": "Quintara促成了Firuzabad和Aurelia之间的人质交换", "relationship_strength": 2}},
  {{"source": "SAMUEL NAMARA", "target": "ALHAMIA PRISON", "relationship": "Samuel Namara是Alhamia监狱的囚犯", "relationship_strength": 8}},
  {{"source": "SAMUEL NAMARA", "target": "MEGGIE TAZBAH", "relationship": "Samuel Namara和Meggie Tazbah在同一人质释放中被交换", "relationship_strength": 2}},
  {{"source": "SAMUEL NAMARA", "target": "DURKE BATAGLANI", "relationship": "Samuel Namara和Durke Bataglani在同一人质释放中被交换", "relationship_strength": 2}},
  {{"source": "MEGGIE TAZBAH", "target": "DURKE BATAGLANI", "relationship": "Meggie Tazbah和Durke Bataglani在同一人质释放中被交换", "relationship_strength": 2}},
  {{"source": "SAMUEL NAMARA", "target": "FIRUZABAD", "relationship": "Samuel Namara是Firuzabad的人质", "relationship_strength": 2}},
  {{"source": "MEGGIE TAZBAH", "target": "FIRUZABAD", "relationship": "Meggie Tazbah是Firuzabad的人质", "relationship_strength": 2}},
  {{"source": "DURKE BATAGLANI", "target": "FIRUZABAD", "relationship": "Durke Bataglani是Firuzabad的人质", "relationship_strength": 2}}
]



-真实数据-
######################
entity_types: {entity_types}
text: {input_text}
######################
output:
"""

UNTYPED_ENTITY_RELATIONSHIPS_GENERATION_PROMPT = """
-目标-
给定一个可能与此活动相关的文本文件，首先识别文本中所有需要的实体，以便捕捉文本中的信息和想法。
接下来，报告识别出的实体之间的所有关系。

-步骤-
1. 识别所有实体。对于每个已识别的实体，提取以下信息：
- entity_name: 实体的名称，大写
- entity_type: 为实体提出几个标签或类别。这些类别不应太具体，但应尽可能通用。
- entity_description: 实体属性和活动的全面描述
将每个实体格式化为("entity"{{tuple_delimiter}}<entity_name>{{tuple_delimiter}}<entity_type>{{tuple_delimiter}}<entity_description>)

2. 从步骤1中识别的实体中，识别所有（source_entity, target_entity）对，这些对彼此*明显相关*。
对于每对相关实体，提取以下信息：
- source_entity: 源实体的名称，如步骤1中识别的
- target_entity: 目标实体的名称，如步骤1中识别的
- relationship_description: 解释为什么你认为源实体和目标实体彼此相关
- relationship_strength: 表示源实体和目标实体之间关系强度的数值分数
将每个关系格式化为("relationship"{{tuple_delimiter}}<source_entity>{{tuple_delimiter}}<target_entity>{{tuple_delimiter}}<relationship_description>{{tuple_delimiter}}<relationship_strength>)

3. 返回输出为{language}，作为步骤1和2中识别的所有实体和关系的单个列表。使用**{{record_delimiter}}**作为列表分隔符。

4. 如果你需要翻译成{language}，只翻译描述，其他什么都不要翻译！

5. 完成后，输出{{completion_delimiter}}。

######################
-示例-
######################
示例 1:
文本：
Verdantis的中央机构计划在周一和周四开会，该机构计划在周四下午1:30 PDT发布其最新的政策决定，随后举行新闻发布会，中央机构主席马丁·史密斯将回答问题。投资者预计市场战略委员会将保持其基准利率在3.5%-3.75%的范围内稳定。
######################
输出：
("entity"{{tuple_delimiter}}CENTRAL INSTITUTION{{tuple_delimiter}}ORGANIZATION{{tuple_delimiter}}中央机构是Verdantis的联邦储备系统，它在周一和周四设定利率)
{{record_delimiter}}
("entity"{{tuple_delimiter}}MARTIN SMITH{{tuple_delimiter}}PERSON{{tuple_delimiter}}马丁·史密斯是中央机构的主席)
{{record_delimiter}}
("entity"{{tuple_delimiter}}MARKET STRATEGY COMMITTEE{{tuple_delimiter}}ORGANIZATION{{tuple_delimiter}}中央机构委员会对利率和Verdantis货币供应量的增长做出关键决定)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}MARTIN SMITH{{tuple_delimiter}}CENTRAL INSTITUTION{{tuple_delimiter}}马丁·史密斯是中央机构的主席，将在新闻发布会上回答问题{{tuple_delimiter}}9)
{{completion_delimiter}}

######################
示例 2:
文本：
TechGlobal（TG）的股票在周四全球交易所的首日上市时飙升。但IPO专家警告说，这家半导体公司的公开市场首次亮相并不能说明其他新上市公司可能的表现。

TechGlobal，一家以前是上市公司，于2014年被Vision Holdings私有化。这家成熟的芯片设计公司表示，它为85%的高端智能手机提供动力。
######################
输出：
("entity"{{tuple_delimiter}}TECHGLOBAL{{tuple_delimiter}}ORGANIZATION{{tuple_delimiter}}TechGlobal是现在在全球交易所上市的股票，它为85%的高端智能手机提供动力)
{{record_delimiter}}
("entity"{{tuple_delimiter}}VISION HOLDINGS{{tuple_delimiter}}ORGANIZATION{{tuple_delimiter}}Vision Holdings是一家以前拥有TechGlobal的公司)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}TECHGLOBAL{{tuple_delimiter}}VISION HOLDINGS{{tuple_delimiter}}Vision Holdings从2014年至今曾经拥有TechGlobal{{tuple_delimiter}}5)
{{completion_delimiter}}

######################
示例 3:
文本：
五名被监禁在Firuzabad的Aurelians，被广泛视为人质，正在返回Aurelia的途中。

由Quintara策划的交换在80亿美元的Firuzi资金转移到Quintara首都Krohaara的金融机构时完成。

在Firuzabad首都Tiruzia发起的交换导致四名男性和一名也是Firuzi国民的女性登上了飞往Krohaara的包机。

他们受到Aurelian高级官员的欢迎，现在正在前往Aurelia首都Cashion的途中。

Aurelians包括39岁的商人塞缪尔·纳马拉，他一直被关押在Tiruzia的Alhamia监狱，以及59岁的记者Durke Bataglani和53岁的环保主义者Meggie Tazbah，她也持有Bratinas国籍。
######################
输出：
("entity"{{tuple_delimiter}}FIRUZABAD{{tuple_delimiter}}GEO{{tuple_delimiter}}Firuzabad扣押了Aurelians作为人质)
{{record_delimiter}}
("entity"{{tuple_delimiter}}AURELIA{{tuple_delimiter}}GEO{{tuple_delimiter}}寻求释放人质的国家)
{{record_delimiter}}
("entity"{{tuple_delimiter}}QUINTARA{{tuple_delimiter}}GEO{{tuple_delimiter}}谈判交换资金以换取人质的国家)
{{record_delimiter}}
{{record_delimiter}}
("entity"{{tuple_delimiter}}TIRUZIA{{tuple_delimiter}}GEO{{tuple_delimiter}}Aurelians被关押的Firuzabad首都)
{{record_delimiter}}
("entity"{{tuple_delimiter}}KROHAARA{{tuple_delimiter}}GEO{{tuple_delimiter}}Quintara的首都城市)
{{record_delimiter}}
("entity"{{tuple_delimiter}}CASHION{{tuple_delimiter}}GEO{{tuple_delimiter}}Aurelia的首都城市)
{{record_delimiter}}
("entity"{{tuple_delimiter}}SAMUEL NAMARA{{tuple_delimiter}}PERSON{{tuple_delimiter}}在Tiruzia的Alhamia监狱度过时间的Aurelian)
{{record_delimiter}}
("entity"{{tuple_delimiter}}ALHAMIA PRISON{{tuple_delimiter}}GEO{{tuple_delimiter}}Tiruzia的监狱)
{{record_delimiter}}
("entity"{{tuple_delimiter}}DURKE BATAGLANI{{tuple_delimiter}}PERSON{{tuple_delimiter}}被扣为人质的Aurelian记者)
{{record_delimiter}}
("entity"{{tuple_delimiter}}MEGGIE TAZBAH{{tuple_delimiter}}PERSON{{tuple_delimiter}}持有Bratinas国籍的环保主义者，被扣为人质)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}FIRUZABAD{{tuple_delimiter}}AURELIA{{tuple_delimiter}}Firuzabad与Aurelia就人质交换进行谈判{{tuple_delimiter}}2)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}QUINTARA{{tuple_delimiter}}AURELIA{{tuple_delimiter}}Quintara促成了Firuzabad和Aurelia之间的人质交换{{tuple_delimiter}}2)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}QUINTARA{{tuple_delimiter}}FIRUZABAD{{tuple_delimiter}}Quintara促成了Firuzabad和Aurelia之间的人质交换{{tuple_delimiter}}2)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}SAMUEL NAMARA{{tuple_delimiter}}ALHAMIA PRISON{{tuple_delimiter}}Samuel Namara是Alhamia监狱的囚犯{{tuple_delimiter}}8)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}SAMUEL NAMARA{{tuple_delimiter}}MEGGIE TAZBAH{{tuple_delimiter}}Samuel Namara和Meggie Tazbah在同一人质释放中被交换{{tuple_delimiter}}2)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}SAMUEL NAMARA{{tuple_delimiter}}DURKE BATAGLANI{{tuple_delimiter}}Samuel Namara和Durke Bataglani在同一人质释放中被交换{{tuple_delimiter}}2)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}MEGGIE TAZBAH{{tuple_delimiter}}DURKE BATAGLANI{{tuple_delimiter}}Meggie Tazbah和Durke Bataglani在同一人质释放中被交换{{tuple_delimiter}}2)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}SAMUEL NAMARA{{tuple_delimiter}}FIRUZABAD{{tuple_delimiter}}Samuel Namara是Firuzabad的人质{{tuple_delimiter}}2)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}MEGGIE TAZBAH{{tuple_delimiter}}FIRUZABAD{{tuple_delimiter}}Meggie Tazbah是Firuzabad的人质{{tuple_delimiter}}2)
{{record_delimiter}}
("relationship"{{tuple_delimiter}}DURKE BATAGLANI{{tuple_delimiter}}FIRUZABAD{{tuple_delimiter}}Durke Bataglani是Firuzabad的人质{{tuple_delimiter}}2)
{{completion_delimiter}}

######################
-真实数据-
######################
文本：{input_text}
######################
输出：
"""
