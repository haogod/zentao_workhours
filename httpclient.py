import http.client
import json

class ZentaoSessionClient:
    def __init__(self, host):
        """初始化客户端
        
        Args:
            host: 服务器主机地址，如"172.16.2.72"
        """
        self.host = host
        self.session_id = None  # 存储sessionID的变量
        self.conn = None
        
    def _create_connection(self):
        """创建HTTP连接"""
        self.conn = http.client.HTTPConnection(self.host)
        
    def _get_headers(self):
        """构建请求头"""
        return {
            'Accept': "*/*",
            'Accept-Encoding': "gzip, deflate, br",
            'User-Agent': "PostmanRuntime-ApipostRuntime/1.1.0",
            'Connection': "keep-alive",
            'Cookie': "zentaosid=a16b740fbdc5be507dd1668e89bb9f39;lang=zh-cn;vision=rnd;device=desktop;theme=default;preExecutionID=133;executionTaskOrder=status%2Cid_desc;lastProject=125;lastProject=125"
        }
        
    def get_session_id(self):
        """获取sessionID并存储到实例变量中"""
        try:
            self._create_connection()
            payload = ""
            url = "/zentao/index.php?m=api&f=getSessionID&t=json"
            
            self.conn.request("GET", url, payload, self._get_headers())
            res = self.conn.getresponse()
            data = res.read()
                
            data = data.json()
            data_str = data['data']
            data_dict = json.loads(data_str)
            session_id = data_dict['sessionID']
            self.zentaosid = session_id
            return self.zentaosid
            # 假设返回的是JSON格式，这里简化处理，实际可能需要解析JSON
            response_data = data.decode("utf-8")
            # 这里需要根据实际返回格式提取sessionID
            # 示例：如果返回的是{"sessionID": "xxx"}，则可以使用json解析
            # import json
            # result = json.loads(response_data)
            # self.session_id = result.get('sessionID')
            
            # 暂时直接存储原始响应，实际使用时请根据返回格式修改
            self.session_id = response_data
            return self.session_id
            
        except Exception as e:
            print(f"获取sessionID失败: {str(e)}")
            return None
        finally:
            if self.conn:
                self.conn.close()

# 使用示例
if __name__ == "__main__":
    client = ZentaoSessionClient("172.16.2.72")
    session_id = client.get_session_id()
    print(f"获取到的sessionID: {session_id}")
    # 可以通过client.session_id访问存储的sessionID
    print(f"存储的sessionID: {client.session_id}")
