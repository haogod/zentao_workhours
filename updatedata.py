import requests
import http.client
import json
from projectcsv import projectcsv
from executioncsv import executioncsv
from taskcsv import taskcsv


class ZenTaoAPI:
    def __init__(self, base_url, account, password):
        self.base_url = base_url.rstrip('/')
        self.account = account
        self.password = password
        self.zentaosid = None
        self.session = requests.Session()
        self.project_ids = []  # 用于存储项目ID列表
        self.execution_ids =[] 
        self.task_ids =[]

    def get_session_id(self):
        url = f"{self.base_url}/index.php?m=api&f=getSessionID&t=json"
        resp = self.session.get(url)
        resp.raise_for_status()
        data = resp.json()
        data_str = data['data']
        data_dict = json.loads(data_str)
        session_id = data_dict['sessionID']
        self.zentaosid = session_id
        return self.zentaosid

    def login(self):
        if not self.zentaosid:
            self.get_session_id()
        login_url = (
            f"{self.base_url}/index.php?m=user&f=login&t=json"
            f"&account={self.account}&password={self.password}&zentaosid={self.zentaosid}"
        )
        resp = self.session.get(login_url)
        resp.raise_for_status()
        return resp.json()

    def get_projects(self):
        if not self.zentaosid:
            self.login()
        projects_url = f"{self.base_url}/index.php?m=project&f=browse&t=json"
        
   
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",  # 关键：模拟AJAX请求
            "Content-Type": "application/json"  # 若传JSON参数，必须指定
        }
        cookies = {'zentaosid': self.zentaosid}
        resp = self.session.get(projects_url, cookies=cookies,headers=headers)
        resp.raise_for_status()
        
        return resp.json()

    def projectcsv(self):
            # 服务器地址
        server_host = "172.16.2.72"

        # Session ID（从Cookie中提取）
        session_id = self.zentaosid

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

        # 将数据转换为JSON格式
        json_data = json.loads(data)
        print(json_data)

        projectcsv().translatecsv(json_data,'./zentao_project.csv') 
        self.project_ids = projectcsv().getprojectid(json_data)
        # 关闭连接
        conn.close()
    # 生成所有的project下的execution数据
    def executioncsv(self):
        session_id = self.zentaosid


        headers = {
        'Accept': "*/*",
        'Accept-Encoding': "gzip, deflate, br",
        'User-Agent': "PostmanRuntime-ApipostRuntime/1.1.0",
        'Connection': "keep-alive",
        'Cookie': f"zentaosid={session_id};lang=zh-cn;vision=rnd;device=desktop;theme=default;preExecutionID=133;executionTaskOrder=status%2Cid_desc;lastProject=125;lastProject=125"
    }
    
    # 禅道服务器地址固定（未变量化）
        conn = http.client.HTTPConnection("172.16.2.72")
        payload = ""

        if not self.project_ids:
            print("project_ids为空")
            return
        # 遍历所有项目ID（核心变量，可动态修改）
        for project_id in self.project_ids:
            try:
                # 构建带项目ID变量的URL（禅道路径“/index.php”固定）
                url = f"/index.php?m=project&f=execution&status=undone&projectID={project_id}&t=json"

                # 发送GET请求
                conn.request("GET", url, payload, headers)

                # 获取响应并读取数据
                res = conn.getresponse()
                data = res.read()

                # 打印每个项目的响应结果
                # print(f"项目ID: {project_id} 的响应数据:")
                # print(data.decode("utf-8"))
                # print("-" * 50)  # 分隔线，区分不同项目结果

                executioncsv().execution_to_csv(json.loads(data),project_id)
                getexecutionids=executioncsv().getexecutionid(json.loads(data))
                self.execution_ids.extend(getexecutionids)
                # 遍历self.execution_ids
                print(f"项目ID: {project_id} 的executionIDs: {getexecutionids}")

            except Exception as e:
                # 捕获异常，避免单个项目访问失败影响整体遍历
                print(f"访问项目ID: {project_id} 时发生错误: {str(e)}")

        # 关闭HTTP连接
        conn.close()

    def taskcsv(self):
        execution_ids = self.execution_ids
        
        # 检查数组是否为空
        if not execution_ids:
            print("错误：executionid数组为空，没有需要处理的ID")
            return
        
        # 创建HTTP连接
        conn = http.client.HTTPConnection("172.16.2.72")
        payload = ""
        
        # 构建请求头（包含动态session_id）
        headers = {
            'Accept': "*/*",
            'Accept-Encoding': "gzip, deflate, br",
            'User-Agent': "PostmanRuntime-ApipostRuntime/1.1.0",
            'Connection': "keep-alive",
            'Cookie': f"zentaosid={self.zentaosid};lang=zh-cn;vision=rnd;device=desktop;theme=default"
        }
        
        # 遍历数组中的每个executionid（核心逻辑）
        for exec_id in execution_ids:
            try:
                # 构建带当前ID的请求URL
                url = f"/index.php?m=execution&f=task&executionID={exec_id}&t=json"
                
                # 发送GET请求
                conn.request("GET", url, payload, headers)
                
                # 获取并处理响应
                res = conn.getresponse()
                data = res.read()
                
                # 打印结果
                # print(f"项目ID: {self.execution_data['projectid']}, ExecutionID: {exec_id} 响应:")
                # print(data.decode("utf-8"))
                # print("-" * 80)

                # 获取taskid并存储
                self.task_ids.extend(taskcsv().gettaskid(json.loads(data))) 
                #print(f"ExecutionID: {exec_id} 的taskIDs: {self.task_ids}")


            except Exception as e:
                print(f"处理ExecutionID: {exec_id} 时出错: {str(e)}")
                print("-" * 80)
        
        # 关闭连接
        conn.close()

    def workhourcsv(self):
        """
        遍历多个taskID并发送HTTP请求

        参数:
            zentaosid: 禅道的session ID
            task_ids: 要访问的taskID数组
        """
        task_ids = self.task_ids
        zentaosid = self.zentaosid  
        # 创建连接
        conn = http.client.HTTPConnection("172.16.2.72")
        payload = ""

        # 构建请求头，包含动态zentaosid
        headers = {
            'Accept': "*/*",
            'Accept-Encoding': "gzip, deflate, br",
            'User-Agent': "PostmanRuntime-ApipostRuntime/1.1.0",
            'Connection': "keep-alive",
            'Cookie': f"zentaosid={zentaosid};lang=zh-cn;vision=rnd;device=desktop;theme=default;preExecutionID=133;executionTaskOrder=status%2Cid_desc;lastProject=125;lastProject=125"
        }

        # 遍历taskID数组
        print(task_ids)
        for task_id in task_ids:
            try:
                # 构建带当前taskID的URL
               
                url = f"/index.php?m=task&f=recordworkhour&taskID={task_id}&t=json"

                # 发送请求
                conn.request("GET", url, payload, headers)

                # 获取响应
                res = conn.getresponse()
                data = res.read()

                # 打印结果
                print(f"taskID: {task_id} 的响应数据:")
                # print(data.decode("utf-8"))
                # print("-" * 80)  # 分隔线

                # 生成workhour CSV文件
                taskcsv().export_efforts_to_csv(json.loads(data))

                # recordworkhours = taskcsv().extract_recordworkhour_fields(json.loads(data))
                # if not recordworkhours:
                #     print(f"task_id {task_id} 没有可导出的工时记录数据")
                # else:    
                #     taskcsv().export_to_csv_by_task(
                #     recordworkhours,
                #     task_id,
                #     folder_name="recordworkhour"
                #     )

                # # 生成effor
                # effortworkhours = taskcsv().extract_editeffort_fields(json.loads(data))
                # if not effortworkhours:
                #     print(f"task_id {task_id} 没有可导出的工时记录数据")
                # else:
                #     taskcsv().export_editeffort_to_csv(
                #         effortworkhours,
                #         folder_name="effortworkhour"
                #         )

            except Exception as e:
                print(f"访问taskID: {task_id} 时发生错误: {str(e)}")
                print("-" * 80)

        # 关闭连接
        conn.close()

 


if __name__ == "__main__":
    api = ZenTaoAPI(
        base_url="http://172.16.2.72/zentao",
        account="zftx",
        password="Zftx1234"
    )
    print("获取SessionID:", api.get_session_id())
    print("登录结果:", api.login())
    # 生成zentao_project.csv文件
    api.projectcsv()
    api.executioncsv()
    api.taskcsv()
    api.workhourcsv()
    
