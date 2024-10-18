
import re
import json
import logging

log = logging.getLogger(__name__)


def try_parse_json_object(input: str) -> tuple[str, dict]:
    """JSON cleaning and formatting utilities."""
    # Sometimes, the LLM returns a json string with some extra description, this function will clean it up.

    result = None
    try:
        # Try parse first
        result = json.loads(input)
        print("success load json in step 1\n", result)
    except json.JSONDecodeError:
        print("Warning: fail to decoding faulty json, attempting repair, attempt to clean up input strings and Markdown frameworks")

    if result:
        return input, result

    _pattern = r"\{(.*)\}"
    _match = re.search(_pattern, input)
    input = "{" + _match.group(1) + "}" if _match else input

    # Clean up json string.
    input = (
        input.replace("{{", "{")
        .replace("}}", "}")
        .replace('"[{', "[{")
        .replace('}]"', "}]")
        .replace("\\", " ")
        .replace("\\n", " ")
        .replace("\n", " ")
        .replace("\r", "")
        .strip()
    )

    # Remove JSON Markdown Frame
    if input.startswith("```json"):
        input = input[len("```json") :]
    if input.endswith("```"):
        input = input[: len(input) - len("```")]

    try:
        result = json.loads(input)
        print("success load json in step 2\n", result)
    except json.JSONDecodeError:
        print(f"Error: JSONDecodeError{input}")

        # Fixup potentially malformed json string using json_repair.
        # input = str(repair_json(json_str=input, return_objects=False))

        # Generate JSON-string output using best-attempt prompting & parsing techniques.
        try:
            result = json.loads(input)
        except json.JSONDecodeError:
            print(f"Execption: JSONDecodeError, error loading json, json={input}")
            return input, {}
        else:
            if not isinstance(result, dict):
                print("Execption: not expected dict type. type=%s:", type(result))
                return input, {}
            print("success load json in step 3\n", result)
            return input, result
    else:
        return input, result



# 打开文件并读取内容
with open("json_str.txt", "r", encoding="utf-8") as file:
    text = file.read()

text = '{\"title\": \"\\u7259\\u79d1\\u533b\\u7597\\u793e\\u533a\\u5206\\u6790\\u62a5\\u544a\\uff1a\\u5e74\\u9f84\\u7fa4\\u4f53\\u4e0e\\u5065\\u5eb7\\u72b6\\u51b5\\u7684\\u5173\\u8054\\u6027\\u7814\\u7a76\", \"summary\": \"\\u672c\\u62a5\\u544a\\u63a2\\u8ba8\\u4e86\\u7259\\u79d1\\u533b\\u7597\\u793e\\u533a\\u4e2d\\u5e74\\u9f84\\u7fa4\\u4f53\\u4e0e\\u5065\\u5eb7\\u72b6\\u51b5\\u4e4b\\u95f4\\u7684\\u5173\\u8054\\u6027\\uff0c\\u91cd\\u70b9\\u5173\\u6ce8\\u4e34\\u5e8a\\u8bd5\\u9a8c\\u3001\\u9884\\u9632\\u63aa\\u65bd\\u3001\\u6cbb\\u7597\\u65b9\\u6848\\u3001\\u5eb7\\u590d\\u63aa\\u65bd\\u7b49\\u5173\\u952e\\u9886\\u57df\\u3002\\u901a\\u8fc7\\u5206\\u6790\\u4e0d\\u540c\\u5e74\\u9f84\\u7fa4\\u4f53\\u7684\\u5065\\u5eb7\\u72b6\\u51b5\\u3001\\u6cbb\\u7597\\u65b9\\u6cd5\\u548c\\u5eb7\\u590d\\u7b56\\u7565\\uff0c\\u63ed\\u793a\\u4e86\\u5e74\\u9f84\\u56e0\\u7d20\\u5728\\u7259\\u79d1\\u533b\\u7597\\u51b3\\u7b56\\u4e2d\\u7684\\u91cd\\u8981\\u6027\\u3002\", \"rating\": 7.5, \"rating_explanation\": \"\\u6b64\\u62a5\\u544a\\u5728\\u7259\\u79d1\\u533b\\u7597\\u9886\\u57df\\u63d0\\u4f9b\\u4e86\\u6df1\\u5165\\u7684\\u89c1\\u89e3\\uff0c\\u5f3a\\u8c03\\u4e86\\u5e74\\u9f84\\u56e0\\u7d20\\u5bf9\\u5065\\u5eb7\\u72b6\\u51b5\\u3001\\u6cbb\\u7597\\u65b9\\u6cd5\\u548c\\u5eb7\\u590d\\u7b56\\u7565\\u7684\\u5f71\\u54cd\\uff0c\\u5bf9\\u4fc3\\u8fdb\\u7259\\u79d1\\u5065\\u5eb7\\u548c\\u793e\\u533a\\u7406\\u89e3\\u5177\\u6709\\u4e2d\\u7b49\\u81f3\\u9ad8\\u91cd\\u8981\\u6027\\u3002\", \"findings\": [{\"summary\": \"\\u62a5\\u544a\\u7ed3\\u675f\", \"explanation\": \"\\u672c\\u62a5\\u544a\\u5230\\u6b64\\u7ed3\\u675f\\uff0c\\u611f\\u8c22\\u60a8\\u7684\\u9605\\u8bfb\\u3002\\u5982\\u6709\\u4efb\\u4f55\\u7591\\u95ee\\u6216\\u5efa\\u8bae\\uff0c\\u8bf7\\u968f\\u65f6\\u4e0e\\u6211\\u4eec\\u8054\\u7cfb\\u3002[Data: \\u5e74\\u9f84\\u7fa4\\u4f53\\uff08132\\uff09\\uff0c\\u5065\\u5eb7\\u72b6\\u51b5\\uff0843\\uff09\\uff0c\\u4e34\\u5e8a\\u8bd5\\u9a8c\\uff0887\\uff09\\uff0c\\u9884\\u9632\\u63aa\\u65bd\\uff0875\\uff09\\uff0c\\u6cbb\\u7597\\u65b9\\u6848\\uff08103\\uff09\\uff0c\\u5eb7\\u590d\\u63aa\\u65bd\\uff0895\\uff09\\uff0c+more]\"}]}'
# 解析JSON字符串
# decoded_data = json.loads(text)
decoded_data = try_parse_json_object(text)

# 打印解析后的数据
print(json.dumps(decoded_data, ensure_ascii=False, indent=4))

