---
namd: generate git commit message (生成git的提交信息)
description: 根据当前项目下 git 待提交文件的修改，自动生成符合 Conventional Commits 规范的中文提交信息。
allowed-tools: Read (只读)
---

# 格式规范
<type>(<scope>): <subject>
<body>

# 提交内容要求
- 语言: 中文
- Type: 必须是以下之一: feat, fix, docs, style, refactor, test, chore, perf, revert。
- Subject: 使用祈使句，首字母小写，不超过 50 字，结尾不加句号。
- Body: 详细说明变更原因。
- 不要增加非提交信息之外信息,比如"Generated with Claude Code"
    - 比如:该消息由xxx生成.
    - 比如:Co-Authored-Byxxx.


# 内容依据
必须是[Changes to be committed:]里的文件

# 提交流程

1. **提交前准备**
    - 子代理完成当前步骤
    - 展示当前目录和分支名称
    - 拉取远程更新
    - 检测是否有冲突文件,有冲突则展示冲突列表并退出提交流程
    - 退出子代理

2. **提交范围确认**
    - 子代理完成当前步骤
    - 列出需要提交的文件列表,并展示是[新增/修改/删除],如果列表为空则向用户询问希望暂存那些文件.
    - 自动忽略 gitingore的文件
    - 用户确认后进入下一步
    - 退出子代理

3. **生成提交信息**
    - 子代理完成当前步骤
    - 查看用户确认的提交范围的文件diff
    - 生成提交信息
    - 询问用户是否修改
    - 无修改后进入下一步
    - 退出子代理

4. **最终提交**
    - 展示提交目录和分支
    - 展示提交内容
    - 用户确认后进行提交
        - 实际提交消息要保持和用户确认的字符串一致,不要增加额外内容.
    - 如果提示提交前需要拉取远程,则返回阶段1重新开始.

