#作者：Adaihappyjan
#版本号：0.2.82
#更新内容：增加了运行速率显示、优化了运行速度，增加了大量注释以便于用户修改代码
#创建时间：2023年5月8日
#最后修改时间：2023年6月5日
#说明：该代码是一个Fandom社区管理工具，用于检查Fandom社区（wiki）页面中的恶意内容。主要功能包括从指定数量的新wiki中查找包含指定关键词的页面，并将结果保存到文件中。用户可以选择关键词选项和要检查的wiki数量，并可以实时查看处理进度和运行速率。
#是否为公共版：是
#Github地址：https://github.com/adaihappyjan/Fandom_Tool
#注释地狱警告

#导入库
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin
from concurrent.futures import as_completed, ThreadPoolExecutor

session = requests.Session()# 创建会话
headers = {# 设置请求头，防止被Fandom阻止，如果被阻止，可以尝试修改请求头
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
}
session.headers.update(headers)# 更新会话的请求头
def find_bureaucrats(wiki_url):# 获取行政员信息
    api_url = f"{wiki_url}/api.php?action=query&list=allusers&augroup=bureaucrat&format=json"# 构造API请求链接
    response = session.get(api_url)# 发送请求

    bureaucrats = []# 用于存储行政员信息
    if response.status_code == 200:# 如果请求成功
        try:
            data = json.loads(response.text)# 尝试解析JSON数据
            for user in data['query']['allusers']:
                bureaucrat_url = f"{wiki_url}/wiki/User:{user['name']}"# 构造行政员页面链接
                bureaucrats.append((bureaucrat_url, user['name']))# 将行政员信息添加到列表中
        except json.JSONDecodeError:# 如果解析JSON数据失败
            print(f"Could not parse JSON data from {api_url}")# 输出错误信息
    else:
        print(f"Failed to request {api_url}, status code: {response.status_code}")# 输出错误信息

    return bureaucrats# 返回行政员信息列表
def process_single_wiki(base_url, li, keywords, progressbar):# 处理单个wiki
    a = li.find('a')# 找到a元素
    if a:
        wiki_name = a.text# 获取wiki名称
        wiki_url = urljoin(base_url, a['href'])# 获取wiki链接
        if wiki_url.startswith(base_url) or wiki_url.startswith('https://about.fandom.com') or wiki_url.startswith('https://support.fandom.com') or wiki_url.startswith('https://soap.fandom.com') or wiki_url.startswith('https://www.fandom.com') or wiki_url.startswith('https://community.fandom.com') or wiki_url.startswith('https://www.twitter.com') or wiki_url.startswith('https://www.futhead.com') or wiki_url.startswith('https://www.muthead.com') or wiki_url.startswith('https://www.fanatical.com'):# 如果链接是Fandom官方的链接或者是子域名
            return None# 返回空值

        response = session.get(wiki_url)# 发送请求
        soup = BeautifulSoup(response.text, 'lxml')# 解析HTML

        text = soup.get_text()# 获取页面文本
        total_characters = len(text)# 获取文本长度

        keyword_characters = 0# 用于存储关键词字符数
        for keyword in keywords:
            occurrences = text.count(keyword)# 计算关键词出现次数
            keyword_characters += len(keyword) * occurrences# 计算关键词字符数

        if keyword_characters > 0:
            malicious_probability = keyword_characters / total_characters * 100 # 计算恶意概率
            trigger_value = round(malicious_probability, 1) * 10  # 计算恶意值
            bureaucrats = find_bureaucrats(wiki_url)# 获取行政员信息
            for bureaucrat_url, bureaucrat_name in bureaucrats:# 遍历行政员信息
                return (wiki_name, wiki_url, bureaucrat_name, bureaucrat_url, trigger_value)  # 返回触发值

