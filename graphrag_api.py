import asyncio
import os
import re
import time
# import jieba
import torch
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional, Dict, Union, Literal, AsyncGenerator, Any

import pandas as pd
import tiktoken
import uvicorn
from environs import Env
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from graphrag.query.context_builder.conversation_history import (
    ConversationHistory,
)
# GraphRAG 相关导入
from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey
from graphrag.query.indexer_adapters import (
    read_indexer_covariates,
    read_indexer_entities,
    read_indexer_relationships,
    read_indexer_reports,
    read_indexer_text_units,
)
from graphrag.query.input.loaders.dfs import store_entity_semantic_embeddings
from graphrag.query.llm.oai.chat_openai import ChatOpenAI
from graphrag.query.llm.oai.embedding import OpenAIEmbedding
from graphrag.query.llm.oai.typing import OpenaiApiType
from graphrag.query.question_gen.local_gen import LocalQuestionGen
from graphrag.query.structured_search.global_search.community_context import GlobalCommunityContext
from graphrag.query.structured_search.global_search.search import GlobalSearch
from graphrag.query.structured_search.local_search.mixed_context import LocalSearchMixedContext
from graphrag.query.structured_search.local_search.search import LocalSearch
from graphrag.vector_stores.lancedb import LanceDBVectorStore
from utils.log_utils import logger
from utils.read_json import read_config_file

# 设置常量和配置
COMMUNITY_REPORT_TABLE = "create_final_community_reports"
ENTITY_TABLE = "create_final_nodes"
ENTITY_EMBEDDING_TABLE = "create_final_entities"
RELATIONSHIP_TABLE = "create_final_relationships"
COVARIATE_TABLE = "create_final_covariates"
TEXT_UNIT_TABLE = "create_final_text_units"
COMMUNITY_LEVEL = 2
CURRENT_MODEL = ''
CURRENT_KNOWLEDGE_BASE = 'dentistry'
PORT = 8013


# # 定义LLMConfig和EmbedderConfig类型
class LLMConfig(BaseModel):
    api_base: str = None
    api_key: str = None
    model: str = None
    api_type: OpenaiApiType


class EmbedderConfig(BaseModel):
    api_base: str = None
    api_key: str = None
    model: str = None
    api_type: OpenaiApiType


class ModelCard(BaseModel):
    id: str
    object: str = 'model'
    mode: str = ''
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: str = 'owner'
    root: Optional[str] = None
    parent: Optional[str] = None
    permission: Optional[list] = None


class ModelList(BaseModel):
    object: str = 'list'
    data: List[ModelCard] = []


# 定义ChatCompletionRequest类
class ChatCompletionRequest(BaseModel):
    model: str = 'Qwen2.5-7B-Instruct'
    mode: str
    knowledge: Literal['zyy', 'dentistry', 'ecology', 'spectra', 'test'] = 'dentistry'
    # messages: List[Message]
    messages: List[dict[str, str]]
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None


class Delta(BaseModel):
    role: Optional[Literal['user', 'assistant', 'system']] = None
    content: Optional[str] = None


# 定义Message类型
class Message(BaseModel):
    role: Optional[Literal['user', 'assistant', 'system']] = None
    content: Optional[str] = None


# 定义Usage类
class UsageInfo(BaseModel):
    prompt_tokens: int = None
    completion_tokens: int = None
    total_tokens: int = None


# 定义ChatCompletionResponseChoice类
class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: Message
    finish_reason: Literal['stop', 'length', 'function_call'] = 'stop'


class ChatCompletionResponseStreamChoice(BaseModel):
    index: int = 0
    delta: Delta  # delta字段包含内容
    finish_reason: Optional[Literal['stop', 'length']] = None


class ChatCompletionResponse(BaseModel):
    model: str
    id: str = Field(default_factory=lambda: f"chatcmpl-{str(uuid.uuid4().hex)}")
    created: Optional[int] = Field(default_factory=lambda: int(time.time()))
    object: Literal['chat.completion', 'chat.completion.chunk'] = "chat.completion"
    choices: List[Union[ChatCompletionResponseChoice, ChatCompletionResponseStreamChoice]]
    usage: Optional[UsageInfo] = Field(default=None)


