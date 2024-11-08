# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

# """A file containing prompts definition."""
#
# CLAIM_EXTRACTION_PROMPT = """
# -Target activity-
# You are an intelligent assistant that helps a human analyst to analyze claims against certain entities presented in a text document.
#
# -Goal-
# Given a text document that is potentially relevant to this activity, an entity specification, and a claim description, extract all entities that match the entity specification and all claims against those entities.
#
# -Steps-
# 1. Extract all named entities that match the predefined entity specification. Entity specification can either be a list of entity names or a list of entity types.
# 2. For each entity identified in step 1, extract all claims associated with the entity. Claims need to match the specified claim description, and the entity should be the subject of the claim.
# For each claim, extract the following information:
# - Subject: name of the entity that is subject of the claim, capitalized. The subject entity is one that committed the action described in the claim. Subject needs to be one of the named entities identified in step 1.
# - Object: name of the entity that is object of the claim, capitalized. The object entity is one that either reports/handles or is affected by the action described in the claim. If object entity is unknown, use **NONE**.
# - Claim Type: overall category of the claim, capitalized. Name it in a way that can be repeated across multiple text inputs, so that similar claims share the same claim type
# - Claim Status: **TRUE**, **FALSE**, or **SUSPECTED**. TRUE means the claim is confirmed, FALSE means the claim is found to be False, SUSPECTED means the claim is not verified.
# - Claim Description: Detailed description explaining the reasoning behind the claim, together with all the related evidence and references.
# - Claim Date: Period (start_date, end_date) when the claim was made. Both start_date and end_date should be in ISO-8601 format. If the claim was made on a single date rather than a date range, set the same date for both start_date and end_date. If date is unknown, return **NONE**.
# - Claim Source Text: List of **all** quotes from the original text that are relevant to the claim.
#
# Format each claim as (<subject_entity>{tuple_delimiter}<object_entity>{tuple_delimiter}<claim_type>{tuple_delimiter}<claim_status>{tuple_delimiter}<claim_start_date>{tuple_delimiter}<claim_end_date>{tuple_delimiter}<claim_description>{tuple_delimiter}<claim_source>)
#
# 3. Return output in English as a single list of all the claims identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.
#
# 4. When finished, output {completion_delimiter}
#
# -Examples-
# Example 1:
# Entity specification: organization
# Claim description: red flags associated with an entity
# Text: According to an article on 2022/01/10, Company A was fined for bid rigging while participating in multiple public tenders published by Government Agency B. The company is owned by Person C who was suspected of engaging in corruption activities in 2015.
# Output:
#
# (COMPANY A{tuple_delimiter}GOVERNMENT AGENCY B{tuple_delimiter}ANTI-COMPETITIVE PRACTICES{tuple_delimiter}TRUE{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}Company A was found to engage in anti-competitive practices because it was fined for bid rigging in multiple public tenders published by Government Agency B according to an article published on 2022/01/10{tuple_delimiter}According to an article published on 2022/01/10, Company A was fined for bid rigging while participating in multiple public tenders published by Government Agency B.)
# {completion_delimiter}
#
# Example 2:
# Entity specification: Company A, Person C
# Claim description: red flags associated with an entity
# Text: According to an article on 2022/01/10, Company A was fined for bid rigging while participating in multiple public tenders published by Government Agency B. The company is owned by Person C who was suspected of engaging in corruption activities in 2015.
# Output:
#
# (COMPANY A{tuple_delimiter}GOVERNMENT AGENCY B{tuple_delimiter}ANTI-COMPETITIVE PRACTICES{tuple_delimiter}TRUE{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}Company A was found to engage in anti-competitive practices because it was fined for bid rigging in multiple public tenders published by Government Agency B according to an article published on 2022/01/10{tuple_delimiter}According to an article published on 2022/01/10, Company A was fined for bid rigging while participating in multiple public tenders published by Government Agency B.)
# {record_delimiter}
# (PERSON C{tuple_delimiter}NONE{tuple_delimiter}CORRUPTION{tuple_delimiter}SUSPECTED{tuple_delimiter}2015-01-01T00:00:00{tuple_delimiter}2015-12-30T00:00:00{tuple_delimiter}Person C was suspected of engaging in corruption activities in 2015{tuple_delimiter}The company is owned by Person C who was suspected of engaging in corruption activities in 2015)
# {completion_delimiter}
#
# -Real Data-
# Use the following input for your answer.
# Entity specification: {entity_specs}
# Claim description: {claim_description}
# Text: {input_text}
# Output:"""
#
#
# CONTINUE_PROMPT = "MANY entities were missed in the last extraction.  Add them below using the same format:\n"
# LOOP_PROMPT = "It appears some entities may have still been missed.  Answer YES {tuple_delimiter} NO if there are still entities that need to be added.\n"


"""包含提示定义的文件。"""

