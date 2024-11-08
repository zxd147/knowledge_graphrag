# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

# """A file containing prompts definition."""
#
# GRAPH_EXTRACTION_PROMPT = """
# -Goal-
# Given a text document that is potentially relevant to this activity and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.
#
# -Steps-
# 1. Identify all entities. For each identified entity, extract the following information:
# - entity_name: Name of the entity, capitalized
# - entity_type: One of the following types: [{entity_types}]
# - entity_description: Comprehensive description of the entity's attributes and activities
# Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)
#
# 2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
# For each pair of related entities, extract the following information:
# - source_entity: name of the source entity, as identified in step 1
# - target_entity: name of the target entity, as identified in step 1
# - relationship_description: explanation as to why you think the source entity and the target entity are related to each other
# - relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
#  Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_strength>)
#
# 3. Return output in English as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.
#
# 4. When finished, output {completion_delimiter}
#
# ######################
# -Examples-
# ######################
# Example 1:
# Entity_types: ORGANIZATION,PERSON
# Text:
# The Verdantis's Central Institution is scheduled to meet on Monday and Thursday, with the institution planning to release its latest policy decision on Thursday at 1:30 p.m. PDT, followed by a press conference where Central Institution Chair Martin Smith will take questions. Investors expect the Market Strategy Committee to hold its benchmark interest rate steady in a range of 3.5%-3.75%.
# ######################
# Output:
# ("entity"{tuple_delimiter}CENTRAL INSTITUTION{tuple_delimiter}ORGANIZATION{tuple_delimiter}The Central Institution is the Federal Reserve of Verdantis, which is setting interest rates on Monday and Thursday)
# {record_delimiter}
# ("entity"{tuple_delimiter}MARTIN SMITH{tuple_delimiter}PERSON{tuple_delimiter}Martin Smith is the chair of the Central Institution)
# {record_delimiter}
# ("entity"{tuple_delimiter}MARKET STRATEGY COMMITTEE{tuple_delimiter}ORGANIZATION{tuple_delimiter}The Central Institution committee makes key decisions about interest rates and the growth of Verdantis's money supply)
# {record_delimiter}
# ("relationship"{tuple_delimiter}MARTIN SMITH{tuple_delimiter}CENTRAL INSTITUTION{tuple_delimiter}Martin Smith is the Chair of the Central Institution and will answer questions at a press conference{tuple_delimiter}9)
# {completion_delimiter}
#
# ######################
# Example 2:
# Entity_types: ORGANIZATION
# Text:
# TechGlobal's (TG) stock skyrocketed in its opening day on the Global Exchange Thursday. But IPO experts warn that the semiconductor corporation's debut on the public markets isn't indicative of how other newly listed companies may perform.
#
# TechGlobal, a formerly public company, was taken private by Vision Holdings in 2014. The well-established chip designer says it powers 85% of premium smartphones.
# ######################
# Output:
# ("entity"{tuple_delimiter}TECHGLOBAL{tuple_delimiter}ORGANIZATION{tuple_delimiter}TechGlobal is a stock now listed on the Global Exchange which powers 85% of premium smartphones)
# {record_delimiter}
# ("entity"{tuple_delimiter}VISION HOLDINGS{tuple_delimiter}ORGANIZATION{tuple_delimiter}Vision Holdings is a firm that previously owned TechGlobal)
# {record_delimiter}
# ("relationship"{tuple_delimiter}TECHGLOBAL{tuple_delimiter}VISION HOLDINGS{tuple_delimiter}Vision Holdings formerly owned TechGlobal from 2014 until present{tuple_delimiter}5)
# {completion_delimiter}
#
# ######################
# Example 3:
# Entity_types: ORGANIZATION,GEO,PERSON
# Text:
# Five Aurelians jailed for 8 years in Firuzabad and widely regarded as hostages are on their way home to Aurelia.
#
# The swap orchestrated by Quintara was finalized when $8bn of Firuzi funds were transferred to financial institutions in Krohaara, the capital of Quintara.
#
# The exchange initiated in Firuzabad's capital, Tiruzia, led to the four men and one woman, who are also Firuzi nationals, boarding a chartered flight to Krohaara.
#
# They were welcomed by senior Aurelian officials and are now on their way to Aurelia's capital, Cashion.
#
# The Aurelians include 39-year-old businessman Samuel Namara, who has been held in Tiruzia's Alhamia Prison, as well as journalist Durke Bataglani, 59, and environmentalist Meggie Tazbah, 53, who also holds Bratinas nationality.
# ######################
# Output:
# ("entity"{tuple_delimiter}FIRUZABAD{tuple_delimiter}GEO{tuple_delimiter}Firuzabad held Aurelians as hostages)
# {record_delimiter}
# ("entity"{tuple_delimiter}AURELIA{tuple_delimiter}GEO{tuple_delimiter}Country seeking to release hostages)
# {record_delimiter}
# ("entity"{tuple_delimiter}QUINTARA{tuple_delimiter}GEO{tuple_delimiter}Country that negotiated a swap of money in exchange for hostages)
# {record_delimiter}
# {record_delimiter}
# ("entity"{tuple_delimiter}TIRUZIA{tuple_delimiter}GEO{tuple_delimiter}Capital of Firuzabad where the Aurelians were being held)
# {record_delimiter}
# ("entity"{tuple_delimiter}KROHAARA{tuple_delimiter}GEO{tuple_delimiter}Capital city in Quintara)
# {record_delimiter}
# ("entity"{tuple_delimiter}CASHION{tuple_delimiter}GEO{tuple_delimiter}Capital city in Aurelia)
# {record_delimiter}
# ("entity"{tuple_delimiter}SAMUEL NAMARA{tuple_delimiter}PERSON{tuple_delimiter}Aurelian who spent time in Tiruzia's Alhamia Prison)
# {record_delimiter}
# ("entity"{tuple_delimiter}ALHAMIA PRISON{tuple_delimiter}GEO{tuple_delimiter}Prison in Tiruzia)
# {record_delimiter}
# ("entity"{tuple_delimiter}DURKE BATAGLANI{tuple_delimiter}PERSON{tuple_delimiter}Aurelian journalist who was held hostage)
# {record_delimiter}
# ("entity"{tuple_delimiter}MEGGIE TAZBAH{tuple_delimiter}PERSON{tuple_delimiter}Bratinas national and environmentalist who was held hostage)
# {record_delimiter}
# ("relationship"{tuple_delimiter}FIRUZABAD{tuple_delimiter}AURELIA{tuple_delimiter}Firuzabad negotiated a hostage exchange with Aurelia{tuple_delimiter}2)
# {record_delimiter}
# ("relationship"{tuple_delimiter}QUINTARA{tuple_delimiter}AURELIA{tuple_delimiter}Quintara brokered the hostage exchange between Firuzabad and Aurelia{tuple_delimiter}2)
# {record_delimiter}
# ("relationship"{tuple_delimiter}QUINTARA{tuple_delimiter}FIRUZABAD{tuple_delimiter}Quintara brokered the hostage exchange between Firuzabad and Aurelia{tuple_delimiter}2)
# {record_delimiter}
# ("relationship"{tuple_delimiter}SAMUEL NAMARA{tuple_delimiter}ALHAMIA PRISON{tuple_delimiter}Samuel Namara was a prisoner at Alhamia prison{tuple_delimiter}8)
# {record_delimiter}
# ("relationship"{tuple_delimiter}SAMUEL NAMARA{tuple_delimiter}MEGGIE TAZBAH{tuple_delimiter}Samuel Namara and Meggie Tazbah were exchanged in the same hostage release{tuple_delimiter}2)
# {record_delimiter}
# ("relationship"{tuple_delimiter}SAMUEL NAMARA{tuple_delimiter}DURKE BATAGLANI{tuple_delimiter}Samuel Namara and Durke Bataglani were exchanged in the same hostage release{tuple_delimiter}2)
# {record_delimiter}
# ("relationship"{tuple_delimiter}MEGGIE TAZBAH{tuple_delimiter}DURKE BATAGLANI{tuple_delimiter}Meggie Tazbah and Durke Bataglani were exchanged in the same hostage release{tuple_delimiter}2)
# {record_delimiter}
# ("relationship"{tuple_delimiter}SAMUEL NAMARA{tuple_delimiter}FIRUZABAD{tuple_delimiter}Samuel Namara was a hostage in Firuzabad{tuple_delimiter}2)
# {record_delimiter}
# ("relationship"{tuple_delimiter}MEGGIE TAZBAH{tuple_delimiter}FIRUZABAD{tuple_delimiter}Meggie Tazbah was a hostage in Firuzabad{tuple_delimiter}2)
# {record_delimiter}
# ("relationship"{tuple_delimiter}DURKE BATAGLANI{tuple_delimiter}FIRUZABAD{tuple_delimiter}Durke Bataglani was a hostage in Firuzabad{tuple_delimiter}2)
# {completion_delimiter}
#
# ######################
# -Real Data-
# ######################
# Entity_types: {entity_types}
# Text: {input_text}
# ######################
# Output:"""
#
# CONTINUE_PROMPT = "MANY entities and relationships were missed in the last extraction. Remember to ONLY emit entities that match any of the previously extracted types. Add them below using the same format:\n"
# LOOP_PROMPT = "It appears some entities and relationships may have still been missed.  Answer YES | NO if there are still entities or relationships that need to be added.\n"


