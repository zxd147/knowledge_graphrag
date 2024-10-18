import asyncio
import os
import pandas as pd
import tiktoken
from IPython.display import display
from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey
from yfiles_jupyter_graphs import GraphWidget
from graphrag.query.indexer_adapters import (
    read_indexer_covariates,
    read_indexer_entities,
    read_indexer_relationships,
    read_indexer_reports,
    read_indexer_text_units,
)
from graphrag.query.input.loaders.dfs import (
    store_entity_semantic_embeddings,
)
from graphrag.query.llm.oai.chat_openai import ChatOpenAI
from graphrag.query.llm.oai.embedding import OpenAIEmbedding
from graphrag.query.llm.oai.typing import OpenaiApiType
from graphrag.query.structured_search.local_search.mixed_context import (
    LocalSearchMixedContext,
)
from graphrag.query.structured_search.local_search.search import LocalSearch
from graphrag.vector_stores.lancedb import LanceDBVectorStore

INPUT_DIR = "../../inputs/operation dulce"
LANCEDB_URI = f"{INPUT_DIR}/lancedb"
COMMUNITY_REPORT_TABLE = "create_final_community_reports"
ENTITY_TABLE = "create_final_nodes"
ENTITY_EMBEDDING_TABLE = "create_final_entities"
RELATIONSHIP_TABLE = "create_final_relationships"
COVARIATE_TABLE = "create_final_covariates"
TEXT_UNIT_TABLE = "create_final_text_units"
COMMUNITY_LEVEL = 2
# read nodes table to get community and degree data
entity_df = pd.read_parquet(f"{INPUT_DIR}/{ENTITY_TABLE}.parquet")
entity_embedding_df = pd.read_parquet(f"{INPUT_DIR}/{ENTITY_EMBEDDING_TABLE}.parquet")
relationship_df = pd.read_parquet(f"{INPUT_DIR}/{RELATIONSHIP_TABLE}.parquet")
relationships = read_indexer_relationships(relationship_df)
# converts the entities dataframe to a list of dicts for yfiles-jupyter-graphs


def convert_entities_to_dicts(df):
    """Convert the entities dataframe to a list of dicts for yfiles-jupyter-graphs."""
    nodes_dict = {}
    for _, row in df.iterrows():
        # Create a dictionary for each row and collect unique nodes
        node_id = row["title"]
        if node_id not in nodes_dict:
            nodes_dict[node_id] = {
                "id": node_id,
                "properties": row.to_dict(),
            }
    return list(nodes_dict.values())


# converts the relationships dataframe to a list of dicts for yfiles-jupyter-graphs
def convert_relationships_to_dicts(df):
    """Convert the relationships dataframe to a list of dicts for yfiles-jupyter-graphs."""
    relationships = []
    for _, row in df.iterrows():
        # Create a dictionary for each row
        relationships.append({
            "start": row["source"],
            "end": row["target"],
            "properties": row.to_dict(),
        })
    return relationships


w = GraphWidget()
w.directed = True
w.nodes = convert_entities_to_dicts(entity_df)
w.edges = convert_relationships_to_dicts(relationship_df)
# show title on the node
w.node_label_mapping = "title"


# map community to a color
def community_to_color(community):
    """Map a community to a color."""
    colors = [
        "crimson",
        "darkorange",
        "indigo",
        "cornflowerblue",
        "cyan",
        "teal",
        "green",
    ]
    return (
        colors[int(community) % len(colors)] if community is not None else "lightgray"
    )


def edge_to_source_community(edge):
    """Get the community of the source node of an edge."""
    source_node = next(
        (entry for entry in w.nodes if entry["properties"]["title"] == edge["start"]),
        None,
    )
    source_node_community = source_node["properties"]["community"]
    return source_node_community if source_node_community is not None else None