def process_wikis(base_url, limit, keywords, progressbar, result_file, speed_label):# 处理wiki
    url = f"{base_url}/wiki/Special:NewWikis?start=&language=zh&hub=0&limit={limit}"# 构造请求链接
    response = session.get(url)# 发送请求
    soup = BeautifulSoup(response.text, 'lxml')# 解析HTML

    li_elements = soup.find_all('li')# 找到所有的li元素
    if len(li_elements) == 0:# 如果没有找到任何li元素，说明没有新的wiki
        messagebox.showinfo("错误", "无法找到任何新的wiki，可能是网络问题或被请求阻止。")# 弹出错误提示框
        return

    wikis = []# 用于存储wiki信息
    start_time = time.time()  # 记录开始时间
    with ThreadPoolExecutor(max_workers=70) as executor:# 创建线程池
        futures = [executor.submit(process_single_wiki, base_url, li, keywords, progressbar) for li in li_elements]# 提交任务

        for i, future in enumerate(as_completed(futures)):#
            try:
                wiki = future.result()# 获取结果
                if wiki:
                    wikis.append(wiki)# 将结果添加到列表中
            except Exception as e:
                print(f"访问出现问题 {e}")# 输出错误信息

            progressbar['value'] = (i + 1) / len(li_elements) * 100# 更新进度条
            progressbar.update()# 更新进度条
            
            elapsed_time = time.time() - start_time  # 计算消耗的时间
            speed = (i + 1) / elapsed_time  # 计算运行速率（每秒处理的网页数量）
            speed_label.config(text=f"运行速率: {speed:.2f} 页/秒")  # 更新速率显示
            speed_label.update()# 更新速率显示

    wikis.sort(key=lambda x: x[4], reverse=True)# 按照触发值排序

    for wiki in wikis:
        result_file.write(f"wiki名称: {wiki[0]}, wiki链接: {wiki[1]}, 行政员昵称: {wiki[2]}, 行政员链接: {wiki[3]}, 触发值: {wiki[4]}%\n") # 将结果写入文件
        result_file.write('-' * 50 + '\n')# 分割线

    messagebox.showinfo("完成", "运行完毕！")# 弹出完成提示框

def main():# 主函数
    base_url = 'https://community.fandom.com'

    def get_keywords():# 获取关键词
        keyword_choice = simpledialog.askstring("选择关键词选项", "请输入一个数字：\n1: 后室关键词\n2: 政治关键词\n3: 从文件导入关键词")# 弹出输入框
        if keyword_choice == "1":
            return ["后室", "Backrooms", "backrooms", "adaihappyjan", "backroom", "小草", "室"]
        elif keyword_choice == "2":
            return ["政治", "习近平", "习", "毛泽东", "毛", "中国", "中华人民共和国", "打倒", "党", "共产党", "国民党", "台湾", "独立", "民主", "独裁", "言论自由", "新闻自由", "人权", "抗议", "集会", "示威", "政变", "革命", "改革", "制宪", "宪法", "选举", "总统", "首相", "立法", "政府", "军队", "军事", "战争", "和平", "贪腐", "清廉", "廉政", "法治", "权力", "权威", "独裁", "专制", "民主制", "共和制", "君主制", "社会主义", "资本主义", "共产主义", "网络审查", "敏感词", "禁言", "屏蔽", "颠覆", "封锁", "谣言", "反动", "维稳", "六四", "天安门", "达赖喇嘛", "维吾尔", "藏独", "疆独", "自由疆", "自由藏", "法轮功", "珍惜草", "真相", "翻墙", "VPN", "洋葱路由", "TOR", "封控", "审查制度"]
        elif keyword_choice == "3":
            file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])# 弹出文件选择框
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as file:# 读取文件
                    return file.read().split()
            else:
                messagebox.showinfo("错误", "无效的文件路径")# 弹出错误提示框
                return None
        else:
            messagebox.showinfo("错误", "无效的选项")# 弹出错误提示框
            return None

    def get_limit():# 获取wiki数量限制
        limit_choice = simpledialog.askinteger("选择wiki数量", "请输入需要检查的wiki数量（例如：50，100，500）")# 弹出输入框
        return limit_choice if limit_choice is not None else None# 如果输入框为空，返回空值

    def run_process():# 运行程序

        keywords = get_keywords()#
        if keywords is None:# 如果关键词为空
            return

        limit = get_limit()
        if limit is None:# 如果wiki数量限制为空
            return

        # 获取当前脚本的绝对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # 在脚本路径下创建结果文件
        result_file_path = os.path.join(script_dir, '结果.txt')

        with open(result_file_path, 'w', encoding='utf-8') as result_file:
            process_wikis(base_url, limit, keywords, progressbar, result_file, speed_label)  # 在这里加入 speed_label
# GUI
    root = tk.Tk()
    root.geometry("500x500")
    root.title("SOAP Tool")

    msg = tk.Message(root, text="SOAP Tool，Fandom社区管理工具", width=480)
    msg.config(bg='lightgreen', font=('times', 20, 'italic'))
    msg.pack()

    button = tk.Button(root, text="开始检查wiki", command=run_process)
    button.pack()

    progressbar = ttk.Progressbar(root, length=200, mode='determinate')
    progressbar.pack(pady=10)

    speed_label = tk.Label(root, text="运行速度: 0.00 页/秒")  # 定义速率显示标签
    speed_label.pack()

    credits = tk.Label(root, text="Made by Adaihappyjan   Powered by NLBstudio")
    credits.pack(side='bottom', anchor='w') 

    root.mainloop()

if __name__ == "__main__":
    main()