# # 定义ChatCompletionResponse类
# class ChatCompletionResponse(BaseModel):
#     model: str
#     id: str = Field(default_factory=lambda: f"chatcmpl-{str(uuid.uuid4().hex)}")
#     created: int = Field(default_factory=lambda: int(time.time()))
#     object: str = "chat.completion"
#     choices: List[ChatCompletionResponseChoice]
#     usage: UsageInfo
#     # system_fingerprint: Optional[str] = None
#

# # 定义流式返回的Chunk
# class ChatCompletionStreamResponse(BaseModel):
#     model: str
#     id: str = Field(default_factory=lambda: f"chatcmpl-{str(uuid.uuid4().hex)}")
#     created: Optional[int] = Field(default_factory=lambda: int(time.time()))
#     object: str = "chat.completion.chunk"
#     choices: List[ChatCompletionResponseStreamChoice]
#     usage: UsageInfo


class BasicAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret_key: str):
        super().__init__(app)
        self.required_credentials = secret_key

    async def dispatch(self, request: Request, call_next):
        authorization: str = request.headers.get('Authorization')
        if authorization and authorization.startswith('Bearer '):
            provided_credentials = authorization.split(' ')[1]
            # 比较提供的令牌和所需的令牌
            if provided_credentials == self.required_credentials:
                return await call_next(request)
        # 返回一个带有自定义消息的JSON响应
        return JSONResponse(
            status_code=400,
            content={"detail": "Unauthorized: Invalid or missing credentials"},
            headers={'WWW-Authenticate': 'Bearer realm="Secure Area"'}
        )


# 定义了一个异步函数 lifespan，它接收一个 FastAPI 应用实例 app 作为参数。这个函数将管理应用的生命周期，包括启动和关闭时的操作
# 函数在应用启动时执行一些初始化操作，如设置搜索引擎、加载上下文数据、以及初始化问题生成器
# 函数在应用关闭时执行一些清理操作
# @asynccontextmanager 装饰器用于创建一个异步上下文管理器，它允许你在 yield 之前和之后执行特定的代码块，分别表示启动和关闭时的操作
@asynccontextmanager
async def lifespan(graphrag_app: FastAPI):
    # 启动时执行
    try:
        graphrag_logger.info("启动中...")
        # 初始化系统
        # llm_config, embedder_config = get_config(new_llm_model=None)
        await refresh_models(new_llm_model=CURRENT_MODEL, new_knowledge=CURRENT_KNOWLEDGE_BASE)
        # 让应用继续运行
        yield
    except Exception as e:
        graphrag_logger.error(f"启动失败: {e}")
        raise
    finally:
        graphrag_logger.info("关闭应用...")


async def init_app():
    if torch.cuda.is_available():
        log = f'本次加载模型的设备为GPU: {torch.cuda.get_device_name(0)}'
    else:
        log = '本次加载模型的设备为CPU.'
    graphrag_logger.info(log)
    log = f"Service started!"
    graphrag_logger.info(log)


role_prompt_path = 'config/role_prompt.json'
all_role_prompt = read_config_file(role_prompt_path)
# 全局变量，用于存储搜索引擎和问题生成器，类型注解为 Optional 类型，表示这些变量可能是 None 或特定的类型对象
local_search_engine: Optional[LocalSearch] = None
global_search_engine: Optional[GlobalSearch] = None
question_generator: Optional[LocalQuestionGen] = None
graphrag_logger = logger
# lifespan 参数用于在应用程序生命周期的开始和结束时执行一些初始化或清理工作
graphrag_app = FastAPI(lifespan=lifespan)
secret_key = os.getenv('GRAPHRAG-SECRET-KEY', 'sk-graphrag')
graphrag_app.add_middleware(BasicAuthMiddleware, secret_key=secret_key)
graphrag_app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'], )


def count_tokens(text: str, model: str = "gpt-4") -> int:
    # 根据模型选择分词器
    encoding = tiktoken.encoding_for_model(model)
    token = len(encoding.encode(text))
    # 返回分词后的 token 数量
    return token


