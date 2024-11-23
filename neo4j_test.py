from neo4j import GraphDatabase

# 定义连接信息
NEO4J_URI = "bolt://192.168.0.245:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "12345678"


class Neo4jConnection:
    def __init__(self, uri, username, password):
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None

    def connect(self):
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            print("连接成功！")
        except Exception as e:
            print(f"连接失败: {e}")

    def close(self):
        if self.driver is not None:
            self.driver.close()
            print("连接已关闭。")

    def test_connection(self):
        with self.driver.session() as session:
            # try:
                result = session.run("MATCH (n) RETURN count(n) AS count")
                count = result.single()["count"]
                print(f"数据库中节点的数量: {count}")
            # except Exception as e:
            #     print(f"查询失败: {e}")


# 使用 Neo4jConnection 类
if __name__ == "__main__":
    conn = Neo4jConnection(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    conn.connect()
    if conn.driver is not None:
        conn.test_connection()
    conn.close()
