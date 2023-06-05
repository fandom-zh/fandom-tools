# Fandom_Tool
为了更好的管理fandom wiki的程序集合

目前可用工具：
Fandom社区管理工具（SOAP Tool）




# Fandom社区管理工具（SOAP Tool）

#下一步更新计划
0.3.00版本将增加查询非中文区（Fandom支持的语言选项）的功能
优化代码结构
增加可使用ChatGPT总结并判断wiki内容的功能
增加可使用Fandom Zendesk自动发送举报邮件的功能（需要用户提供Zendesk账号和密码）

#功能说明
该程序是一个Fandom社区管理工具，用于检查Fandom社区（wiki）页面中的恶意内容。主要功能包括从指定数量的新wiki中查找包含指定关键词的页面，并将结果保存到文件中。用户可以选择关键词选项和要检查的wiki数量，并可以实时查看处理进度和运行速率。

#使用方法
运行程序后，点击"开始检查wiki"按钮。
在弹出的对话框中选择关键词选项：
输入数字1：后室关键词
输入数字2：CN政治关键词
输入数字3：全球政治关键词
输入数字4：从文件导入关键词
根据选择的关键词选项，输入需要检查的wiki数量。
程序开始检查wiki页面，会显示处理进度和运行速率。
检查完成后，会生成一个结果文件（结果.txt），其中包含检查到的内容的相关信息。

#注意事项
确保你的计算机已安装Python和所需的依赖库。
该版本为公共测试版，可能存在一些问题和不完善的功能。
如果您对该工具有任何问题或建议，请联系作者 Adaihappyjan。
如果需要对不同部分进行修改，请自行打开源代码解决，注释很全。
