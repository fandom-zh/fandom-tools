import re  # 使用正则表达式匹配关键词
import sys
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urlparse, urljoin
from typing import List, Optional
import logging
import csv
import json
from tqdm import tqdm
import time

# 配置日志记录
logging.basicConfig(filename='soap_tool.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
}


class FandomWiki:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self.keywords_hit = 0
        self.bureaucrats: List[str] = []
        self.oldest_rev = None

    @property
    def api(self) -> str:
        return urljoin(self.url, "/api.php")

    def userlink(self, username: str) -> str:
        return urljoin(self.url, "/wiki/User:" + username.replace(" ", "_"))


def print_header(text: str):
    print("\n" + "#" * 50)
    print(text.center(50))
    print("#" * 50 + "\n")


async def fetch(session, url, params=None):
    retries = 3
    for attempt in range(retries):
        try:
            async with session.get(url, params=params, headers=headers, timeout=10) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            logging.warning(f"请求失败，第{attempt+1}次重试：{url}，错误：{e}")
            await asyncio.sleep(1)
    logging.error(f"请求失败，已超过最大重试次数：{url}")
    return None


async def fetch_json(session, url, params=None):
    retries = 3
    for attempt in range(retries):
        try:
            async with session.get(url, params=params, headers=headers, timeout=10) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logging.warning(f"请求失败，第{attempt+1}次重试：{url}，错误：{e}")
            await asyncio.sleep(1)
    logging.error(f"请求失败，已超过最大重试次数：{url}")
    return None


async def fetch_wiki_data(session, wiki: FandomWiki, regex_patterns: List[re.Pattern]):
    logging.info(f"开始处理wiki：{wiki.name}")
    result = None

    main_page_content = await fetch(session, wiki.url)
    if not main_page_content:
        logging.error(f"无法获取主页内容：{wiki.url}")
        return result

    soup = BeautifulSoup(main_page_content, 'html.parser')
    wiki_mainpage = soup.select_one(".mw-parser-output")
    if not wiki_mainpage:
        logging.warning(f"主页可能已被删除：{wiki.url}")
        return result

    text_content = wiki_mainpage.get_text()
    for pattern in regex_patterns:
        if pattern.search(text_content):
            wiki.keywords_hit += 1

    if wiki.keywords_hit == 0:
        return result

    # 获取行政员列表
    query = {
        "format": "json",
        "formatversion": 2,
        "action": "query",
        "list": "allusers",
        "augroup": "bureaucrat"
    }
    json_data = await fetch_json(session, wiki.api, params=query)
    if json_data:
        try:
            wiki.bureaucrats = [obj["name"] for obj in json_data["query"]["allusers"]]
        except KeyError:
            logging.error(f"解析行政员列表失败：{wiki.api}")
    else:
        logging.error(f"无法获取行政员列表：{wiki.api}")

    # 获取最旧修订时间
    query = {
        "format": "json",
        "formatversion": 2,
        "action": "query",
        "list": "allrevisions",
        "arvprop": "timestamp",
        "arvlimit": 1,
        "arvdir": "newer"
    }
    json_data = await fetch_json(session, wiki.api, params=query)
    if json_data:
        try:
            wiki.oldest_rev = json_data["query"]["allrevisions"][0]["revisions"][0]["timestamp"]
            wiki.oldest_rev = wiki.oldest_rev.replace("T", " ").rstrip("Z")
        except KeyError:
            logging.error(f"解析最旧修订时间失败：{wiki.api}")
    else:
        logging.error(f"无法获取最旧修订时间：{wiki.api}")

    logging.info(f"完成处理wiki：{wiki.name}")
    return wiki


