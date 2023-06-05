#作者：Adaihappyjan
#版本号：0.2.82
#更新内容：增加了运行速率显示、优化了运行速度，增加了大量注释以便于用户修改代码
#创建时间：2023年5月8日
#最后修改时间：2023年6月5日
#说明：该代码是一个Fandom社区管理工具，用于检查Fandom社区（wiki）页面中的恶意内容。主要功能包括从指定数量的新wiki中查找包含指定关键词的页面，并将结果保存到文件中。用户可以选择关键词选项和要检查的wiki数量，并可以实时查看处理进度和运行速率。
#是否为公共版：是
#Github地址：https://github.com/adaihappyjan/Fandom_Tool

import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin
from concurrent.futures import as_completed, ThreadPoolExecutor

session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
}
session.headers.update(headers)
def find_bureaucrats(wiki_url):
    api_url = f"{wiki_url}/api.php?action=query&list=allusers&augroup=bureaucrat&format=json"
    response = session.get(api_url)

    bureaucrats = []
    if response.status_code == 200:
        try:
            data = json.loads(response.text)
            for user in data['query']['allusers']:
                bureaucrat_url = f"{wiki_url}/wiki/User:{user['name']}"
                bureaucrats.append((bureaucrat_url, user['name']))
        except json.JSONDecodeError:
            print(f"Could not parse JSON data from {api_url}")
    else:
        print(f"Failed to request {api_url}, status code: {response.status_code}")

    return bureaucrats
def process_single_wiki(base_url, li, keywords, progressbar):
    a = li.find('a')
    if a:
        wiki_name = a.text
        wiki_url = urljoin(base_url, a['href'])
        if wiki_url.startswith(base_url) or wiki_url.startswith('https://about.fandom.com') or wiki_url.startswith('https://support.fandom.com') or wiki_url.startswith('https://soap.fandom.com') or wiki_url.startswith('https://www.fandom.com') or wiki_url.startswith('https://community.fandom.com') or wiki_url.startswith('https://www.twitter.com') or wiki_url.startswith('https://www.futhead.com') or wiki_url.startswith('https://www.muthead.com') or wiki_url.startswith('https://www.fanatical.com'):
            return None

        response = session.get(wiki_url)
        soup = BeautifulSoup(response.text, 'lxml')

        text = soup.get_text()
        total_characters = len(text)

        keyword_characters = 0
        for keyword in keywords:
            occurrences = text.count(keyword)
            keyword_characters += len(keyword) * occurrences

        if keyword_characters > 0:
            malicious_probability = keyword_characters / total_characters * 100
            trigger_value = round(malicious_probability, 1) * 10  # 按你的要求进行了修改
            bureaucrats = find_bureaucrats(wiki_url)# 获取行政员信息
            for bureaucrat_url, bureaucrat_name in bureaucrats:# 遍历行政员信息
                return (wiki_name, wiki_url, bureaucrat_name, bureaucrat_url, trigger_value)  # 返回触发值

def process_wikis(base_url, limit, keywords, progressbar, result_file, speed_label):
    url = f"{base_url}/wiki/Special:NewWikis?start=&language=zh&hub=0&limit={limit}"
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    li_elements = soup.find_all('li')# 找到所有的li元素
    if len(li_elements) == 0:# 如果没有找到任何li元素，说明没有新的wiki
        messagebox.showinfo("错误", "无法找到任何新的wiki，可能是网络问题或被请求阻止。")
        return

    wikis = []
    start_time = time.time()  # 记录开始时间
    with ThreadPoolExecutor(max_workers=70) as executor:
        futures = [executor.submit(process_single_wiki, base_url, li, keywords, progressbar) for li in li_elements]

        for i, future in enumerate(as_completed(futures)):
            try:
                wiki = future.result()
                if wiki:
                    wikis.append(wiki)
            except Exception as e:
                print(f"访问出现问题 {e}")

            progressbar['value'] = (i + 1) / len(li_elements) * 100
            progressbar.update()
            
            elapsed_time = time.time() - start_time  # 计算消耗的时间
            speed = (i + 1) / elapsed_time  # 计算运行速率（每秒处理的网页数量）
            speed_label.config(text=f"运行速率: {speed:.2f} 页/秒")  # 更新速率显示
            speed_label.update()

    wikis.sort(key=lambda x: x[4], reverse=True)

    for wiki in wikis:
        result_file.write(f"wiki名称: {wiki[0]}, wiki链接: {wiki[1]}, 行政员昵称: {wiki[2]}, 行政员链接: {wiki[3]}, 触发值: {wiki[4]}%\n")  # 恶意值已经被更名为触发值
        result_file.write('-' * 50 + '\n')

    messagebox.showinfo("完成", "运行完毕！")

def main():
    base_url = 'https://community.fandom.com'

    def get_keywords():
        """
        获取用户选择的关键词选项，并返回关键词列表。
        """
        keyword_choice = simpledialog.askstring("选择关键词选项", "请输入一个数字：\n1: 后室关键词\n2: 政治关键词\n3: 从文件导入关键词")
        if keyword_choice == "1":
            return ["后室", "Backrooms", "backrooms", "adaihappyjan", "backroom", "小草", "室"]
        elif keyword_choice == "2":
            return ["政治", "习近平", "习", "毛泽东", "毛", "中国", "中华人民共和国", "打倒", "党", "共产党", "国民党", "台湾", "独立", "民主", "独裁", "言论自由", "新闻自由", "人权", "抗议", "集会", "示威", "政变", "革命", "改革", "制宪", "宪法", "选举", "总统", "首相", "立法", "政府", "军队", "军事", "战争", "和平", "贪腐", "清廉", "廉政", "法治", "权力", "权威", "独裁", "专制", "民主制", "共和制", "君主制", "社会主义", "资本主义", "共产主义", "网络审查", "敏感词", "禁言", "屏蔽", "颠覆", "封锁", "谣言", "反动", "维稳", "六四", "天安门", "达赖喇嘛", "维吾尔", "藏独", "疆独", "自由疆", "自由藏", "法轮功", "珍惜草", "真相", "翻墙", "VPN", "洋葱路由", "TOR", "封控", "审查制度"]
        elif keyword_choice == "3":
            file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read().split()
            else:
                messagebox.showinfo("错误", "无效的文件路径")
                return None
        else:
            messagebox.showinfo("错误", "无效的选项")
            return None

    def get_limit():
        """
        获取用户选择的wiki数量限制，并返回选择的数量。
        """
        limit_choice = simpledialog.askinteger("选择wiki数量", "请输入需要检查的wiki数量（例如：50，100，500）")
        return limit_choice if limit_choice is not None else None

    def run_process():
        """
        运行处理函数，开始检查wiki页面。
        """
        keywords = get_keywords()
        if keywords is None:
            return

        limit = get_limit()
        if limit is None:
            return

        # 获取当前脚本的绝对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # 在脚本路径下创建结果文件
        result_file_path = os.path.join(script_dir, '结果.txt')

        with open(result_file_path, 'w', encoding='utf-8') as result_file:
            process_wikis(base_url, limit, keywords, progressbar, result_file, speed_label)  # 在这里加入 speed_label

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