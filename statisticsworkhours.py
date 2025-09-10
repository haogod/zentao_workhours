import os
import json
import pandas as pd

def load_name_mapping(config_file):
    """
    加载名称映射配置文件并返回映射字典
    
    参数:
        config_file: 配置文件路径
        
    返回:
        名称映射字典，如果文件加载失败则返回空字典
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(config_file):
            print(f"错误: 配置文件 {config_file} 不存在")
            return {}
            
        # 读取并解析JSON文件
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 返回name_mapping部分，如果不存在则返回空字典
            return config.get('name_mapping', {})
            
    except json.JSONDecodeError:
        print(f"错误: 配置文件 {config_file} 格式不正确，不是有效的JSON")
        return {}
    except Exception as e:
        print(f"加载配置文件时发生错误: {str(e)}")
        return {}

def read_workhours_files(folder_path):
    all_workhours = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if file_path.endswith('.csv'):
            try:
                df = pd.read_csv(file_path)
                all_workhours.append(df)
            except Exception as e:
                print(f"读取文件 {file_path} 时出现错误: {e}")
    return pd.concat(all_workhours, ignore_index=True)

def read_execution_file(folder_path):
    all_executions = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if file_path.endswith('.csv'):
            try:
                df = pd.read_csv(file_path)
                all_executions.append(df)
            except Exception as e:
                print(f"读取文件 {file_path} 时出现错误: {e}")
    return pd.concat(all_executions, ignore_index=True)


def associate_workhours_with_project(workhours_folder_path,execution_foler_path, project_file_path, time_unit, start_date=None, end_date=None, employee_name=None):
    # 读取工时文件
    workhours_df = read_workhours_files(workhours_folder_path)
    workhours_df['date'] = pd.to_datetime(workhours_df['date'])

    # 读取项目文件
    project_df = pd.read_csv(project_file_path)

    # 合并工时和项目数据
    workhours_df = workhours_df.rename(columns={'project': 'project_id'})
    project_df = project_df.rename(columns={'id': 'project_id'})
    merged_df = pd.merge(workhours_df, project_df, on='project_id', how='left', suffixes=('', '_project'))
    merged_df = merged_df.rename(columns={'project': 'project_name'})

    # 读取execution文件
    execution_df = read_execution_file(execution_foler_path)
    merged_df = pd.merge(merged_df, execution_df, left_on='execution', right_on='execution', how='left', suffixes=('', '_execution'))

    # 筛选时间范围
    if start_date and end_date:
        merged_df = merged_df[(merged_df['date'] >= pd.to_datetime(start_date)) & (merged_df['date'] <= pd.to_datetime(end_date))]

    # 筛选员工
    if employee_name:
        merged_df = merged_df[merged_df['account'] == employee_name]

    # 按员工、日期、项目统计工时
    grouped = merged_df.groupby(['account','team','date', 'project_name','name'])['consumed'].sum().reset_index()

    # 获取中文名称映射
    name_map = load_name_mapping(
        r"F:\code\zendao\data\config\map_name.json"
    )
    # 构建结果
    associated_data = []
    for index, row in grouped.iterrows():
        chinaname= name_map.get(row['account'], row['account'])  # 获取映射名称，默认使用原名称
        entry = {
            '部门':row['team'],
            '姓名': chinaname,
            '日期': row['date'].strftime('%Y-%m-%d'),
            '项目名称': row['project_name'],
            '任务名称':row['name'],
            '工时(h)': row['consumed']
        }
        associated_data.append(entry)

    result_df = pd.DataFrame(associated_data)
    return result_df


if __name__ == "__main__":
    workhours_folder_path = r"F:\code\zendao\recordworkhours"
    execution_foler_path = r"F:\code\zendao\execution"
    project_file_path =  "F:\code\zendao\zentao_project.csv"

    while True:
        print("\n请选择操作：")
        print("1. 按天统计工时")
        print("2. 按周统计工时")
        print("3. 按月统计工时")
        print("4. 退出")

        choice = input("请输入选项数字: ")

        if choice == '1':
            time_unit = 'day'
        elif choice == '2':
            time_unit = 'week'
        elif choice == '3':
            time_unit ='month'
        elif choice == '4':
            print("感谢使用，再见！")
            break
        else:
            print("无效的选项，请重新输入。")
            continue

        start_date = input("请输入开始日期（格式：YYYY-MM-DD）：")
        end_date = input("请输入结束日期（格式：YYYY-MM-DD）：")
        employee_name = input("请输入员工姓名（留空表示统计所有员工）：")

        result_df = associate_workhours_with_project(
            workhours_folder_path, execution_foler_path,project_file_path, time_unit, start_date, end_date, employee_name)

        file_name = f'{time_unit}_statistics'
        if employee_name:
            file_name += f'_{employee_name}'
        file_name += f'_{start_date}_{end_date}.csv'

        result_df.to_csv(file_name, index=False)
        print(f'统计结果已保存到 {file_name}')