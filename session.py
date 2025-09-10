import http.client
class ZenTaoAPI:
    def send_request():
        # 服务器地址
        server_host = "172.16.2.72"

        # Session ID（从Cookie中提取）
        session_id = "a16b740fbdc5be507dd1668e89bb9f39"

        # 查询参数
        query_params = {
            "m": "project",
            "f": "browse",
            "t": "json"
        }

        # 构建查询字符串
        query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
        request_path = f"/index.php?{query_string}"

        # 请求头
        headers = {
            'Accept': "*/*",
            'Accept-Encoding': "gzip, deflate, br",
            'User-Agent': "PostmanRuntime-ApipostRuntime/1.1.0",
            'Connection': "keep-alive",
            'Cookie': f"zentaosid={session_id};lang=zh-cn;vision=rnd;device=desktop;theme=default;preExecutionID=133;executionTaskOrder=status%2Cid_desc;lastProject=125;lastProject=125"
        }

        # 发送请求
        conn = http.client.HTTPConnection(server_host)
        payload = ""
        conn.request("GET", request_path, payload, headers)

        # 获取响应
        res = conn.getresponse()
        data = res.read()

        # 输出结果
        print(data.decode("utf-8"))

        # 关闭连接
        conn.close()

