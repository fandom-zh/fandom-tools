import re # 以后改用正则表达式匹配
import requests
from bs4 import BeautifulSoup
from urllib3.util import parse_url

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
}

class FandomWiki:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self.keywords_hit = 0
        self.bureaucrats: list[str] = []
        self.revtime = None
    
    @property
    def api(self) -> str:
        return self.url + "/api.php"

    def userlink(self, username: str) -> str:
        return parse_url(self.url + "/wiki/User:" + username.replace(" ", "_")).url

def print_header(text: str):
    print("\n" + "#" * 50)
    print(text.center(50))
    print("#" * 50 + "\n")

def process_wikis(limit: int, keywords: list[str]):
    print_header("开始处理wiki")
    url = f"https://community.fandom.com/wiki/Special:NewWikis"

    try:
        response = requests.get(url, {
            "language": "zh",
            "hub": 0,
            "limit": limit
        }, headers=headers)
    except requests.exceptions.RequestException:
        print("请求失败！")
        return        
    spnw = BeautifulSoup(response.text, 'html.parser')

    sus_wikis: list[FandomWiki] = []
    for i, a in enumerate(spnw.select(".page-content li > a")):
        wiki = FandomWiki(a.text, a["href"].replace("http://", "https://", 1).removesuffix("/"))
        print(f"\033[94m正在处理的wiki {i+1}/{limit}：{wiki.name} ({wiki.url})\033[0m")

        try:
            response = requests.get(wiki.url, headers=headers)
            wiki_mainpage = BeautifulSoup(response.text, 'html.parser').select_one(".mw-parser-output")
        except requests.exceptions.RequestException:
            print("主页获取失败！")
            continue
        if wiki_mainpage is None:
            print("这个wiki的首页可能已被删除，请手动检查！")
            continue

        for kw in keywords:
            if kw in wiki_mainpage.get_text():
                wiki.keywords_hit += 1
        if wiki.keywords_hit == 0: continue

        try:
            response = requests.get(wiki.api, {
                "format": "json",
                "formatversion": 2,
                "action": "query",
                "list": "allusers",
                "augroup": "bureaucrat"
            }, headers=headers)
            wiki.bureaucrats = [obj["name"] for obj in response.json()["query"]["allusers"]]
        except requests.exceptions.RequestException:
            print("行政员列表获取失败！")
            continue

        sus_wikis.append(wiki)

    sus_wikis.sort(key=lambda w: w.keywords_hit, reverse=True)

    print_header("处理结果")
    for wiki in sus_wikis:
        print(f"\033[91mwiki名：{wiki.name} ({wiki.url})")
        print(f"匹配的关键词数：{wiki.keywords_hit}个")
        if wiki.bureaucrats:
            print("行政员：")
            for bureaucrat in wiki.bureaucrats:
                print(f"\t{bureaucrat} ({wiki.userlink(bureaucrat)})")
        print("\033[0m")

def main():
    while True:
        print_header("欢迎来到SOAP Tool!")

        print("请选择一个选项：")
        print("1：检查后室违规")
        print("2：检查政治违规")
        print("3：检查自提供关键词")
        print("4：退出")

        choice = input("输入选项：")

        if choice == "4": return

        if choice == "1":
            keywords = ["后室", "Backrooms", "backrooms", "adaihappyjan", "backroom", "小草", "室"]
        elif choice == "2":
            keywords = ["政治", "习近平", "习", "毛泽东", "毛", "中国", "中华民族共和国", "打倒"]
        elif choice == "3":
            keywords = input("请输入关键词，用空格分开：").split()
        
        input_prompt = "请输入待检查wiki的数量（10-500个）："
        while True:
            try:
                limit = int(input(input_prompt))
                if limit < 10 or limit > 500: raise ValueError
            except ValueError:
                input_prompt = "无法转换为10-500之间的整数，请重新输入："
            else:
                break

        process_wikis(limit, keywords)

        if input("输入R重新运行，输入其它任意内容以退出：").upper() != "R": return

if __name__ == "__main__":
    main()