def get_config(new_llm_model=None):
    env = Env()
    env.read_env()  # 自动读取 .env 文件
    llm_api_base = env("LLM_API_BASE", env("AZURE_OPENAI_API_BASE", None))
    llm_api_key = env("LLM_API_KEY", env("AZURE_OPENAI_API_KEY", None))
    llm_model = env("LLM_MODEL", env("AZURE_OPENAI_MODEL", None))
    llm_api_type = env("LLM_API_TYPE", env("AZURE_OPENAI_API_TYPE", None))
    embedder_api_base = env("EMBEDDING_API_BASE", env("AZURE_OPENAI_API_BASE", None))
    embedder_api_key = env("EMBEDDING_API_KEY", env("AZURE_OPENAI_API_KEY", None))
    embedder_model = env("EMBEDDING_MODEL", env("AZURE_OPENAI_MODEL", None))
    embedder_api_type = env("EMBEDDING_API_TYPE", env("AZURE_OPENAI_API_TYPE", None))
    if new_llm_model:
        llm_model = new_llm_model
    llm_config = LLMConfig(
        api_base=llm_api_base,
        api_key=llm_api_key,
        model=llm_model,
        api_type=llm_api_type
    )
    embedder_config = EmbedderConfig(
        api_base=embedder_api_base,
        api_key=embedder_api_key,
        model=embedder_model,
        api_type=embedder_api_type
    )
    return llm_config, embedder_config


# async def sync_setting(new_llm_model, new_knowledge):
#     global CURRENT_MODEL, CURRENT_KNOWLEDGE_BASE
#     try:
#         if new_llm_model != CURRENT_MODEL or new_knowledge != CURRENT_KNOWLEDGE_BASE:
#             graphrag_logger.info(f"检测到LLM模型/知识库变化，正在重新初始化为：{new_llm_model, new_knowledge}")
#             # 重新执行初始化操作
#             # llm_config, embedder_config = get_config(new_llm_model=new_llm_model)
#             await refresh_models(new_llm_model, new_knowledge)
#         return {"status": "model changed", "new_model": CURRENT_MODEL}
#     except Exception as e:
#         graphrag_logger.error(f"初始化过程中出错: {str(e)}")
#         # raise 关键字重新抛出异常，以确保程序不会在错误状态下继续运行
#         # yield 关键字将控制权交还给FastAPI框架，使应用开始运行
#         # 分隔了启动和关闭的逻辑。在yield 之前的代码在应用启动时运行，yield 之后的代码在应用关闭时运行
#         # 关闭时执行
#         graphrag_logger.info("正在关闭...")


async def refresh_models(new_llm_model, new_knowledge):
    if new_llm_model != CURRENT_MODEL or new_knowledge != CURRENT_KNOWLEDGE_BASE or not CURRENT_MODEL:
        graphrag_logger.info(f"检测到LLM模型/知识库变化，正在重新初始化为：{new_llm_model, new_knowledge}")
        # 申明引用全局变量，在函数中被初始化，并在整个应用中使用
        global local_search_engine, global_search_engine, question_generator
        """初始搜索引擎和问题生成器"""
        graphrag_logger.info("正在初始化搜索引擎和问题生成器...")
        # 调用setup_llm_and_embedder()函数以设置语言模型（LLM）、token编码器（TokenEncoder）和文本嵌入向量生成器（TextEmbedder）
        # await 关键字表示此调用是异步的，函数将在这个操作完成后继续执行
        llm, token_encoder, text_embedder = await setup_llm_and_embedder(new_llm_model)
        # 调用load_context()函数加载实体、关系、报告、文本单元、描述嵌入存储和协变量等数据，这些数据将用于构建搜索引擎和问题生成器
        entities, relationships, reports, text_units, description_embedding_store, covariates = await load_context(
            new_knowledge)
        # 调用setup_search_engines()函数设置本地和全局搜索引擎、上下文构建器（ContextBuilder）、以及相关参数
        local_search_engine, global_search_engine, local_context_builder, local_llm_params, local_context_params = await setup_search_engines(
            llm, token_encoder, text_embedder, entities, relationships, reports, text_units,
            description_embedding_store, covariates
        )
        # 使用LocalQuestionGen类创建一个本地问题生成器question_generator，将前面初始化的各种组件传递给它
        question_generator = LocalQuestionGen(
            llm=llm,
            context_builder=local_context_builder,
            token_encoder=token_encoder,
            llm_params=local_llm_params,
            context_builder_params=local_context_params,
        )
        graphrag_logger.info("初始化完成")
    return {"status": "success"}


