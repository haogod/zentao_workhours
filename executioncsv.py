import json
import csv
import os

class executioncsv:
    def execution_to_csv(self, json_data, project_id,csv_dir_path='project'):
        """
        将JSON文件中的data字段下的executionStats数据转换为CSV文件，
        保存到project文件夹下，文件名为project_id.csv

        参数:
            json_data(dict): 输入的JSON数据字典
            csv_dir_path(str): 输出的CSV文件夹路径，默认为'project'
        """        
        data_str = json_data['data']
        data = json.loads(data_str)

        # 提取executionStats数据
        execution_stats = data.get('executionStats', [])
        if not execution_stats:
            print('警告:未找到executionStats数据,生成的CSV文件可能为空')
            return 
       
        # 创建project文件夹（如果不存在）
        os.makedirs(csv_dir_path, exist_ok=True)

        # 构建CSV文件路径
        csv_file_path = os.path.join(csv_dir_path, f"{project_id}.csv")

        # 处理特殊字段(列表转字符串)
        for item in execution_stats:
            for key, value in item.items():
                if isinstance(value, list):
                    item[key] = str(value)

        # 写入CSV文件
        with open(csv_file_path, 'w', encoding='utf-8', newline='') as f:
            # 使用第一个元素的键作为表头
            headers = execution_stats[0].keys() if execution_stats else []
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(execution_stats)

        print(f"转换成功！已生成CSV文件: {csv_file_path}")


    # def execution_to_csv(self,json_data,csv_file_path):
        """
        将JSON文件中的data字段下的executionState数据转换为CSV文件

        参数:
            json_file_path(str):输入的Json文件路径
            csv_file_path(str):输出的CSV文件路径
        """        
        data_str = json_data['data']
        data = json.loads(data_str)

        # 提取executionStats数据
        execution_stats = data.get('executionStats',[])
        if not execution_stats:
            print('警告:未找到executionStats数据,生成的CSV文件可能为空')
            return 

        #处理特殊字段(列表转字符串)
        for item in execution_stats:
            for key,value in item.items():
                if isinstance(value,list):
                    item[key] = str(value)

        # 写入CSV文件
        with open(csv_file_path,'w',encoding='utf-8',newline='')as f:
            #使用第一个元素的键作为表头
            headers = execution_stats[0].keys()
            writer = csv.DictWriter(f,fieldnames=headers)
            writer.writeheader()
            writer.writerows(execution_stats)

        print(f"转换成功！已生成CSV文件: {csv_file_path}")

    def getexecutionid(self,json_data):
        data_str = json_data['data']
        data = json.loads(data_str)
        execution_stats = data.get('executionStats',[])
        execution_ids = [item['id'] for item in execution_stats if 'id' in item]
        return execution_ids