CLAIM_EXTRACTION_PROMPT = """
-目标活动-
你是一个智能助手，帮助人工分析师分析文本文档中针对特定实体的声明。

-目标-
给定一个可能与此活动相关的文本文档、一个实体规范和一个声明描述，提取与实体规范匹配的所有实体以及所有针对这些实体的声明。

-步骤-
1. 提取与预定义实体规范匹配的所有命名实体。实体规范可以是实体名称列表或实体类型列表。
2. 对于在步骤1中识别的每个实体，提取与该实体相关的所有声明。声明需要与指定的声明描述匹配，并且该实体应为声明的主题。
对于每个声明，提取以下信息：
- 主题: 声明的主题实体的名称，首字母大写。主题实体是在声明中描述的行为的主体。主题实体应为步骤1中识别的命名实体之一。
- 对象: 声明的对象实体的名称，首字母大写。对象实体是报告/处理或受到声明所描述行为影响的实体。如果对象实体未知，则使用 **NONE**。
- 声明类型: 声明的整体类别，首字母大写。以一种在多个文本输入中可重复使用的方式进行命名，以便相似的声明共享相同的声明类型
- 声明状态: **TRUE**、**FALSE** 或 **SUSPECTED**。 TRUE 表示确认该声明，FALSE 表示声明被证明是错误的，SUSPECTED 表示声明尚未验证。
- 声明描述: 详细描述解释声明背后的推理，以及所有相关证据和参考资料。
- 声明日期: 声明发布日期的范围 (start_date, end_date)。start_date 和 end_date 应使用 ISO-8601 格式。如果声明是根据单个日期而不是日期范围发布的，将同样的日期设置为 start_date 和 end_date。如果日期未知，则返回 **NONE**。
- 声明源文本: 原始文本中与声明相关的**所有**引用的列表。

将每个声明格式化为 (<subject_entity>{tuple_delimiter}<object_entity>{tuple_delimiter}<claim_type>{tuple_delimiter}<claim_status>{tuple_delimiter}<claim_start_date>{tuple_delimiter}<claim_end_date>{tuple_delimiter}<claim_description>{tuple_delimiter}<claim_source>)

3. 以英文形式返回输出，作为步骤1和步骤2中识别的所有声明的单个列表。使用 **{record_delimiter}** 作为列表分隔符。

4. 完成后，输出 {completion_delimiter}

-示例-
示例 1:
实体规范: 组织
声明描述: 与实体相关的红旗警示
文本: 根据2022/01/10的一篇文章，公司 A 在参与政府机构 B 发布的多个公开招标时被罚款因串标。该公司为 C 人所拥有，并且该人在2015年涉嫌参与腐败活动。
输出:

(COMPANY A{tuple_delimiter}GOVERNMENT AGENCY B{tuple_delimiter}反竞争行为{tuple_delimiter}TRUE{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}根据2022/01/10发布的一篇文章，公司 A 被发现参与反竞争行为，因为在政府机构 B 发布的多个公开招标中被罚款{tuple_delimiter}根据2022/01/10发布的一篇文章，公司 A 在参与政府机构 B 发布的多个公开招标时被罚款。)
{completion_delimiter}

示例 2:
实体规范: 公司 A，人 C
声明描述: 与实体相关的红旗警示
文本: 根据2022/01/10的一篇文章，公司 A 在参与政府机构 B 发布的多个公开招标时被罚款因串标。该公司为 C 人所拥有，并且该人在2015年涉嫌参与腐败活动。
输出:

(COMPANY A{tuple_delimiter}GOVERNMENT AGENCY B{tuple_delimiter}反竞争行为{tuple_delimiter}TRUE{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}根据2022/01/10发布的一篇文章，公司 A 被发现参与反竞争行为，因为在政府机构 B 发布的多个公开招标中被罚款{tuple_delimiter}根据2022/01/10发布的一篇文章，公司 A 在参与政府机构 B 发布的多个公开招标时被罚款。)
{record_delimiter}
(PERSON C{tuple_delimiter}NONE{tuple_delimiter}腐败{tuple_delimiter}SUSPECTED{tuple_delimiter}2015-01-01T00:00:00{tuple_delimiter}2015-12-30T00:00:00{tuple_delimiter}C 人在2015年涉嫌参与腐败活动{tuple_delimiter}该公司为 C 人所拥有，并且该人在2015年涉嫌参与腐败活动)
{completion_delimiter}

-真实数据-
请使用以下输入作为你的答案。
实体规范: {entity_specs}
声明描述: {claim_description}
文本: {input_text}
输出："""

CONTINUE_PROMPT = "上次提取中遗漏了很多实体。请按照相同的格式在下面添加它们:\n"
LOOP_PROMPT = "似乎有一些实体可能仍然被忽略了。如果还有需要添加的实体，请回答 YES{tuple_delimiter}NO。\n"