# 设置语言模型（LLM）、token编码器（TokenEncoder）和文本嵌入向量生成器（TextEmbedder）
async def setup_llm_and_embedder(new_llm_model):
    graphrag_logger.info("正在设置LLM和嵌入器")
    # 实例化一个ChatOpenAI客户端对象
    env = Env()
    env.read_env()  # 自动读取 .env 文件
    llm_api_base = env("LLM_API_BASE", env("AZURE_OPENAI_API_BASE", None))
    llm_api_key = env("LLM_API_KEY", env("AZURE_OPENAI_API_KEY", None))
    llm_model = new_llm_model or env("LLM_MODEL", env("AZURE_OPENAI_MODEL", None))
    embedder_api_base = env("EMBEDDING_API_BASE", env("AZURE_OPENAI_API_BASE", None))
    embedder_api_key = env("EMBEDDING_API_KEY", env("AZURE_OPENAI_API_KEY", None))
    embedder_model = env("EMBEDDING_MODEL", env("AZURE_OPENAI_MODEL", None))
    llm = ChatOpenAI(
        # 调用其他模型  通过oneAPI
        api_base=llm_api_base,  # 请求的API服务地址
        api_key=llm_api_key,  # API Key
        model=llm_model,  # 本次使用的模型
        api_type=OpenaiApiType.OpenAI,
        max_retries=1,
    )
    # 实例化OpenAIEmbeddings处理模型
    text_embedder = OpenAIEmbedding(
        # 调用其他模型  通过oneAPI
        api_base=embedder_api_base,  # 请求的API服务地址
        api_key=embedder_api_key,  # API Key
        model=embedder_model,
        # deployment_name="m3e-large",
        api_type=OpenaiApiType.OpenAI,
        max_retries=1,
    )

    # llm = ChatOpenAI(
    #     # # 调用gpt
    #     # api_base="https://api.wlai.vip/v1",  # 请求的API服务地址
    #     # api_key="sk-4P8HC2GD6heTwx0l8dD83f13F1014e039eC4Ac6d47877dCb",  # API Key
    #     # model="gpt-4o-mini",  # 本次使用的模型
    #     # api_type=OpenaiApiType.OpenAI,
    #
    #     # 调用其他模型  通过oneAPI
    #     api_base=llm_api_base,  # 请求的API服务地址
    #     api_key=llm_api_key,  # API Key
    #     model=llm_model,  # 本次使用的模型
    #     api_type=OpenaiApiType.OpenAI,
    # )
    # # 实例化OpenAIEmbeddings处理模型
    # text_embedder = OpenAIEmbedding(
    #     # # 调用gpt
    #     # api_base="https://api.wlai.vip/v1",  # 请求的API服务地址
    #     # api_key="sk-Soz7kmey8JKidej0AeD416B87d2547E1861d29F4F3E7A75e",  # API Key
    #     # model="text-embedding-3-small",
    #     # deployment_name="text-embedding-3-small",
    #     # api_type=OpenaiApiType.OpenAI,
    #     # max_retries=20,
    #
    #     # 调用其他模型  通过oneAPI
    #     api_base="http://192.168.0.245:8016/v1",  # 请求的API服务地址
    #     api_key="sk-fastgpt",  # API Key
    #     model="m3e-large",
    #     # deployment_name="m3e-large",
    #     api_type=OpenaiApiType.OpenAI,
    #     max_retries=20,
    # )
    global CURRENT_MODEL
    CURRENT_MODEL = llm_model
    graphrag_logger.info(f"LLM和嵌入器设置完成, 当前模型为: {CURRENT_MODEL}")
    # 初始化token编码器
    token_encoder = tiktoken.get_encoding("cl100k_base")
    return llm, token_encoder, text_embedder