async def process_wikis(limit: int, lang: str, keywords: List[str], output_format: str):
    print_header(f"开始处理 {lang} wiki")
    url = "https://community.fandom.com/wiki/Special:NewWikis"

    async with aiohttp.ClientSession() as session:
        params = {
            "language": lang,
            "hub": 0,
            "limit": limit
        }
        page_content = await fetch(session, url, params=params)
        if not page_content:
            print("无法获取新Wiki列表！")
            return
        spnw = BeautifulSoup(page_content, 'html.parser')

        wikis = []
        for a in spnw.select(".page-content li > a"):
            href = a["href"].replace("http://", "https://", 1).rstrip("/")
            wikis.append(FandomWiki(a.text, href))

        # 编译正则表达式
        regex_patterns = [re.compile(kw, re.IGNORECASE) for kw in keywords]

        tasks = []
        for wiki in wikis:
            tasks.append(fetch_wiki_data(session, wiki, regex_patterns))

        sus_wikis = []
        start_time = time.time()
        for future in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="处理进度", unit="wiki"):
            result = await future
            if result:
                sus_wikis.append(result)
            # 更新进度条描述，估计剩余时间
            elapsed_time = time.time() - start_time
            processed = len(sus_wikis)
            remaining = len(tasks) - processed
            if processed > 0:
                avg_time_per_task = elapsed_time / processed
                eta = avg_time_per_task * remaining
                tqdm.write(f"预计剩余时间：{eta:.2f}秒")
        total_time = time.time() - start_time
        print(f"总处理时间：{total_time:.2f}秒")

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

    # 导出结果
    if output_format == 'csv':
        with open('sus_wikis.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'url', 'keywords_hit', 'oldest_rev', 'bureaucrats']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for wiki in sus_wikis:
                writer.writerow({
                    'name': wiki.name,
                    'url': wiki.url,
                    'keywords_hit': wiki.keywords_hit,
                    'oldest_rev': wiki.oldest_rev,
                    'bureaucrats': ', '.join(wiki.bureaucrats)
                })
        print("结果已导出到 sus_wikis.csv")
    elif output_format == 'json':
        with open('sus_wikis.json', 'w', encoding='utf-8') as jsonfile:
            json.dump([wiki.__dict__ for wiki in sus_wikis], jsonfile, ensure_ascii=False, indent=4)
        print("结果已导出到 sus_wikis.json")


def main(limit: Optional[int], lang: Optional[str]):
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
            keywords = [
                "后室", "Backrooms", "backrooms", "adaihappyjan", "backroom",
                "小草", "室", "层级", "层", "实体", "小屋", "聚合物", "Wikidot",
                "尘埃", "夜晚", "树", "出口", "入口", "层级列表"
            ]
        elif choice == "2":
            keywords = [
                "政治", "习近平", "习", "毛泽东", "毛", "中国", "中华人民共和国",
                "打倒", "政府", "党", "革命", "社会主义", "资本主义", "民主",
                "自由", "人权", "独裁", "腐败", "选举"
            ]
        elif choice == "3":
            keywords = input("请输入关键词，用空格分开（支持正则表达式）：").split()
        elif choice == "4":
            try:
                with open("keywords.txt", "r", encoding='utf-8') as fin:
                    keywords = [line.strip() for line in fin if line.strip()]
            except:
                print("keywords.txt文件打开失败！")
                continue
        else:
            return

        input_prompt = "请输入待检查wiki的数量（10-3000个）："
        while limit is None:
            try:
                limit = int(input(input_prompt))
                if limit < 10 or limit > 3000:
                    raise ValueError
            except ValueError:
                input_prompt = "无法转换为10-3000之间的整数，请重新输入："
                limit = None
            else:
                break

        print("请选择输出格式：")
        print("1：CSV")
        print("2：JSON")
        print("其它任意内容：不导出")
        output_choice = input("输入选项：")
        if output_choice == "1":
            output_format = 'csv'
        elif output_choice == "2":
            output_format = 'json'
        else:
            output_format = None

        asyncio.run(process_wikis(limit, lang, keywords, output_format))

        if input("输入R重新运行，输入其它任意内容以退出：").upper() != "R":
            return
        else:
            limit = None  # 重置limit，确保下一次运行时可以重新输入


if __name__ == "__main__":
    i = 1
    limit = None
    lang = "zh"
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg.startswith("--lim="):
            limit_str = arg[6:]
            try:
                limit = int(limit_str)
                if limit < 10 or limit > 3000:
                    limit = None
            except ValueError:
                limit = None
        elif arg.startswith("--lang="):
            lang = arg[7:]
        i += 1
    main(limit, lang)