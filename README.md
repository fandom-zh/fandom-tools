# Fandom_Tool

Fandom_Tool 是由 Adaihappyjan 开发和维护的一套用于优化 Fandom wiki 管理的程序集合。目前包含两个主要工具：

1. Fandom 新社区页面检查工具 - SOAP Tool
2. 用于移动端的 SOAP Tool - SOAP Tool Mobile
3. Fandom 社区页面修订历史获取工具 - Fanhistopy
4. ZHCCC限定，用于发布公告而使用的智能简繁替换器 - EasyPost

---

## EasyPost

EasyPost 是一个用于轻松发布Fandom中文公告的只能简繁替换器。

### 版本号
0.1

### 更新
目前的版本号为 0.1

### 特性
- 支持润色功能，可以直接将英文公告使用ChatGPT API进行初步翻译和润色（虽然还是要进行手动校对）。
- 支持Fandom中文简繁对照表。
- 支持导入页面ID并自动生成链接。
- 将结果复制粘贴即可发送至Discord。

### 使用方法
运行此 Python 脚本，然后在 GUI 中输入想要转换的公告原文（英文中文即可），可选择润色，然后点击转换，并将生成的文本复制粘贴入Discord。

### 代码依赖
此代码依赖以下 Python 库：
- openai
- tkinter
- datetime
- zhconv
- re
- random

---

## Fanhistopy

Fanhistopy 是一个用于获取 Fandom（wiki）页面修订历史的 Python 工具。

### 版本号
0.3

### 更新
目前的版本号为 0.3。0.8 版本出现 BUG 需要修复。

### 特性
- 支持在 GUI 中输入 wiki 名称、语言以及起始点来获取页面的修订历史。
- 提供开始、停止和继续的功能以控制获取过程。
- 生成一个包含页面修订历史信息的文本文件。
- 显示进度条以跟踪获取过程的进度。

### 使用方法
运行此 Python 脚本，然后在 GUI 中输入相应的信息。点击“开始”按钮开始获取修订历史，点击“停止”按钮停止获取，点击“继续”按钮继续获取。获取过程的进度将在进度条中显示。

### 代码依赖
此代码依赖以下 Python 库：
- requests
- json
- tkinter
- threading

---

## Fandom 新社区页面检查工具（System of Advanced Page monitoring Tool, SOAP Tool）

### 下一步更新计划
0.3.00 版本将有以下更新：
- 增加查询非中文区（Fandom支持的语言选项）的功能
- 优化代码结构
- 增加可使用 ChatGPT 总结并判断 wiki 内容的功能
- 增加可使用 FandomZendesk 自动发送举报邮件的功能（需要用户提供 Zendesk 账号和密码）

### 功能说明
SOAP Tool 是一个 Wiki 页面监视系统，为 Fandom 社区设计，用于检查新的 wiki 页面中的内容。主要功能包括从指定数量的新 wiki 中查找含有指定关键词的页面，并将结果保存到文件中。用户可以选择关键词选项和要检查的 wiki 数量，并可以实时查看处理进度和运行速率。

### 使用方法
1. 运行程序后，点击 "开始检查 wiki" 按钮。
2. 在弹出的对话框中选择关键词选项：
   - 输入数字1：后室关键词
   - 输入数字2：CN政治关键词
   - 输入数字3：全球政治关键词
   - 输入数字4：从文件导入关键词
3. 根据选择的关键词选项，输入需要检查的 wiki 数量。
4. 程序开始检查 wiki 页面，会显示处理进度和运行速率。
5. 检查完成后，会生成一个结果文件（结果.txt），其中包含检查到的内容的相关信息。

### 注意事项
- 确保你的计算机已安装 Python 和所需的依赖库。
- 该版本为公共测试版，可能存在一些问题和不完善的功能。
- 如果您对该工具有任何问题或建议，请联系作者 Adaihappyjan。
- 如果需要对不同部分进行修改，请自行打开源代码解决，注释很全。

### 代码依赖
此代码依赖以下 Python 库：
- requests
- beautifulsoup4
- lxml