# 加载上下文数据，包括实体、关系、报告、文本单元和协变量
async def load_context(new_knowledge):
    graphrag_logger.info("正在加载上下文数据")
    knowledge_dir = f"./project/{new_knowledge}/output/artifacts"
    lancedb_uri = f"{knowledge_dir}/lancedb"
    try:
        # 使用pandas库从指定的路径读取实体数据表ENTITY_TABLE，文件格式为Parquet，并将其加载为DataFrame，存储在变量entity_df中
        entity_df = pd.read_parquet(f"{knowledge_dir}/{ENTITY_TABLE}.parquet")
        # 读取实体嵌入向量数据表ENTITY_EMBEDDING_TABLE，并将其加载为DataFrame，存储在变量entity_embedding_df中
        entity_embedding_df = pd.read_parquet(f"{knowledge_dir}/{ENTITY_EMBEDDING_TABLE}.parquet")
        # 将entity_df和entity_embedding_df传入，并基于COMMUNITY_LEVEL（社区级别）处理这些数据，返回处理后的实体数据entities
        entities = read_indexer_entities(entity_df, entity_embedding_df, COMMUNITY_LEVEL)
        # 创建一个LanceDBVectorStore的实例description_embedding_store，用于存储实体的描述嵌入向量
        # 这个实例与一个名为"entity_description_embeddings_qwen"的集合（collection）相关联
        description_embedding_store = LanceDBVectorStore(collection_name="entity_description_embeddings")
        # 通过调用connect方法，连接到指定的LanceDB数据库，使用的URI存储在LANCEDB_URI变量中
        description_embedding_store.connect(db_uri=lancedb_uri)
        # 将已处理的实体数据entities存储到description_embedding_store中，用于语义搜索或其他用途
        store_entity_semantic_embeddings(entities=entities, vectorstore=description_embedding_store)
        relationship_df = pd.read_parquet(f"{knowledge_dir}/{RELATIONSHIP_TABLE}.parquet")
        relationships = read_indexer_relationships(relationship_df)
        report_df = pd.read_parquet(f"{knowledge_dir}/{COMMUNITY_REPORT_TABLE}.parquet")
        reports = read_indexer_reports(report_df, entity_df, COMMUNITY_LEVEL)
        text_unit_df = pd.read_parquet(f"{knowledge_dir}/{TEXT_UNIT_TABLE}.parquet")
        text_units = read_indexer_text_units(text_unit_df)
        covariate_df = pd.read_parquet(f"{knowledge_dir}/{COVARIATE_TABLE}.parquet")
        claims = read_indexer_covariates(covariate_df)
        graphrag_logger.info(f"声明记录数: {len(claims)}")
        covariates = {"claims": claims}
        global CURRENT_KNOWLEDGE_BASE
        CURRENT_KNOWLEDGE_BASE = new_knowledge
        graphrag_logger.info(f"上下文数据加载完成, 当前知识库为: {CURRENT_KNOWLEDGE_BASE}")
        return entities, relationships, reports, text_units, description_embedding_store, covariates
    except Exception as e:
        graphrag_logger.error(f"加载上下文数据时出错: {str(e)}")
        raise


# 设置本地和全局搜索引擎、上下文构建器（ContextBuilder）、以及相关参数
async def setup_search_engines(llm, token_encoder, text_embedder, entities, relationships, reports, text_units,
                               description_embedding_store, covariates):
    global global_search_engine, local_search_engine
    graphrag_logger.info("正在设置搜索引擎")
    # 设置本地搜索引擎
    local_context_builder = LocalSearchMixedContext(
        community_reports=reports,
        text_units=text_units,
        entities=entities,
        relationships=relationships,
        covariates=covariates,
        entity_text_embeddings=description_embedding_store,
        embedding_vectorstore_key=EntityVectorStoreKey.ID,
        text_embedder=text_embedder,
        token_encoder=token_encoder,
    )

    local_context_params = {
        "text_unit_prop": 0.5,
        "community_prop": 0.1,
        "conversation_history_max_turns": 5,
        "conversation_history_user_turns_only": True,
        "top_k_mapped_entities": 10,
        "top_k_relationships": 10,
        "include_entity_rank": True,
        "include_relationship_weight": True,
        "include_community_rank": False,
        "return_candidate_context": False,
        "embedding_vectorstore_key": EntityVectorStoreKey.ID,
        # "max_tokens": 12_000,
        "max_tokens": 4096,
    }

    local_llm_params = {
        # "max_tokens": 2_000,
        "max_tokens": 4096,
        "temperature": 0.0,
    }

    local_search_engine = LocalSearch(
        llm=llm,
        context_builder=local_context_builder,
        token_encoder=token_encoder,
        llm_params=local_llm_params,
        context_builder_params=local_context_params,
        # response_type="multiple paragraphs",
        response_type="Single Sentence",
    )

    # 设置全局搜索引擎
    global_context_builder = GlobalCommunityContext(
        community_reports=reports,
        entities=entities,
        token_encoder=token_encoder,
    )

    global_context_builder_params = {
        "use_community_summary": False,
        "shuffle_data": True,
        "include_community_rank": True,
        "min_community_rank": 0,
        "community_rank_name": "rank",
        "include_community_weight": True,
        "community_weight_name": "occurrence weight",
        "normalize_community_weight": True,
        # "max_tokens": 12_000,
        "max_tokens": 4096,
        "context_name": "Reports",
    }

    map_llm_params = {
        "max_tokens": 1000,
        "temperature": 0.0,
        "response_format": {"type": "json_object"},
    }

    reduce_llm_params = {
        "max_tokens": 2000,
        "temperature": 0.0,
    }

    global_search_engine = GlobalSearch(
        llm=llm,
        context_builder=global_context_builder,
        token_encoder=token_encoder,
        # max_data_tokens=12_000,
        max_data_tokens=4096,
        map_llm_params=map_llm_params,
        reduce_llm_params=reduce_llm_params,
        allow_general_knowledge=False,
        json_mode=True,
        context_builder_params=global_context_builder_params,
        concurrent_coroutines=1,
        # response_type="multiple paragraphs",
        response_type="Single Sentence",
    )

    graphrag_logger.info("搜索引擎设置完成")
    return local_search_engine, global_search_engine, local_context_builder, local_llm_params, local_context_params


