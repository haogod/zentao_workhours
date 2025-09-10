
import json
import csv
import os

class projectcsv:
    def __init__(self):
        print("init projectcsv")
  
    def getprojectid(self,json_data):
         # 提取项目核心数据(projectStats列表)
        project_stats = json_data.get('data',{})
        # 处理嵌套的JSON字符串(若存在)
        project_ids = []
        if isinstance(project_stats,str):
            project_stats = json.loads(project_stats)
        projects = project_stats.get('projectStats',{})
        for proj in projects:
            project_ids.append(proj.get('id',''))
        return project_ids

    def translatecsv(self,json_data,csv_file_path):
         # 提取项目核心数据(projectStats列表)
        project_stats = json_data.get('data',{})
        # 处理嵌套的JSON字符串(若存在)
        if isinstance(project_stats,str):
            project_stats = json.loads(project_stats)
        projects = project_stats.get('projectStats',{})
        # 提取用户影射表
        users = project_stats.get('users',{})

        #--------------------------------
        # 步骤2：定义CSV字段表头
        #--------------------------------   
        csv_headers = [
            'id', 
            'project',
            # 'charter',
            # 'model',
            # 'type',
            # 'category',
            # 'lifetime',
            # 'budget',
            # 'budgetUnit',
            # 'attribute',
            # 'percent',
            # 'milestone',
            # 'output',
            # 'auth',
            # 'storyType',
            'parent', 
            # 'path',
            # 'grade', 
            # 'name',
            # 'code',
            # 'hasProduct', 
            'begin',
            'end', 
            'firstEnd', 
            'realBegan',
            'realEnd',
            'days',
            'status',
            'subStatus',
            'pri',
            #'desc',
            'version',
            # 'parentVersion',
            # 'planDuration',
            # 'realDuration',
            'progress',
            'estimate',
            'left',
            'consumed',
            'teamCount',
            # 'market', 
            # 'openedBy',
            # 'openedDate',
            # 'openedVersion',
            # 'lastEditedBy', 
            # 'lastEditedDate',
            # 'closedBy',
            # 'closedDate', 
            # 'closedReason', 
            # 'canceledBy', 
            # 'canceledDate',
            # 'suspendedDate', 
            # 'PO', 
            # 'PM',
            # 'QD',
            # 'RD',
             'team',
            # 'acl',
            # 'whitelist',
            # 'order',
            # 'vision',
            # 'stageBy',
            # 'displayCards',
            # 'fluidBoard',
            # 'multiple',
            # 'parallel',
             'enabled',
            # 'colWidth',
            # 'minColWidth',
            # 'maxColWidth',
            # 'deleted',
            'teamMembers',
            # 'leftTasks',
            # 'statusTitle',
            # 'consume',
            # 'surplus',
            # 'invested',
            # 'storyCount',
            # 'storyPoints',
            # 'executionCount',
            # 'from',
            # 'actions',
            # 'PMAvatar',
            # 'PMUserID'
        ]

        #--------------------------------
        # 步骤3：处理每个项目数据，适配CSV格式
        #-------------------------------- 
        csv_rows = []
        for proj in projects:
            # 处理用户信息格式
            def get_user_json(user_account):
                if not user_account:
                      return json.dumps({'id': 1, 'account': '', 'avatar': '', 'realname': ''}, ensure_ascii=False)
                realname = users.get(user_account,user_account)
                return json.dumps({
                    'id':1, #目标CSV中用户ID统一为1（参考示例格式）
                    'account':user_account,
                    'avatar':'',
                    'realname':realname
                },ensure_ascii=False)
            # 处理时间格式
            def format_date(date_str,default=''):
                if not date_str:
                    return default
                if date_str == '长期':
                    return '长期'
                return date_str.replace('-', '/').lstrip('0').replace('/0', '/')

            # 构建CSV行数据
            row = {
                'id': proj.get('id',''),  # 使用项目id
                'project': proj.get('name', ''),
                #'charter': get_user_json(proj.get('openedBy', '')),  # 创建人信息
                #'model': get_user_json(proj.get('lastEditedBy', '')),  # 最后编辑人信息
                #'type': get_user_json(proj.get('closedBy', '')),  # 关闭人信息（无则空）
                #'category': proj.get('name', ''),  # 分类复用项目名称
                #'lifetime': '—',  # 目标CSV中lifetime统一为"—"
                #'budget': proj.get('budget', '待定'),
                #'budgetUnit': proj.get('budgetUnit', 'CNY'),
                #'attribute': proj.get('attribute', ''),
                #'percent': proj.get('percent', 0),
                #'milestone': proj.get('milestone', 0),
                #'output': proj.get('output', ''),
                #'auth': proj.get('auth', 'extend'),
                #'storyType': proj.get('storyType', 'story'),
                'parent': proj.get('parent', 0),
                #'path': proj.get('path', ''),
                #'grade': proj.get('grade', 2),
                #'name': proj.get('name', ''),
                #'code': proj.get('code', ''),
                #'hasProduct': proj.get('hasProduct', 0),
                'begin': format_date(proj.get('begin')),
                'end': format_date(proj.get('end'), '长期'),  # 无结束时间则为"长期"
                'firstEnd': format_date(proj.get('firstEnd'), '2059/12/31'),  # 默认结束时间
                'realBegan': format_date(proj.get('realBegan')),
                'realEnd': format_date(proj.get('realEnd')),
                'days': proj.get('days', 0),
                'status': proj.get('status', 'doing'),
                'subStatus': proj.get('subStatus', ''),
                'pri': proj.get('pri', 1),
                #'desc': proj.get('desc', ''),
                'version': proj.get('version', 0),
                #'parentVersion': proj.get('parentVersion', 0),
                #'planDuration': proj.get('planDuration', 0),
                #'realDuration': proj.get('realDuration', 0),
                'progress': proj.get('progress', 0.0),
                'estimate': f"{proj.get('estimate', 0)}h" if proj.get('estimate') else '0h',  # 工时带单位
                'left': proj.get('left', 0.0),
                'consumed': proj.get('consumed', 0.0),
                'teamCount': proj.get('teamCount', 0),
                #'market': proj.get('market', 0),
                #'openedBy': proj.get('openedBy', ''),
                #'openedDate': f"{proj.get('openedDate', '').replace(' ', 'T')}Z" if proj.get('openedDate') else '',  # UTC格式
                #'openedVersion': proj.get('openedVersion', ''),
                #'lastEditedBy': proj.get('lastEditedBy', ''),
                #'lastEditedDate': f"{proj.get('lastEditedDate', '').replace(' ', 'T')}Z" if proj.get('lastEditedDate') else '',
                #'closedBy': proj.get('closedBy', ''),
                #'closedDate': f"{proj.get('closedDate', '').replace(' ', 'T')}Z" if proj.get('closedDate') else '',
                #'closedReason': proj.get('closedReason', ''),
                #'canceledBy': proj.get('canceledBy', ''),
                #'canceledDate': proj.get('canceledDate', ''),
                #'suspendedDate': format_date(proj.get('suspendedDate')),
                #'PO': proj.get('PO', ''),
                #'PM': proj.get('PM', ''),
                #'QD': proj.get('QD', ''),
                #'RD': proj.get('RD', ''),
                'team': proj.get('team', ''),
                #'acl': proj.get('acl', 'open'),
                #'whitelist': json.dumps(proj.get('whitelist', []), ensure_ascii=False),  # 白名单JSON数组
                #'order': proj.get('order', 0),
                #'vision': proj.get('vision', 'rnd'),
                #'stageBy': proj.get('stageBy', 'project'),
                #'displayCards': proj.get('displayCards', 0),
                #'fluidBoard': proj.get('fluidBoard', 0),
                #'multiple': proj.get('multiple', 1),
                #'parallel': proj.get('parallel', 0),
                'enabled': proj.get('enabled', 'on'),
                #'colWidth': proj.get('colWidth', 264),
                #'minColWidth': proj.get('minColWidth', 200),
                #'maxColWidth': proj.get('maxColWidth', 384),
                #'deleted': 'FALSE' if proj.get('deleted', '0') == '0' else 'TRUE',  # 布尔值格式
                'teamMembers': json.dumps(proj.get('teamMembers', []), ensure_ascii=False),  # 团队成员JSON数组
                #'leftTasks': proj.get('leftTasks', '—'),
                #'statusTitle': proj.get('statusTitle', '进行中'),
                #'consume': f"{proj.get('consumed', 0)}h" if proj.get('consumed') else '0h',
                #'surplus': f"{proj.get('left', 0)}h" if proj.get('left') else '0h',
                #'invested': proj.get('invested', 0.0),
                #'storyCount': proj.get('storyCount', 0),
                #'storyPoints': f"{proj.get('storyPoints', '0')} h",
                #'executionCount': proj.get('executionCount', 0),
                #'from': proj.get('from', 'project'),
                #'actions': json.dumps(proj.get('actions', []), ensure_ascii=False),  # 操作列表JSON数组
                #'PMAvatar': proj.get('PMAvatar', ''),
                #'PMUserID': proj.get('PMUserID', '')
            }
            csv_rows.append(row)


        #--------------------------------
        # 步骤4：写入CSV文件
        #-------------------------------- 
        try:
            with open(csv_file_path,'w',newline='',encoding='utf-8-sig')as f:
                writer = csv.DictWriter(f,fieldnames=csv_headers,delimiter=',')
                #写入表头和数据
                writer.writeheader() #写入表头
                writer.writerows(csv_rows) #写入数据
            print(f"转换完成！CSV文件已保存至：{csv_file_path}")
        except PermissionError:
            print(f"错误:无权限写入CSV文件,请检查路径是否可写:{csv_file_path}")
        except Exception as e:
            print(f"写入CSV时发生未知错误:{str(e)}")
    def create_project_files(self,folder_name):
        try:
            # 创建projects文件夹,如果不存在
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
                print(f"已创建文件夹: {folder_name}")
            else:
                print(f"文件夹 {folder_name} 已存在")
        
              # 在文件夹中创建系列文件
            num_files = 100  # 创建100个文件
            for i in range(1, num_files + 1):
                file_name = f"project{i}"
                file_path = os.path.join(folder_name, file_name)
            
            # 创建文件（如果不存在）
                if not os.path.exists(file_path):
                    with open(file_path, 'w') as f:
                    # 可以在文件中写入一些内容，这里仅创建空文件
                        pass
                    print(f"已创建文件: {file_path}")
                else:
                    print(f"文件 {file_path} 已存在，跳过创建")
                
        except Exception as e:
            print(f"操作过程中发生错误: {str(e)}")
    # end def