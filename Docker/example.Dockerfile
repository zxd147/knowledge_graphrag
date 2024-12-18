# 基础镜像
FROM base/python:ubuntu22.04-cuda11.8-python3.10

# 设置代理 (确保网络环境)
#ENV all_proxy=http://192.168.0.64:7890
# 使用 nvidia 容器运行时支持 GPU
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=all
# 设置访问密钥
ENV GRAPHRAG-SECRET-KEY=sk-graphrag

# 设置工作目录
WORKDIR /app/graphrag

# 安装依赖环境
RUN apt-get update && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 拉取代码
RUN git clone https://github.com/zxd147/knowledge_graphrag.git /app/graphrag

# 安装依赖环境
RUN pip install -r ./requirements.txt && pip cache purge

# 暴露容器端口
EXPOSE 8013

# 运行启动命令
CMD ["python", "graphrag_api.py"]
