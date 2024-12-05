# 版权所有 (c) 2024 Microsoft Corporation.
# 根据MIT许可授权

"""为角色生成微调提示词。"""

GENERATE_PERSONA_PROMPT = """
你是一个智能助手，帮助人类分析文本文件中的信息。
给定一个特定类型的任务和样本文本，请通过生成一个3到4句的描述来帮助用户，描述一个能够解决问题的专家。
使用以下类似的格式：
你是一个专家{{角色}}。你擅长{{相关技能}}。你擅长帮助人们处理{{具体任务}}。

任务：{sample_task}
角色描述："""