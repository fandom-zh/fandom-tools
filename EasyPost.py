#作者：Adaihappyjan
#版本号：0.0.3
#创建时间：2023年8月29日
#最后修改时间：2023年8月29日
#说明：该程序仅限ZHCCC使用，用于生成Fandom公告内容
#是否为公共版：否
#Github地址：https://github.com/adaihappyjan/Fandom_Tool

import openai
import tkinter as tk
from tkinter import ttk, font, scrolledtext
from datetime import datetime
import zhconv
import re
import random

# 简繁对照表
translation_dict = {
    "4週": "4周",
    "存取": "访问",
    "帳號": "账号",
    "加入": "添加",
    "新增": "添加新",
    "進階": "高级",
    "陣列": "数组",
    "條目": "文章",
    "動態": "活动",
    "頻寬": "带宽",
    "封鎖": "封禁",
    "網誌": "博客",
    "網誌文章": "博客文章",
    "網誌貼文": "博客帖子",
    "機器人": "机器人",
    "快取": "缓存",
    "目錄": "目录",
    "變更": "更改",
    "代碼": "代码",
    "電腦": "电脑",
    "目次": "目录",
    "繼續": "继续",
    "建立": "创建",
    "目前": "当前",
    "剪下": "剪切",
    "資料": "数据",
    "資料庫": "数据库",
    "預設": "默认",
    "已棄用": "已弃用",
    "數位": "数字",
    "開發人員": "开发者",
    "討論板": "讨论板",
    "停用": "禁用",
    "文件": "文档",
    "傾印": "转储",
    "動態": "活动",
    "啟用": "启用",
    "擴充": "扩展",
    "擴充功能": "扩展",
    "檔案": "文件",
    "關注": "关注",
    "頁尾": "页脚",
    "表單": "表单",
    "論壇": "论坛",
    "創始人": "创始人",
    "圖庫": "图库",
    "產生": "生成",
    "指南": "指南",
    "指引": "指引",
    "質量": "质量",
    "留言": "留言",
    "訊息": "消息",
    "訊息框": "消息框",
    "介面": "界面",
    "網際網路": "互联网",
    "加入": "加入",
    "語言代碼": "语言代码",
    "載入": "加载",
    "好消息": "好消息",
    "清單": "列表",
    "討論": "讨论",
    "討論頁": "讨论页",
    "模板": "模板",
    "文字": "文本",
    "主題": "主题",
    "帖子": "帖子",
    "透過": "通过",
    "工具列": "工具栏",
    "追蹤": "追踪",
    "教學": "教程",
    "恢復": "恢复",
    "使用者": "用户",
    "使用者名稱": "用户名",
    "使用者群組": "用户组",
    "使用者頁面": "用户页",
    "變數": "变量",
    "影片": "视频",
    "視頻": "视频",
    "檢視": "查看",
    "造訪": "访问",
    "志工": "志愿者",
    "桌布": "壁纸",
    "週": "周",
    "wiki": "wiki",
    "視窗": "窗口",
    "運作": "工作",
    "存取": "访问",
    "帳號": "账户",
    "位址": "地址",
    "進階": "高级",
    "應用程式": "应用程序",
    "套用": "应用",
    "音訊": "音频",
    "列": "栏",
    "封鎖": "封禁",
    "機器人": "机器人",
    "快取": "缓存",
    "變更": "更改",
    "客戶端": "客户端",
    "欄": "列",
    "社群": "社区",
    "電腦": "电脑",
    "建立": "创建",
    "剪下": "剪切",
    "資料": "数据",
    "資料庫": "数据库",
    "預設": "默认",
    "已棄用": "已弃用",
    "裝置": "设备",
    "數位": "数码",
    "停用": "禁用",
    "文件": "文档",
    "啟用": "启用",
    "嚴重": "严重",
    "嚴重錯誤": "严重错误",
    "嚴重異常": "严重异常",
    "嚴重異常錯誤": "严重异常错误",
    "檔案": "文件",
    "字型": "字体",
    "硬體": "硬件",
    "說明": "帮助",
    "圖示": "图标",
    "身分": "身份",
    "匯入": "导入",
    "介面": "界面",
    "網際網路": "互联网",
    "資訊": "信息",
    "IP位址": "IP地址",
    "項目": "项目",
    "連結": "链接",
    "清單": "列表",
    "載入": "加载",
    "日誌": "日志",
    "登入": "登录",
    "登出": "退出",
    "訊息": "消息",
    "行動": "移动",
    "模組": "模块",
    "移動": "移动",
    "命名空間": "命名空间",
    "網路": "网络",
    "數字": "数字",
    "過時": "过时",
    "線上": "在线",
    "開啟": "打开",
    "營運": "运营",
    "業者": "运营商",
    "通過": "通过",
    "貼上": "粘贴",
    "埠": "端口",
    "入口": "门户",
    "貼文": "帖子",
    "發佈": "发布",
    "偏好設定": "首选项",
    "偏好": "首选",
    "列印": "打印",
    "隱私": "隐私",
    "計畫": "项目",
    "發布": "发布",
    "品質": "质量",
    "重新導向": "重定向",
    "重新整理": "刷新",
    "重新命名": "重命名",
    "重設": "重置",
    "解析度": "分辨率",
    "列": "行",
    "儲存": "保存",
    "搜尋": "搜索",
    "傳送": "发送",
    "伺服器": "服务器",
    "設定": "设置",
    "捷徑": "快捷方式",
    "外觀": "皮肤",
    "軟體": "软件",
    "分頁": "标签页",
    "表": "表",
    "討論": "讨论",
    "模板": "模板",
    "文字": "文本",
    "主題": "主题",
    "帖子": "帖子",
    "透過": "通过",
    "話題": "话题",
    "上傳": "上传",
    "使用者": "用户",
    "影片": "视频",
    "檢視": "查看",
    "造訪": "访问",
    "志工": "志愿者",
    "視窗": "窗口",
    "中止": "中止",
    "關於": "关于",
    "自動": "自动",
    "編輯": "编辑",
    "歷史": "历史",
    "頁面": "页面",
    "段落": "段落",
    "屬性": "属性",
    "查詢": "查询",
    "章節": "章节"
}

