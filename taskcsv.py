import json
import csv
import os
from json import JSONDecodeError


class taskcsv:
    def gettaskid(self,json_data):
        data_str = json_data['data']
        data = json.loads(data_str)
        tasks_info = data.get('tasks', {})
        task_ids = [item['id'] for item in tasks_info.values() if 'id' in item]
        return task_ids 
    

    def json_to_csv(self,json_data,csv_file_path):
        try:
            # 解析外层JSON
            outer_data = json.loads(json_data)
            if outer_data.get('status') != 'success':
                print("数据状态异常")
                return

            # 解析内层data字段（注意：内层data是字符串形式的JSON）
            try:
                inner_data = json.loads(outer_data['data'])
            except JSONDecodeError:
                print("内层数据解析失败")
                return

            #0. 生成tasks信息
            tasks_info = inner_data.get('tasks', {})
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                fields = ['id', 'project', 'parent', 'name', 'consumed', 'left']
                writer.writerow(fields)
                for member in tasks_info.values():
                    row = [
                        member.get('id', ''),
                        member.get('project', ''),
                        member.get('parent', ''),
                        member.get('name', ''),
                        member.get('consumed', ''),
                        member.get('left', '')
                    ]
                    writer.writerow(row)

            # 1. 生成执行信息CSV
            # execution_info = inner_data.get('execution', {})
            # with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
            #     writer = csv.writer(f)
            #     # 提取关键字段
            #     fields = ['id', 'project', 'name', 'status', 'begin', 'end', 
            #               'realBegan', 'PM', 'totalHours', 'totalEstimate', 
            #               'totalConsumed', 'totalLeft']
            #     writer.writerow(fields)
            #     row = [execution_info.get(field, '') for field in fields]
            #     writer.writerow(row)

            # # 2. 生成团队成员CSV
            # team_members = inner_data.get('teamMembers', {})
            # with open('team_members.csv', 'w', newline='', encoding='utf-8') as f:
            #     writer = csv.writer(f)
            #     fields = ['account', 'realname', 'role', 'joinDate', 'totalHours', 'userID']
            #     writer.writerow(fields)
            #     for member in team_members.values():
            #         row = [
            #             member.get('account', ''),
            #             member.get('realname', ''),
            #             member.get('role', ''),
            #             member.get('join', ''),
            #             member.get('totalHours', ''),
            #             member.get('userID', '')
            #         ]
            #         writer.writerow(row)

            # # 3. 生成操作记录CSV
            # actions = inner_data.get('actions', {})
            # with open('actions.csv', 'w', newline='', encoding='utf-8') as f:
            #     writer = csv.writer(f)
            #     fields = ['id', 'actor', 'action', 'date', 'objectType', 'objectID']
            #     writer.writerow(fields)
            #     for action in actions.values():
            #         row = [
            #             action.get('id', ''),
            #             action.get('actor', ''),
            #             action.get('action', ''),
            #             action.get('date', ''),
            #             action.get('objectType', ''),
            #             action.get('objectID', '')
            #         ]
            #         writer.writerow(row)

            # print("CSV文件生成成功\n")

        except Exception as e:
            print(f"转换失败：{str(e)}")

    # 记录工时
    def extract_recordworkhour_fields(self,json_data):
 
        # 解析嵌套的data字段（原数据中data是字符串格式的JSON）
        task_data = json.loads(json_data['data'])
        actions = task_data.get('actions', {})

        # 筛选出action为recordworkhour的记录
        recordworkhour_list = []
        for action_id, action_info in actions.items():
            if action_info.get('action') == 'recordworkhour':
                # 提取关键字段
                record = {
                    'id': action_info.get('id'),
                    'objectType': action_info.get('objectType'),
                    'objectID': action_info.get('objectID'),
                    'project': action_info.get('project'),
                    'execution': action_info.get('execution'),
                    'actor': action_info.get('actor'),
                    'date': action_info.get('date'),
                    'comment': action_info.get('comment'),
                    'recorded_hours': action_info.get('extra'),  # 本次记录的工时
                    'history': action_info.get('history')       # 工时变更历史
                }
                recordworkhour_list.append(record)
        
        return recordworkhour_list
    # 写入文件 
    def export_to_csv_by_task(self,records, task_id, folder_name="workhour"):
        
        if not records:
            print(f"task_id {task_id} 没有可导出的工时记录数据")
            return
    
        # 创建workhour文件夹（如果不存在）
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            # print(f"已创建文件夹: {folder_name}")
        
        # 构建文件名和完整路径（以task_id命名）
        filename = f"{task_id}.csv"
        file_path = os.path.join(folder_name, filename)
        
        # 定义CSV表头
        fieldnames = [
            'id', 'objectType', 'objectID', 'project', 'execution',
            'actor', 'date', 'comment', 'recorded_hours', 'history'
        ]
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for record in records:
                    writer.writerow(record)
            
            print(f"task_id {task_id} 的工时记录已导出到: {file_path}")
        
        except Exception as e:
            print(f"导出task_id {task_id} 的CSV时发生错误: {str(e)}")
    
        # 编辑工时
    def extract_editeffort_fields(self,json_data):
        # 解析嵌套的data字段
        task_data = json.loads(json_data['data'])
        actions = task_data.get('actions', {})
        # 筛选editeffort操作记录
        editeffort_list = []
        for action_info in actions.values():
            if action_info.get('action') == 'editeffort':
                record = {
                    'id': action_info.get('id'),
                    'objectType': action_info.get('objectType'),
                    'objectID': action_info.get('objectID'),
                    'project': action_info.get('project'),
                    'execution': action_info.get('execution'),
                    'actor': action_info.get('actor'),
                    'date': action_info.get('date'),
                    'comment': action_info.get('comment'),
                    'history': action_info.get('history')  # 工时修改历史
                }
                editeffort_list.append(record)
        return editeffort_list
    
    def export_editeffort_to_csv(self,records, folder_name="effort_workhour"):
        """将编辑工时记录导出到指定文件夹，以task_id命名文件"""
        if not records:
            print("没有可导出的编辑工时记录")
            return

        # 创建文件夹（如果不存在）
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"已创建文件夹: {folder_name}")

        # 按objectID（即task_id）分组
        task_records = {}
        for record in records:
            task_id = record.get('objectID')
            if task_id not in task_records:
                task_records[task_id] = []
            task_records[task_id].append(record)

        # 定义CSV表头
        fieldnames = ['id', 'objectType', 'objectID', 'project', 'execution',
                     'actor', 'date', 'comment', 'history']

        # 为每个task_id创建一个CSV文件
        for task_id, task_data in task_records.items():
            filename = f"task_{task_id}.csv"
            file_path = os.path.join(folder_name, filename)

            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for record in task_data:
                        writer.writerow(record)

                print(f"已导出 {len(task_data)} 条记录到: {file_path}")

            except Exception as e:
                print(f"导出task_id {task_id} 时发生错误: {str(e)}")
    def export_efforts_to_csv(self,json_data):
            # 解析嵌套的data字段
            inner_data = json.loads(json_data['data'])
            efforts = inner_data.get('efforts', [])
            if not efforts:
            # 如果没有efforts数据，尝试从inner_data中获取任务ID
                task_id = inner_data.get('task', {}).get('id', None)
                if task_id:
                    print(f"任务 {task_id} 未填报工时")
                else:
                    print("未找到任务ID，且未填报工时")
                return
            # 获取task_id（从efforts的第一条数据中提取，确保所有数据属于同一task）
            task_id = efforts[0]['objectID']
            if not task_id:
                print("无法获取task_id")
                return

            # 创建recordworkhours文件夹（如果不存在）
            output_dir = 'recordworkhours'
            os.makedirs(output_dir, exist_ok=True)

            # 定义CSV文件名和路径
            csv_file_name = f"{task_id}.csv"
            csv_file_path = os.path.join(output_dir, csv_file_name)

            # 获取efforts的字段名（从第一条数据中提取）
            if efforts:
                fieldnames = efforts[0].keys()
            else:
                fieldnames = []

            # 写入CSV文件
            with open(csv_file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for effort in efforts:
                    writer.writerow(effort)

            print(f"数据已成功导出到: {csv_file_path}")