async def main():
    w.node_color_mapping = lambda node: community_to_color(node["properties"]["community"])
    w.edge_color_mapping = lambda edge: community_to_color(edge_to_source_community(edge))
    # map size data to a reasonable factor
    w.node_scale_factor_mapping = lambda node: 0.5 + node["properties"]["size"] * 1.5 / 20
    # use weight for edge thickness
    w.edge_thickness_factor_mapping = "weight"
    # Use the circular layout for this visualization. For larger graphs, the default organic layout is often preferrable.
    w.circular_layout()
    display(w)
    # setup (see also ../../local_search.ipynb)
    entities = read_indexer_entities(entity_df, entity_embedding_df, COMMUNITY_LEVEL)

    description_embedding_store = LanceDBVectorStore(
        collection_name="entity_description_embeddings",
    )
    description_embedding_store.connect(db_uri=LANCEDB_URI)
    entity_description_embeddings = store_entity_semantic_embeddings(
        entities=entities, vectorstore=description_embedding_store
    )
    covariate_df = pd.read_parquet(f"{INPUT_DIR}/{COVARIATE_TABLE}.parquet")
    claims = read_indexer_covariates(covariate_df)
    covariates = {"claims": claims}
    report_df = pd.read_parquet(f"{INPUT_DIR}/{COMMUNITY_REPORT_TABLE}.parquet")
    reports = read_indexer_reports(report_df, entity_df, COMMUNITY_LEVEL)
    text_unit_df = pd.read_parquet(f"{INPUT_DIR}/{TEXT_UNIT_TABLE}.parquet")
    text_units = read_indexer_text_units(text_unit_df)

    api_key = os.environ["GRAPHRAG_API_KEY"]
    llm_model = os.environ["GRAPHRAG_LLM_MODEL"]
    embedding_model = os.environ["GRAPHRAG_EMBEDDING_MODEL"]

    llm = ChatOpenAI(
        api_key=api_key,
        model=llm_model,
        api_type=OpenaiApiType.OpenAI,  # OpenaiApiType.OpenAI or OpenaiApiType.AzureOpenAI
        max_retries=20,
    )

    token_encoder = tiktoken.get_encoding("cl100k_base")

    text_embedder = OpenAIEmbedding(
        api_key=api_key,
        api_base=None,
        api_type=OpenaiApiType.OpenAI,
        model=embedding_model,
        deployment_name=embedding_model,
        max_retries=20,
    )

    context_builder = LocalSearchMixedContext(
        community_reports=reports,
        text_units=text_units,
        entities=entities,
        relationships=relationships,
        covariates=covariates,
        entity_text_embeddings=description_embedding_store,
        embedding_vectorstore_key=EntityVectorStoreKey.ID,  # if the vectorstore uses entity title as ids, set this to EntityVectorStoreKey.TITLE
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
        "embedding_vectorstore_key": EntityVectorStoreKey.ID,  # set this to EntityVectorStoreKey.TITLE if the vectorstore uses entity title as ids
        "max_tokens": 12_000,  # change this based on the token limit you have on your model (if you are using a model with 8k limit, a good setting could be 5000)
    }

    llm_params = {
        "max_tokens": 2_000,  # change this based on the token limit you have on your model (if you are using a model with 8k limit, a good setting could be 1000=1500)
        "temperature": 0.0,
    }

    search_engine = LocalSearch(
        llm=llm,
        context_builder=context_builder,
        token_encoder=token_encoder,
        llm_params=llm_params,
        context_builder_params=local_context_params,
        response_type="multiple paragraphs",  # free form text describing the response type and format, can be anything, e.g. prioritized list, single paragraph, multiple paragraphs, multiple-page report
    )
    result = await search_engine.asearch("Tell me about Agent Mercer")
    print(result.response)
    question = "Tell me about Dr. Jordan Hayes"
    result = await search_engine.asearch(question)
    print(result.response)
    result.context_data["entities"].head()
    result.context_data["relationships"].head()
    """
    Helper function to visualize the result context with `yfiles-jupyter-graphs`.

    The dataframes are converted into supported nodes and relationships lists and then passed to yfiles-jupyter-graphs.
    Additionally, some values are mapped to visualization properties.
    """

    def show_graph(result):
        """Visualize the result context with yfiles-jupyter-graphs."""
        from yfiles_jupyter_graphs import GraphWidget

        if (
                "entities" not in result.context_data
                or "relationships" not in result.context_data
        ):
            msg = "The passed results do not contain 'entities' or 'relationships'"
            raise ValueError(msg)

        # converts the entities dataframe to a list of dicts for yfiles-jupyter-graphs
        def convert_entities_to_dicts(df):
            """Convert the entities dataframe to a list of dicts for yfiles-jupyter-graphs."""
            nodes_dict = {}
            for _, row in df.iterrows():
                # Create a dictionary for each row and collect unique nodes
                node_id = row["entity"]
                if node_id not in nodes_dict:
                    nodes_dict[node_id] = {
                        "id": node_id,
                        "properties": row.to_dict(),
                    }
            return list(nodes_dict.values())

        # converts the relationships dataframe to a list of dicts for yfiles-jupyter-graphs
        def convert_relationships_to_dicts(df):
            """Convert the relationships dataframe to a list of dicts for yfiles-jupyter-graphs."""
            relationships = []
            for _, row in df.iterrows():
                # Create a dictionary for each row
                relationships.append({
                    "start": row["source"],
                    "end": row["target"],
                    "properties": row.to_dict(),
                })
            return relationships

        w = GraphWidget()
        # use the converted data to visualize the graph
        w.nodes = convert_entities_to_dicts(result.context_data["entities"])
        w.edges = convert_relationships_to_dicts(result.context_data["relationships"])
        w.directed = True
        # show title on the node
        w.node_label_mapping = "entity"
        # use weight for edge thickness
        w.edge_thickness_factor_mapping = "weight"
        display(w)

    show_graph(result)


# 在 PyCharm 中需要这样启动事件循环
if __name__ == "__main__":
    asyncio.run(main())

