reverse_translation_dict = {v: k for k, v in translation_dict.items()}

# 初始化OpenAI API
openai.api_key = '自己的apikey'

# 定义润色提示
prompts_simplified = [
    "请帮助我润色以下简体中文公告，使其更加通顺并增添文学气息。同时希望内容能更加明朗，请保证不要出现英文内容，请使用简体中文输出：\n\n{}",
]

prompts_traditional = [
    "請幫助我潤色以下繁體中文公告，使其更加通順與生動，请保证不要出现英文内容，请使用繁体中文输出：\n\n{}",
]

def polish_content():
    content = content_text.get("1.0", tk.END).strip()
    # 根据选择的原文语言选择润色提示
    if language_var.get() == "简体":
        prompt_template = random.choice(prompts_simplified)
    else:
        prompt_template = random.choice(prompts_traditional)
    
    prompt = prompt_template.format(content)
    
    # 使用ChatGPT进行润色
    response = openai.Completion.create(
      engine="text-davinci-002",
      prompt=prompt,
      max_tokens=500,
      temperature=0.7  # 控制输出的确定性
    )
    
    polished_text = response.choices[0].text.strip()
    
    # 将润色后的内容放回文本框中
    content_text.delete(1.0, tk.END)
    content_text.insert(tk.END, polished_text)

# 标记已经被转换的部分
def mark_translated(text, to_lang):
    for trad, simp in translation_dict.items():
        if to_lang == 'zh-cn':
            text = text.replace(trad, f"{{{{no_trans:{simp}}}}}")
        else:
            text = text.replace(simp, f"{{{{no_trans:{trad}}}}}")
    return text

def custom_translate(text, to_lang):
    # 使用自定义的简繁对照表进行转换并标记
    marked_text = mark_translated(text, to_lang)
    
    # 使用zhconv库进行进一步的转换
    translated_text = zhconv.convert(marked_text, to_lang)
    
    # 移除标记
    translated_text = re.sub(r"{{no_trans:(.*?)}}", r"\1", translated_text)
    
    return translated_text

def generate_content():
    content = content_text.get("1.0", tk.END).strip()
    curid = curid_entry.get() if curid_var.get() else ""
    curid_str = f"https://community.fandom.com/zh/wiki/?curid={curid}" if curid else ""
    
    date_str = datetime.now().strftime('%Y/%m/%d %a.')
    
    if language_var.get() == "简体":
        traditional_content_translated = custom_translate(content, 'zh-tw')
        simplified_content = content
    else:
        traditional_content_translated = content
        simplified_content = custom_translate(content, 'zh-cn')
    
    traditional_output = f"""{date_str}
[ 臺灣正體 ]
[ 公告 ]
{traditional_content_translated}

----
"""
    simplified_output = f"""[ 大陆简体 ]
[ 公告 ]
{simplified_content}

{curid_str}

@everyone 
"""
    
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, traditional_output + simplified_output)

app = tk.Tk()
app.title("Fandom Content Generator")
app.geometry("900x700")

# Set main colors
main_color = "#FFC502"
accent_color = "#530044"

app.configure(bg=main_color)

# Set font styles
label_font = font.Font(family="Microsoft YaHei", size=14, weight="bold")
entry_font = font.Font(family="Microsoft YaHei", size=14)
text_font = font.Font(family="Microsoft YaHei", size=14)

# Create labels, text widget, entries, and button
content_label = ttk.Label(app, text="请输入内容：", background=main_color, foreground=accent_color, font=label_font)
content_label.pack(pady=10)
content_text = scrolledtext.ScrolledText(app, width=100, height=10, font=entry_font, wrap=tk.WORD)
content_text.pack(pady=10)

language_var = tk.StringVar(value="简体")
language_label = ttk.Label(app, text="原文为：", background=main_color, foreground=accent_color, font=label_font)
language_label.pack(pady=10)
language_dropdown = ttk.Combobox(app, textvariable=language_var, values=["简体", "繁体"], font=entry_font, state="readonly")
language_dropdown.pack(pady=10)

curid_var = tk.BooleanVar(value=True)
curid_check = tk.Checkbutton(app, text="包含curid", variable=curid_var, onvalue=True, offvalue=False, background=main_color, font=label_font)
curid_check.pack(pady=10)
curid_entry = ttk.Entry(app, width=100, font=entry_font)
curid_entry.pack(pady=10)

generate_button = ttk.Button(app, text="生成", command=generate_content)
generate_button.pack(pady=20)

polish_button = ttk.Button(app, text="润色", command=polish_content)
polish_button.place(x=800, y=30)

output_text = tk.Text(app, width=90, height=20, font=text_font)
output_text.pack(pady=10)

app.mainloop()