# 格式化响应，对输入的文本进行段落分隔、添加适当的换行符，以及在代码块中增加标记，以便生成更具可读性的输出
def format_response(response):
    # 使用正则表达式 \n{2, }将输入的response按照两个或更多的连续换行符进行分割。这样可以将文本分割成多个段落，每个段落由连续的非空行组成
    paragraphs = re.split(r'\n{2,}', response)
    # 空列表，用于存储格式化后的段落
    formatted_paragraphs = []
    # 遍历每个段落进行处理
    for para in paragraphs:
        # 检查段落中是否包含代码块标记
        if '```' in para:
            # 将段落按照```分割成多个部分，代码块和普通文本交替出现
            parts: List[str] = para.split('```')
            for i, part in enumerate(parts):
                # 检查当前部分的索引是否为奇数，奇数部分代表代码块
                if i % 2 == 1:  # 这是代码块
                    # 将代码块部分用换行符和```包围，并去除多余的空白字符
                    parts[i] = f'\n```\n{part.strip()}\n```\n'
            # 将分割后的部分重新组合成一个字符串
            para = ''.join(parts)
        else:
            # 否则，将句子中的句点后面的空格替换为换行符，以便句子之间有明确的分隔
            para = para.replace('. ', '.\n')
        # 将格式化后的段落添加到formatted_paragraphs列表
        # strip()方法用于移除字符串开头和结尾的空白字符（包括空格、制表符 \t、换行符 \n等）
        formatted_paragraphs.append(para.strip())
    # 将所有格式化后的段落用两个换行符连接起来，以形成一个具有清晰段落分隔的文本
    return '\n'.join(formatted_paragraphs)


