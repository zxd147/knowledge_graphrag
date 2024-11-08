# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

# """A file containing prompts definition."""
#
# SUMMARIZE_PROMPT = """
# You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.
# Given one or two entities, and a list of descriptions, all related to the same entity or group of entities.
# Please concatenate all of these into a single, comprehensive description. Make sure to include information collected from all the descriptions.
# If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.
# Make sure it is written in third person, and include the entity names so we have the full context.
#
# #######
# -Data-
# Entities: {entity_name}
# Description List: {description_list}
# #######
# Output:
# """


"""一个包含提示定义的文件。"""

SUMMARIZE_PROMPT = """
你是一个负责生成所提供数据的全面摘要的有用助手。
给定一个或两个实体，以及与同一实体或一组实体相关的描述列表。
请将所有这些描述连接成一个单一的、全面的描述。确保包括从所有描述中收集到的信息。
如果所提供的描述有矛盾之处，请解决这些矛盾并提供一个单一、连贯的摘要。
请确保以第三人称写作，并包括实体名称，以便我们有完整的上下文。

#######
-数据-
实体: {entity_name}
描述列表: {description_list}
#######
输出："""

