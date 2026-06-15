



## [百战程序员] Claude Code简介



![image-20260413181837737](imgs/image-20260413181837737.png)



Claude Code 是 Anthropic 推出的 AI 编程助手，能直接在你的电脑上帮你干活。你只需要用简单的语言告诉它要做什么，它就能理解你的项目，自动完成操作。

和普通 AI 对话有何不同？

核心区别：**不只是聊天，而是能直接帮你动手做事**

| 维度     | 普通 AI 对话（网页版）                            | Claude Code                                               |
| -------- | ------------------------------------------------- | --------------------------------------------------------- |
| 交互方式 | 复制代码 → 粘贴到对话框 → 复制回答 → 粘贴回编辑器 | 直接在你的项目里操作，不需要来回复制                      |
| 上下文   | 你告诉它什么，它才知道什么                        | 它能自己读你整个项目的代码，自己搜索文件                  |
| 执行力   | 只能给你建议和代码片段                            | 能直接创建文件、修改代码、运行命令、跑测试                |
| 记忆     | 每次对话是独立的                                  | 通过 CLAUDE.md 和 Memory 系统，它能记住项目规则和你的偏好 |
| 工具调用 | 无法调用外部工具                                  | 通过 MCP 可以连接浏览器、数据库、GitHub 等外部服务        |

一个直观的比喻：

- **普通 AI 对话** = 你打电话问一个远程顾问
- **Claude Code** = 你请了一个助手坐在你旁边，他能自己翻你的文件夹，自己动手改

<img src="imgs/image-20260413182345211.png" alt="image-20260413182345211" style="zoom:80%;" />





















## [百战程序员] 安装Claude Code



![image-20260413181837737](imgs/image-20260413181837737.png)



Claude Code的使用方式有很多，包含：终端、IDE、Web页面以及App

官网：https://claude.com/product/claude-code



### 安装流程

- 安装Git
- 安装Node
- ClaudeCode安装



### 安装Git

官网：https://git-scm.com/

傻瓜式安装即可

![image-20260413183152862](imgs/image-20260413183152862.png)



### 安装Node

官网：https://nodejs.org/zh-cn

傻瓜式安装即可

![image-20260413183306492](imgs/image-20260413183306492.png)



### Claude Code安装

我们采用最简单的使用方式和安装方式，在终端执行安装命令

> **温馨提示**
>
> 要在 `Windows PowerShell` 下执行安装命令，安装需要等待几分钟...

官网：https://claude.com/product/claude-code

安装命令：`irm https://claude.ai/install.ps1 | iex`

![image-20260413183641002](imgs/image-20260413183641002.png)



















## [百战程序员] Claude Code 配置



![image-20260413184011572](imgs/image-20260413184011572.png)



使用终端的 `Claude Code` 只需要在终端输入 `claude` 命令即可



### 第一个问题：配置环境变量



![image-20260413184115321](imgs/image-20260413184115321.png)

部分同学在执行 `claude` 命令会出现上述问题，解决如下：

> 在 PowerShell 中使用官方命令安装了 Claude Code，但运行 claude --version 时报错“无法将“claude”项识别...”，这通常意味着安装过程没有将 claude 命令所在的目录自动添加到系统的环境变量 PATH 中。系统因此在默认路径下找不到这个程序。



#### 解决方案步骤

手动添加安装目录到 PATH即可

1. 确认安装目录：`C:\Users\iwenw\.local\bin`
2. 添加环境变量
   - 在 Windows 搜索栏输入“环境变量”，选择“编辑系统环境变量”
   - 点击“环境变量”。在“用户变量”列表中找到 `Path` 变量，选中后点击“编辑”
   - 点击“新建”，然后输入 `C:\Users\iwenw\.local\bin`，点击“确定”保存所有窗口
3. 重新测试：关闭并重新打开 PowerShell，再次运行 `claude --version`



### 第二个问题：绕过校验



![image-20260413184601494](imgs/image-20260413184601494.png)



直接执行` claude ` 我们发现会报错。这是因为ClaudeCode工具会校验位置信息。国内是无法使用的，但是我们可以通过修改配置，来绕过这个校验。



#### 修改配置文件

找到C盘下，claude的json配置文件。路径：`C:\Users\iwenw\.clause.json ` ，添加以下代码

```json
"hasCompletedOnboarding": true
```

再次执行 `claude ` 命令可以正常启动了，但是现在还没有办法问它问题。Claude Code自带的大模型我们用不了（`Claude` 付费用户走远点，因为我付不起- -、）。所以接下来会接入国产的大模型



### 第三个问题：切换国产大模型

这里我们选择**阿里云百炼**，无它，免费额度够用

官网：https://bailian.console.aliyun.com/



#### 切换流程

1. 创建API-Key
2. 修改环境变量，接入千问模型
   - 设置Key：`setx ANTHROPIC_API_KEY "YOUR_DASHSCOPE_API_KEY"`
   - 设置URL：`setx ANTHROPIC_BASE_URL "https://dashscope.aliyuncs.com/apps/anthropic"`
   - 设置模型：`setx ANTHROPIC_MODEL "glm-5"`
3. 查看参数是否设置成功
   - `echo %ANTHROPIC_API_KEY%`
   - `echo %ANTHROPIC_BASE_URL%`
   - `echo %ANTHROPIC_MODEL%`



恭喜你~，走到这里，Claude Code已经可以正常运行了，如果您还遇到了其他未知问题，欢迎评论区告诉我们



















## [百战程序员] Claude Code 三种模式



![image-20260413191621735](imgs/image-20260413191621735.png)



### Claude Code制作第一个网页

为代码存放创建一个新的工作空间，例如我这里在 `F:` 盘下创建文件夹 `mkdir claude-code-demo` 作为工作空间

命令行输入：`帮我制作一个网页，用来宣传百战程序员`

![image-20260413190121926](imgs/image-20260413190121926.png)

- `Yes` 单次授权
- `Yes，and don't ask ...` 本次会话中，不在询问
- `No` 拒绝

执行完成后，我们可以去看效果了！

![image-20260413192543645](imgs/image-20260413192543645.png)



### Claude Code 三种模式

使用快捷键 `shift+tab` 切换模式

**模式一** `? for shortcuts` 修改文件前一定询问用户

**模式二** `accept edits on` 自动修改文件

**模式三** `plan mode on` 只讨论，不修改文件



