import csv
import datetime
from collections import defaultdict

class WorkHourTracker:
    def __init__(self, data_file='work_hours.csv'):
        self.data_file = data_file
        self.work_hours = self.load_data()
    
    def load_data(self):
        """从CSV文件加载工时数据"""
        work_hours = []
        try:
            with open(self.data_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # 转换数据类型
                    work_hours.append({
                        'name': row['name'],
                        'date': datetime.datetime.strptime(row['date'], '%Y-%m-%d').date(),
                        'hours': float(row['hours']),
                        'notes': row.get('notes', '')
                    })
            print(f"成功加载 {len(work_hours)} 条工时记录")
        except FileNotFoundError:
            print(f"未找到数据文件 {self.data_file}，将创建新文件")
        except Exception as e:
            print(f"加载数据时出错: {e}")
        return work_hours
    
    def save_data(self):
        """保存工时数据到CSV文件"""
        try:
            with open(self.data_file, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['name', 'date', 'hours', 'notes']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                for entry in self.work_hours:
                    writer.writerow({
                        'name': entry['name'],
                        'date': entry['date'].strftime('%Y-%m-%d'),
                        'hours': entry['hours'],
                        'notes': entry['notes']
                    })
            print(f"成功保存 {len(self.work_hours)} 条工时记录到 {self.data_file}")
        except Exception as e:
            print(f"保存数据时出错: {e}")
    
    def add_work_hour(self, name, date, hours, notes=''):
        """添加新的工时记录"""
        self.work_hours.append({
            'name': name,
            'date': date,
            'hours': hours,
            'notes': notes
        })
        self.save_data()
    
    def get_persons(self):
        """获取所有人员列表"""
        return list(set(entry['name'] for entry in self.work_hours))
    
    def calculate_daily_hours(self, name=None, specific_date=None):
        """计算每日工时"""
        daily = defaultdict(float)
        
        for entry in self.work_hours:
            # 筛选特定人员
            if name and entry['name'] != name:
                continue
            
            # 筛选特定日期
            if specific_date and entry['date'] != specific_date:
                continue
            
            key = (entry['name'], entry['date']) if not name else entry['date']
            daily[key] += entry['hours']
        
        return dict(daily)
    
    def calculate_weekly_hours(self, name=None, specific_year=None, specific_week=None):
        """计算每周工时"""
        weekly = defaultdict(float)
        
        for entry in self.work_hours:
            # 筛选特定人员
            if name and entry['name'] != name:
                continue
            
            # 获取年份和周数
            year, week, _ = entry['date'].isocalendar()
            
            # 筛选特定年份和周
            if specific_year and year != specific_year:
                continue
            if specific_week is not None and week != specific_week:
                continue
            
            key = (entry['name'], year, week) if not name else (year, week)
            weekly[key] += entry['hours']
        
        return dict(weekly)
    
    def calculate_monthly_hours(self, name=None, specific_year=None, specific_month=None):
        """计算每月工时"""
        monthly = defaultdict(float)
        
        for entry in self.work_hours:
            # 筛选特定人员
            if name and entry['name'] != name:
                continue
            
            # 获取年份和月份
            year = entry['date'].year
            month = entry['date'].month
            
            # 筛选特定年份和月份
            if specific_year and year != specific_year:
                continue
            if specific_month and month != specific_month:
                continue
            
            key = (entry['name'], year, month) if not name else (year, month)
            monthly[key] += entry['hours']
        
        return dict(monthly)
    
    def export_to_csv(self, data, filename, headers):
        """将统计数据导出到CSV文件"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                
                for key, hours in data.items():
                    if isinstance(key, tuple):
                        row = list(key) + [hours]
                    else:
                        row = [key, hours]
                    writer.writerow(row)
            
            print(f"数据已成功导出到 {filename}")
        except Exception as e:
            print(f"导出数据时出错: {e}")

def display_menu():
    """显示主菜单"""
    print("\n===== 工时统计系统 =====")
    print("1. 添加工时记录")
    print("2. 统计个人每日工时")
    print("3. 统计个人每周工时")
    print("4. 统计个人每月工时")
    print("5. 统计所有人每日工时")
    print("6. 统计所有人每周工时")
    print("7. 统计所有人每月工时")
    print("8. 退出程序")
    return input("请选择操作 (1-8): ")

def main():
    tracker = WorkHourTracker()
    
    while True:
        choice = display_menu()
        
        if choice == '1':
            # 下载工时信息
            name = input("请输入姓名: ")
            date_str = input("请输入日期 (YYYY-MM-DD): ")
            try:
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                hours = float(input("请输入工时: "))
                notes = input("请输入备注 (可选): ")
                
                tracker.add_work_hour(name, date, hours, notes)
                print("工时记录添加成功!")
            except ValueError:
                print("输入格式错误，请重新尝试")
        
        elif choice in ['2', '3', '4']:
            # 个人统计
            persons = tracker.get_persons()
            if not persons:
                print("没有找到任何工时记录")
                continue
                
            print("现有人员:", ", ".join(persons))
            name = input("请输入要统计的人员姓名: ")
            
            if name not in persons:
                print(f"未找到 {name} 的工时记录")
                continue
            
            if choice == '2':
                # 个人每日统计
                date_str = input("请输入要统计的日期 (YYYY-MM-DD，留空则统计所有日期): ")
                specific_date = None
                if date_str:
                    try:
                        specific_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                    except ValueError:
                        print("日期格式错误，将统计所有日期")
                
                daily_data = tracker.calculate_daily_hours(name, specific_date)
                print(f"\n{name} 的每日工时统计:")
                for date, hours in daily_data.items():
                    print(f"{date}: {hours} 小时")
                
                if input("是否导出为CSV? (y/n): ").lower() == 'y':
                    filename = f"{name}_daily_hours.csv"
                    tracker.export_to_csv(daily_data, filename, ['日期', '工时(小时)'])
            
            elif choice == '3':
                # 个人每周统计
                year_str = input("请输入要统计的年份 (留空则统计所有年份): ")
                week_str = input("请输入要统计的周数 (留空则统计所有周): ")
                
                specific_year = int(year_str) if year_str else None
                specific_week = int(week_str) if week_str else None
                
                weekly_data = tracker.calculate_weekly_hours(name, specific_year, specific_week)
                print(f"\n{name} 的每周工时统计:")
                for (year, week), hours in weekly_data.items():
                    print(f"{year}年 第{week}周: {hours} 小时")
                
                if input("是否导出为CSV? (y/n): ").lower() == 'y':
                    filename = f"{name}_weekly_hours.csv"
                    tracker.export_to_csv(weekly_data, filename, ['年份', '周数', '工时(小时)'])
            
            elif choice == '4':
                # 个人每月统计
                year_str = input("请输入要统计的年份 (留空则统计所有年份): ")
                month_str = input("请输入要统计的月份 (留空则统计所有月份): ")
                
                specific_year = int(year_str) if year_str else None
                specific_month = int(month_str) if month_str else None
                
                monthly_data = tracker.calculate_monthly_hours(name, specific_year, specific_month)
                print(f"\n{name} 的每月工时统计:")
                for (year, month), hours in monthly_data.items():
                    print(f"{year}年 {month}月: {hours} 小时")
                
                if input("是否导出为CSV? (y/n): ").lower() == 'y':
                    filename = f"{name}_monthly_hours.csv"
                    tracker.export_to_csv(monthly_data, filename, ['年份', '月份', '工时(小时)'])
        
        elif choice in ['5', '6', '7']:
            # 所有人统计
            if not tracker.work_hours:
                print("没有找到任何工时记录")
                continue
            
            if choice == '5':
                # 所有人每日统计
                date_str = input("请输入要统计的日期 (YYYY-MM-DD，留空则统计所有日期): ")
                specific_date = None
                if date_str:
                    try:
                        specific_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                    except ValueError:
                        print("日期格式错误，将统计所有日期")
                
                daily_data = tracker.calculate_daily_hours(None, specific_date)
                print("\n所有人的每日工时统计:")
                for (name, date), hours in daily_data.items():
                    print(f"{name} 在 {date}: {hours} 小时")
                
                if input("是否导出为CSV? (y/n): ").lower() == 'y':
                    filename = "all_daily_hours.csv"
                    tracker.export_to_csv(daily_data, filename, ['姓名', '日期', '工时(小时)'])
            
            elif choice == '6':
                # 所有人每周统计
                year_str = input("请输入要统计的年份 (留空则统计所有年份): ")
                week_str = input("请输入要统计的周数 (留空则统计所有周): ")
                
                specific_year = int(year_str) if year_str else None
                specific_week = int(week_str) if week_str else None
                
                weekly_data = tracker.calculate_weekly_hours(None, specific_year, specific_week)
                print("\n所有人的每周工时统计:")
                for (name, year, week), hours in weekly_data.items():
                    print(f"{name} 在 {year}年 第{week}周: {hours} 小时")
                
                if input("是否导出为CSV? (y/n): ").lower() == 'y':
                    filename = "all_weekly_hours.csv"
                    tracker.export_to_csv(weekly_data, filename, ['姓名', '年份', '周数', '工时(小时)'])
            
            elif choice == '7':
                # 所有人每月统计
                year_str = input("请输入要统计的年份 (留空则统计所有年份): ")
                month_str = input("请输入要统计的月份 (留空则统计所有月份): ")
                
                specific_year = int(year_str) if year_str else None
                specific_month = int(month_str) if month_str else None
                
                monthly_data = tracker.calculate_monthly_hours(None, specific_year, specific_month)
                print("\n所有人的每月工时统计:")
                for (name, year, month), hours in monthly_data.items():
                    print(f"{name} 在 {year}年 {month}月: {hours} 小时")
                
                if input("是否导出为CSV? (y/n): ").lower() == 'y':
                    filename = "all_monthly_hours.csv"
                    tracker.export_to_csv(monthly_data, filename, ['姓名', '年份', '月份', '工时(小时)'])
        
        elif choice == '8':
            print("感谢使用工时统计系统，再见!")
            break
        
        else:
            print("无效的选择，请重新输入")

if __name__ == "__main__":
    main()