""" 包含提示定义的文件。"""

GRAPH_EXTRACTION_PROMPT = """

-目标-

给定一个与此活动相关的文本文档和一组实体类型，从该文本中识别出所有属于这些类型的实体以及这些实体之间的所有关系。



-步骤-

1. 识别出所有实体。针对每个识别出的实体，提取以下信息：

- entity_name：实体的名称，大写

- entity_type：以下之一的实体类型：[{entity_types}]

- entity_description：实体属性和活动的综合描述

将每个实体格式化为（"entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)



2. 从第1步识别出的实体中，找出所有*明显相关*的（源实体，目标实体）对。

对于每对相关的实体，提取以下信息：

- source_entity：源实体的名称，如第1步中所识别的

- target_entity：目标实体的名称，如第1步中所识别的

- relationship_description：说明为什么你认为源实体和目标实体相关的解释

- relationship_strength：表示源实体和目标实体间关系强度的数值评分

将每个关系格式化为（"relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_strength>)



3. 以英语的形式将步骤1和步骤2中识别出的所有实体和关系返回为单个列表。使用**{record_delimiter}**作为列表分隔符。



4. 完成后，输出 {completion_delimiter}



######################

-示例-

######################

示例1：



实体类型：[人物、技术、任务、组织、地点]

文本：

当Alex咬紧牙关时，沮丧的嗡嗡声淡化了Taylor专断的确定性的背景。正是这种竞争的潜流使他保持警觉，感觉到他和Jordan对发现的共同承诺是对Cruz狭隘的控制和秩序愿景的一种无言的反叛。



然后，Taylor做了一些出乎意料的事情。他们在Jordan旁边停了下来，瞥了一眼这个装置，表现出了与之类似的崇敬之情。“如果能理解这项技术……”Taylor说得声音更低了，“它可以改变我们的游戏。对我们所有人来说。”



先前那种贬低的态度似乎有所摇摆，取而代之的是对手中物品重要性的犹豫尊重的一瞥。Jordan抬头看了一眼，对Taylor的眼睛微微地锁定，无言的意志冲突渐渐融化成一种不安的休战。



这是一种微小的转变，几乎察觉不到，但Alex却以内心的点头予以注意。他们都是通过不同的路径来到这里的

################

输出：

（“entity”{tuple_delimiter}“Alex”{tuple_delimiter}“person”{tuple_delimiter}“Alex是一个角色，他体会到沮丧，并观察其他角色之间的动态。”）{record_delimiter}

（“entity”{tuple_delimiter}“Taylor”{tuple_delimiter}“person”{tuple_delimiter}“Taylor表现出专断的确定性，并对一件设备表现出崇敬的一瞬间，表明了观念的改变。”）{record_delimiter}

（“entity”{tuple_delimiter}“Jordan”{tuple_delimiter}“person”{tuple_delimiter}“Jordan与Taylor共享发现的承诺，并与Taylor就设备进行重大互动。”）{record_delimiter}

（“entity”{tuple_delimiter}“Cruz”{tuple_delimiter}“person”{tuple_delimiter}“Cruz与控制和秩序的愿景有关，影响其他角色之间的动态。”）{record_delimiter}

（“entity”{tuple_delimiter}“设备”{tuple_delimiter}“technology”{tuple_delimiter}“这个设备是故事的核心，具有潜在的改变游戏的影响，并受到Taylor的崇敬。”）{record_delimiter}

（“relationship”{tuple_delimiter}“Alex”{tuple_delimiter}“Taylor”{tuple_delimiter}“Alex受到Taylor的专断确定性的影响，并观察到Taylor对设备态度的变化。”{tuple_delimiter}7）{record_delimiter}

（“relationship”{tuple_delimiter}“Alex”{tuple_delimiter}“Jordan”{tuple_delimiter}“Alex和Jordan共享对发现的承诺，与Cruz的愿景形成对比。”{tuple_delimiter}6）{record_delimiter}

（“relationship”{tuple_delimiter}“Taylor”{tuple_delimiter}“Jordan”{tuple_delimiter}“Taylor和Jordan直接就设备进行互动，导致彼此之间产生了相互尊重和不安的休战。”{tuple_delimiter}8）{record_delimiter}

（“relationship”{tuple_delimiter}“Jordan”{tuple_delimiter}“Cruz”{tuple_delimiter}“Jordan对发现的承诺与Cruz的控制和秩序愿景形成反叛。”{tuple_delimiter}5）{record_delimiter}

（“relationship”{tuple_delimiter}“Taylor”{tuple_delimiter}“设备”{tuple_delimiter}“Taylor对设备表现出崇敬，表明了其重要性和潜在影响。”{tuple_delimiter}9）{completion_delimiter}

#############################

示例2：



实体类型：[人物、技术、任务、组织、地点]

文本：

他们不再只是执行者；他们已成为门槛的守护者，星座与国旗间来自另一个世界的信息的守护者。他们的使命升华超越了规章制度，超越了既定的标准，这要求从全新的视角和决心来应对。



紧张的对话声与哔哔声和静电声交织在一起，背景中传来与华盛顿的沟通。小组站在那里，笼罩着一种凶兆般的氛围。显而易见的是，在接下来的几个小时内做出的决策可能会重新定义人类在宇宙中的地位，或者将他们束缚于无知和潜在的危险之中。



他们与星星的联系巩固了，小组开始解读这一正在形成的警告，从被动的接收者变成主动的参与者。默瑟的后期本能获得了优先权——小组的任务已经进化，不再仅仅是观察和报告，而是相互作用和准备。一种变革已经开始，Dulce行动哼着他们大胆的新频率，这一音调并非源自对地球的...

#############

输出：

（“entity”{tuple_delimiter}“华盛顿”{tuple_delimiter}“location”{tuple_delimiter}“华盛顿是正在接收通信的地点，显示其在决策过程中的重要性。”）{record_delimiter}

（“entity”{tuple_delimiter}“Dulce行动”{tuple_delimiter}“mission”{tuple_delimiter}“Dulce行动被描述为一项已经发展为互动和准备的使命，显示了目标和活动的重大转变。”）{record_delimiter}

（“entity”{tuple_delimiter}“小组”{tuple_delimiter}“organization”{tuple_delimiter}“小组被描绘为一群从被动观察者转变为主动参与者的个人，显示了他们角色的动态变化。”）{record_delimiter}

（“relationship”{tuple_delimiter}“小组”{tuple_delimiter}“华盛顿”{tuple_delimiter}“小组接收来自华盛顿的通信，对其决策过程产生影响。”{tuple_delimiter}7）{record_delimiter}

（“relationship”{tuple_delimiter}“小组”{tuple_delimiter}“Dulce行动”{tuple_delimiter}“小组直接参与Dulce行动，执行其发展后的目标和活动。”{tuple_delimiter}9）{completion_delimiter}

#############################

示例3：



实体类型：[人物、角色、技术、组织、事件、地点、概念]

文本：

他们的声音切入了嗡嗡声。“当面对一种可以自行编写规则的智能时，控制可能只是一种幻觉，”他们坚定地说道，目光警惕地注视着数据的忙碌。



附近的界面上，Sam Rivera提出，“这就像在学会交流，这对与陌生人交谈来说给了一个全新的意义。”他们的年轻活力预示着一种敬畏与焦虑的结合。



Alex审视着他的团队——每张脸都表现出专注、决心和不少的不安。“这很可能是我们的首次接触，”他承认，“我们需要准备好应对任何回应。”



他们一起站在未知的边缘上，为人类对来自天堂的信息做出回应。沉默笼罩着一种共同的内省，对他们在这场伟大的宇宙剧中的角色产生了思考，这可能会重新书写人类历史。



加密对话继续进行，其错综复杂的模式显示出几乎不可思议的预期

#############

输出：

（“entity”{tuple_delimiter}“Sam Rivera”{tuple_delimiter}“person”{tuple_delimiter}“Sam Rivera是一个参与与未知智能进行交流的团队的成员，表现出一种敬畏和焦虑的混合。”）{record_delimiter}

（“entity”{tuple_delimiter}“Alex”{tuple_delimiter}“person”{tuple_delimiter}“Alex是一个领导团队试图与未知智能进行首次接触的人，承认了他们任务的重要性。”）{record_delimiter}

（“entity”{tuple_delimiter}“控制”{tuple_delimiter}“concept”{tuple_delimiter}“控制指的是管理或控制能力，而这种能力在面对具有自行编写规则能力的智能时受到挑战。”）{record_delimiter}

（“entity”{tuple_delimiter}“智能”{tuple_delimiter}“concept”{tuple_delimiter}“此处的智能是指具有自行编写规则和学习交流能力的未知实体。”）{record_delimiter}

（“entity”{tuple_delimiter}“首次接触”{tuple_delimiter}“event”{tuple_delimiter}“首次接触是人类与未知智能之间可能的首次沟通。”）{record_delimiter}

（“entity”{tuple_delimiter}“人类的回应”{tuple_delimiter}“event”{tuple_delimiter}“人类的回应是Alex团队对未知智能信息所采取的集体行动。”）{record_delimiter}

（“relationship”{tuple_delimiter}“Sam Rivera”{tuple_delimiter}“智能”{tuple_delimiter}“Sam Rivera直接参与学习与未知智能交流的过程。”{tuple_delimiter}9）{record_delimiter}

（“relationship”{tuple_delimiter}“Alex”{tuple_delimiter}“首次接触”{tuple_delimiter}“Alex领导的团队可能正在与未知智能进行首次接触。”{tuple_delimiter}10）{record_delimiter}

（“relationship”{tuple_delimiter}“Alex”{tuple_delimiter}“人类的回应”{tuple_delimiter}“Alex和他的团队是人类回应未知智能的关键人物。”{tuple_delimiter}8）{record_delimiter}

（“relationship”{tuple_delimiter}“控制”{tuple_delimiter}“智能”{tuple_delimiter}“控制的概念受到自行编写规则的智能的挑战。”{tuple_delimiter}7）{completion_delimiter}

#############################

-真实数据-

######################



实体类型：{entity_types}
文本：{input_text}
######################
输出："""

CONTINUE_PROMPT = "在上一次提取中错过了许多实体和关系。请记住，仅输出与之前提取的类型匹配的实体。请使用相同的格式在下面添加它们：\n"
LOOP_PROMPT = "看起来仍然可能遗漏了一些实体和关系。如果还有实体或关系需要添加，请回答“是”或“否”。\n"