# 定义一个异步生成器函数，用于生成流式数据
async def predict(search_result: AsyncGenerator[str, Any], prompt, model):
    """将流式返回的数据格式化为ChatCompletionStreamResponse并生成流数据"""
    full_response = ''
    # 生成最后一个片段，表示流式响应的结束
    first_chunk = ChatCompletionResponse(
        model=model,
        choices=[
            ChatCompletionResponseStreamChoice(
                index=0,
                delta=Delta(role='assistant'),
            )
        ],
        # 使用情况
        usage=UsageInfo(
            # 提示文本的tokens数量
            prompt_tokens=count_tokens(prompt),
            # 完成文本的tokens数量
            completion_tokens=count_tokens(full_response),
            # 总tokens数量
            total_tokens=count_tokens(prompt) + count_tokens(full_response)
        )
    )
    # 返回生成的 JSON 格式的流
    data = first_chunk.model_dump_json(exclude_unset=True, exclude_none=True)
    yield f"data: {data}\n\n"
    graphrag_logger.info(f"开始发送响应: \n{data}\n")
    async for chunk_response in search_result:
        full_response += chunk_response
        # 每个流片段的格式化
        chunk = ChatCompletionResponse(
            model=model,
            choices=[
                ChatCompletionResponseStreamChoice(
                    index=0,
                    delta=Delta(role='assistant', content=chunk_response),  # chunk_response 是生成器的内容
                    finish_reason=None
                )
            ],
            # 使用情况
            usage=UsageInfo(
                # 提示文本的tokens数量
                prompt_tokens=count_tokens(prompt),
                # 完成文本的tokens数量
                completion_tokens=count_tokens(full_response),
                # 总tokens数量
                total_tokens=count_tokens(prompt) + count_tokens(full_response)
            )
        )
        # 返回生成的 JSON 格式的流
        data = chunk.model_dump_json(exclude_unset=True, exclude_none=True)  # SSE 协议要求格式化为 `data: {json}` 的形式
        yield f"data: {data}\n\n"  # SSE协议的标准, 在流式数据传输时, 使用换行符来标识消息结束
    graphrag_logger.info(f"LLM结果: \n{[full_response]}")
    # 生成最后一个片段，表示流式响应的结束
    final_chunk = ChatCompletionResponse(
        model=model,
        choices=[
            ChatCompletionResponseStreamChoice(
                index=0,
                delta=Delta(role='assistant', content=''),
                finish_reason='stop'
            )
        ],
        # 使用情况
        usage=UsageInfo(
            # 提示文本的tokens数量
            prompt_tokens=count_tokens(prompt),
            # 完成文本的tokens数量
            completion_tokens=count_tokens(full_response),
            # 总tokens数量
            total_tokens=count_tokens(prompt) + count_tokens(full_response)
        )
    )
    # 返回生成的 JSON 格式的流
    data = final_chunk.model_dump_json(exclude_unset=True, exclude_none=True)
    yield f"data: {data}\n\n"
    yield "data: [DONE]\n\n"


# 执行全模型搜索，包括本地检索、全局检索
async def full_model_search(prompt: str, role_prompt, history: ConversationHistory):
    local_result = await local_search_engine.asearch(prompt, role_prompt, history)
    global_result = await global_search_engine.asearch(prompt, role_prompt, history)
    # 格式化结果
    formatted_result = "#综合搜索结果:\n"
    formatted_result += "##本地检索结果:\n"
    formatted_result += local_result.response + "\n"
    formatted_result += "##全局检索结果:\n"
    formatted_result += global_result.response + "\n"
    return formatted_result


# 执行全模型搜索，包括本地检索、全局检索
async def stream_full_model_search(prompt: str, role_prompt, history: ConversationHistory, model):
    local_result = await local_search_engine.asearch(prompt, role_prompt, history)
    global_result = await global_search_engine.asearch(prompt, role_prompt, history)
    # 格式化结果
    formatted_result = "#综合搜索结果:\n"
    formatted_result += "##本地检索结果:\n"
    formatted_result += format_response(local_result.response) + "\n"
    formatted_result += "##全局检索结果:\n"
    formatted_result += format_response(global_result.response) + "\n"
    full_response = formatted_result
    # 生成最后一个片段，表示流式响应的结束
    result = ChatCompletionResponse(
        model=model,
        choices=[
            ChatCompletionResponseStreamChoice(
                index=0,
                delta=Delta(role='assistant'),
                finish_reason='stop'
            )
        ],
        # 使用情况
        usage=UsageInfo(
            # 提示文本的tokens数量
            prompt_tokens=count_tokens(prompt),
            # 完成文本的tokens数量
            completion_tokens=count_tokens(full_response),
            # 总tokens数量
            total_tokens=count_tokens(prompt) + count_tokens(full_response)
        )
    )
    # 返回生成的 JSON 格式的流
    data = result.model_dump_json(exclude_unset=True, exclude_none=True)
    yield f"data: {data}\n\n"
    graphrag_logger.info(f"发送响应: \n{data}\n")
    yield "data: [DONE]\n\n"


@graphrag_app.get("/")
async def index():
    service_name = """
        <html> <head> <title>graphrag_service</title> </head>
            <body style="display: flex; justify-content: center;"> <h1>graphrag_service</h1></body> </html>
        """
    return HTMLResponse(status_code=200, content=service_name)


