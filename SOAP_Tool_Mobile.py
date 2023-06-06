import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
}

def print_header(text):
    print("\n" + "#" * 50)
    print(text.center(50))
    print("#" * 50 + "\n")

def find_bureaucrats(wiki_url):
    api_url = f"{wiki_url}/api.php?action=query&list=allusers&augroup=bureaucrat&format=json"
    response = requests.get(api_url, headers=headers)

    bureaucrats = []
    if response.status_code == 200:  # 确保响应有效
        try:
            data = json.loads(response.text)
            for user in data['query']['allusers']:
                bureaucrat_url = f"{wiki_url}/wiki/User:{user['name']}"
                bureaucrats.append((bureaucrat_url, user['name']))
        except json.JSONDecodeError:  # 捕获解析错误
            print(f"无法解析来自 {api_url} 的 JSON 数据")
    else:
        print(f"请求 {api_url} 失败，状态码：{response.status_code}")

    return bureaucrats

def process_wikis(base_url, limit, keywords):
    print_header("开始处理 wikis")
    url = f"{base_url}/wiki/Special:NewWikis?start=&language=zh&hub=0&limit={limit}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    wikis = []
    for li in soup.find_all('li'):
        a = li.find('a')
        if a:
            wiki_name = a.text  # 获取wiki名称
            wiki_url = urljoin(base_url, a['href'])
            wiki_url = urljoin(base_url, a['href'])
            if wiki_url.startswith(base_url) or wiki_url.startswith('https://about.fandom.com') or wiki_url.startswith('https://support.fandom.com') or wiki_url.startswith('https://soap.fandom.com') or wiki_url.startswith('https://www.fandom.com') or wiki_url.startswith('https://community.fandom.com') or wiki_url.startswith('https://www.twitter.com') or wiki_url.startswith('https://www.futhead.com') or wiki_url.startswith('https://www.muthead.com') or wiki_url.startswith('https://www.fanatical.com'):
                continue

            print(f"\033[94m正在处理的wiki: {a.text}\033[0m")

            response = requests.get(wiki_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            malicious_probability = 0
            for keyword in keywords:
                if keyword in soup.get_text():
                    malicious_probability += 15

            if malicious_probability > 0:
                bureaucrats = find_bureaucrats(wiki_url)
                for bureaucrat_url, bureaucrat_name in bureaucrats:
                    wikis.append((wiki_url, wiki_name, bureaucrat_url, bureaucrat_name, malicious_probability))  # 使用wiki_name代替a.text

    # 按照恶意wiki概率从大到小排序
    wikis.sort(key=lambda x: x[4], reverse=True)

    print_header("处理结果")
    for wiki in wikis:
        print(f"\033[91mwiki链接: {wiki[0]}, wiki名字: {wiki[1]}, 行政员链接: {wiki[2]}, 行政员名字: {wiki[3]}, 恶意wiki概率: {wiki[4]}%\033[0m")  # 使用wiki[1]来获取wiki名称
def main():
    base_url = 'https://community.fandom.com'

    while True:
        print_header("欢迎来到SOAP Tool!")

        print("请选择一个选项: ")
        print("1:检查后室违规")
        print("2:检查政治违规")
        print("3:检查自提供关键词")
        print("4:退出")

        choice = input("输入选项: ")

        if choice == "4":
            break

        if choice == "1":
            keywords = ["后室", "Backrooms", "backrooms", "adaihappyjan", "backroom", "小草", "室"]
        elif choice == "2":
            keywords = ["政治", "习近平", "习", "毛泽东", "毛", "中国", "中华民族共和国", "打倒"]
        elif choice == "3":
            keywords = input("请输入关键词，用空格分开: ").split()

        print_header("请选择wiki数量")
        print("1:检查50个新wiki")
        print("2:检查100个新wiki")
        print("3:检查500个新wiki")

        limit_choice = input("输入选项: ")
        if limit_choice == "1":
            limit = 50
        elif limit_choice == "2":
            limit = 100
        elif limit_choice == "3":
            limit = 500

        process_wikis(base_url, limit, keywords)

        while True:
            rerun = input("是否重新运行程序? Y/N: ").strip().upper()
            if rerun in ["Y", "N"]:
                break
            else:
                print("无效的输入，请重新输入.")

        if rerun == "N":
            break

if __name__ == "__main__":
    main()
