import pandas as pd

GRAPHRAG_FOLDER = '/home/zxd/code/Chat/knowledge_graphrag/project/dentistry/output/artifacts'
files = ['create_final_documents.parquet', 'create_final_text_units.parquet', 'create_final_entities.parquet',
         'create_final_relationships.parquet',
         'create_final_communities.parquet', 'create_final_community_reports.parquet',
         'create_final_covariates.parquet']
file = files[0]
file = 'create_base_text_units.parquet'
parquet_path = f'{GRAPHRAG_FOLDER}/{file}'
# 读取 Parquet 文件
df = pd.read_parquet(parquet_path
                     # , columns=["name", "type", "description", "human_readable_id", "id", "description_embedding", "text_unit_ids"]
                     )

# 查看数据
print("原始数据:")
# print(df.head())
# result = df[df['name'] == '广州众易用智能科技有限公司']
# result = df.iloc[21]
# print(result)

# index = 20
# print(f'---{index}---')
# content = df.at[index, 'chunk']
# print(content)


# content = df.at[40, 'name', 'description', 'type']
# texts = df['text']
# for i, text in enumerate(texts):
#     print(f'---{i}---', text)
# type = list(set(df['type']))
# print(type)

# # 添加新列
# df['new_column'] = df['existing_column'] * 2
#
# # 修改现有列
# df['existing_column'] = df['existing_column'].apply(lambda x: x + 1)
#
# # 删除列
# df = df.drop(columns=['column_to_delete'])
# 删除行
# df = df.drop(df.index[21])
#
# # 将修改后的 DataFrame 写入新的 Parquet 文件
df.to_parquet(parquet_path, index=False)
#
# print("修改后的数据:")
# print(df.head())