@graphrag_app.get("/http_check")
@graphrag_app.get("/health")
async def health():
    """Health check."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    health_data = {"status": "healthy", "timestamp": timestamp}
    # 返回JSON格式的响应
    return JSONResponse(status_code=200, content=health_data)


# POST请求接口，与大模型进行知识问答
@graphrag_app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    request_data = request.model_dump()
    graphrag_logger.info(f"收到聊天完成请求: {request_data}")
    llm_model = request.model
    knowledge = request.knowledge
    role_prompt = all_role_prompt[knowledge]
    status = await refresh_models(llm_model, knowledge)
    # 检查搜索引擎是否初始化
    if not local_search_engine or not global_search_engine:
        graphrag_logger.error("搜索引擎未初始化")
        raise HTTPException(status_code=500, detail="搜索引擎未初始化")

    try:
        stream = request.stream
        messages = request.messages
        prompt = messages.pop()['content']  # 获取最后一轮对话的用户问题
        # prompt = '你的身份是黄志青博士，你能普及一些关于环保的知识。' + prompt
        # prompt += ', 不需要给出数据引用，尽可能简短地回答: '
        history = ConversationHistory.from_list(messages)  # 历史记录
        graphrag_logger.info(f"处理问题: prompt: {prompt} \n历史记录: history: {history.turns}")

        # 非流式响应处理
        if not stream:
            # 根据模型选择使用不同的搜索方法
            if request.mode == "local":  # 默认使用本地搜索
                search_result = await local_search_engine.asearch(prompt, role_prompt, history)
                full_response = format_response(search_result.response)
            elif request.mode == "global":
                search_result = await global_search_engine.asearch(prompt, role_prompt, history)
                full_response = format_response(search_result.response)
            elif request.mode == "full":
                search_result = await full_model_search(prompt, role_prompt, history)
                full_response = format_response(search_result)
            else:
                full_response = 'not support mode'
            graphrag_logger.info(f"LLM结果:\n{[full_response]}")
            response = ChatCompletionResponse(
                model=request.model,
                choices=[
                    ChatCompletionResponseChoice(
                        index=0,
                        message=Message(role="assistant", content=full_response),
                        finish_reason="stop"
                    )
                ],
                # 使用情况
                usage=UsageInfo(
                    # 提示文本的tokens数量
                    prompt_tokens=count_tokens(prompt),
                    # 完成文本的tokens数量
                    completion_tokens=count_tokens(full_response),
                    # 总tokens数量
                    total_tokens=count_tokens(prompt) + count_tokens(full_response)
                )
            )
            graphrag_logger.info(f"发送响应: \n{response}\n")
            # 返回JSONResponse对象，其中content是将response对象转换为字典的结果
            return JSONResponse(content=response.model_dump())
        # 流式响应处理
        elif stream:
            # 根据模型选择使用不同的搜索方法
            if request.mode == "local":  # 默认使用本地搜索
                search_result = local_search_engine.astream_search(prompt, role_prompt, history)
            elif request.mode == "global":
                search_result = global_search_engine.astream_search(prompt, role_prompt, history)
            elif request.mode == "full":
                search_result = stream_full_model_search(prompt, history, role_prompt, llm_model)
            else:
                async def async_iter(item):
                    yield item  # 异步生成器返回错误信息
                search_result = async_iter(item='not support request.mode')  # 将普通的字符串转为异步生成器
            generator = predict(search_result, prompt, llm_model)
            # 返回StreamingResponse对象，流式传输数据，media_type设置为text/event-stream以符合SSE(Server-SentEvents) 格式
            return StreamingResponse(generator, media_type="text/event-stream")
    except Exception as e:
        graphrag_logger.error(f"处理聊天完成时出错:\n {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# GET请求接口，获取可用模型列表
@graphrag_app.get("/v1/models")
async def list_models():
    graphrag_logger.info("收到模型列表请求")
    model_cards = [ModelCard(id=CURRENT_MODEL, mode='local', owner='graphrag'),
                   ModelCard(id=CURRENT_MODEL, mode='global', owner='graphrag'),
                   ModelCard(id=CURRENT_MODEL, mode='full', owner='combined')]
    model_list = ModelList(data=model_cards)
    graphrag_logger.info(f"发送模型列表: {model_list}")
    return JSONResponse(content=model_list)


if __name__ == "__main__":
    asyncio.run(init_app())
    graphrag_logger.info(f"在端口 {PORT} 上启动知识图谱Graphrag服务器")
    # uvicorn是一个用于运行ASGI应用的轻量级、超快速的ASGI服务器实现
    # 用于部署基于FastAPI框架的异步PythonWeb应用程序
    uvicorn.run(graphrag_app, host="0.0.0.0", port=8013)


