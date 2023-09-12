import re # 以后改用正则表达式匹配
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
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
        self.oldest_rev = None
    
    @property
    def api(self) -> str:
        return self.url + "/api.php"

    def userlink(self, username: str) -> str:
        return parse_url(self.url + "/wiki/User:" + username.replace(" ", "_")).url

def print_header(text: str):
    print("\n" + "#" * 50)
    print(text.center(50))
    print("#" * 50 + "\n")

def process_wikis(limit: int, lang: str, keywords: list[str]):
    print_header(f"开始处理{lang} wiki")
    url = f"https://community.fandom.com/wiki/Special:NewWikis"

    try:
        response = requests.get(url, {
            "language": lang,
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
            query = {
                "format": "json",
                "formatversion": 2,
                "action": "query",
                "list": "allusers",
                "augroup": "bureaucrat"
            }
            response = requests.get(wiki.api, query, headers=headers)
            wiki.bureaucrats = [obj["name"] for obj in response.json()["query"]["allusers"]]
        except:
            del query["format"]
            print(f"行政员列表获取失败！请手动检查：{wiki.api}?{urlencode(query)}")

        try:
            query = {
                "format": "json",
                "formatversion": 2,
                "action": "query",
                "list": "allrevisions",
                "arvprop": "timestamp",
                "arvlimit": 1,
                "arvdir": "newer"
            }
            response = requests.get(wiki.api, query, headers=headers)
            wiki.oldest_rev: str = response.json()["query"]["allrevisions"][0]["revisions"][0]["timestamp"]
            wiki.oldest_rev = wiki.oldest_rev.replace("T", " ").removesuffix("Z")
        except:
            del query["format"]
            print(f"获取现存最旧修订时间失败！请手动检查：{wiki.api}?{urlencode(query)}")

        sus_wikis.append(wiki)

    sus_wikis.sort(key=lambda w: w.keywords_hit, reverse=True)

    print_header("处理结果")
    for wiki in sus_wikis:
        print(f"\033[91mwiki名：{wiki.name} ({wiki.url})")
        print(f"匹配的关键词数：{wiki.keywords_hit}个")
        if wiki.oldest_rev:
            print(f"现存最旧修订时间：{wiki.oldest_rev}")
        if wiki.bureaucrats:
            print("行政员：")
            for bureaucrat in wiki.bureaucrats:
                print(f"\t{bureaucrat} ({wiki.userlink(bureaucrat)})")
        print("\033[0m")

def main(limit: int|None, lang: str|None):
    while True:
        print_header("欢迎来到SOAP Tool!")

        print("请选择一个选项：")
        print("1：检查后室违规")
        print("2：检查政治违规")
        print("3：检查自提供关键词（由键盘输入）")
        print("4：检查自提供关键词（由工作目录下的keywords.txt输入，一行一个关键词）")
        print("其它任意内容：退出")
        choice = input("输入选项：")

        if choice == "1":
            keywords = ["后室", "Backrooms", "backrooms", "adaihappyjan", "backroom", "小草", "室"]
        elif choice == "2":
            keywords = ["政治", "习近平", "习", "毛泽东", "毛", "中国", "中华民族共和国", "打倒"]
        elif choice == "3":
            keywords = input("请输入关键词，用空格分开：").split()
        elif choice == "4":
            try:
                with open("keywords.txt", "r") as fin:
                    keywords = fin.read().split()
            except:
                print("keywords.txt文件打开失败！")
                continue
        else: return
        
        input_prompt = "请输入待检查wiki的数量（10-500个）："
        while limit is None:
            try:
                limit = int(input(input_prompt))
                if limit < 10 or limit > 500: raise ValueError
            except ValueError:
                input_prompt = "无法转换为10-500之间的整数，请重新输入："
                limit = None
            else:
                break

        process_wikis(limit, lang, keywords)

        if input("输入R重新运行，输入其它任意内容以退出：").upper() != "R": return

if __name__ == "__main__":
    i = 1
    limit = None
    lang = "zh"
    while i < len(sys.argv):
        if (sys.argv[i].startswith("--lim=")):
            limit = sys.argv[i].removeprefix("--lim=")
            try:
                limit = int(limit)
                if limit < 10 or limit > 500: limit = None
            except ValueError:
                limit = None
        elif (sys.argv[i].startswith("--lang=")):
            lang = sys.argv[i].removeprefix("--lang=")
            if lang not in {
                "", "ar", "bg", "ca", "cs", "da", "de", "el",
                "en", "es", "et", "fa", "fi", "fr", "he", "hi",
                "hr", "hu", "id", "it", "ja", "ko", "ms", "nl",
                "no", "pl", "pt-br", "ro", "ru", "sr", "sv", "th",
                "tl", "tr", "uk", "vn", "zh", "zh-hk", "zh-tw"
            }: lang = "zh"
        i += 1
    main(limit, lang)