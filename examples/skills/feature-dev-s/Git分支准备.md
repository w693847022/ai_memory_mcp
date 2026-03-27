## Git 分支准备

**目标**: 在代码实现前准备 Git 开发分支

**流程**:
1. 确定当前分支不为 main 或者 master,如果是暂停后向用户确认合并分支

2. 此时已有 `feature_id`（新建的或已存在的）

3. 调用 `git-branch` 技能准备分支：
   ```
   Skill: git-branch, args: "prepare <feature_id> feature"
   ```
4. 技能会：
   - 检查当前分支是否为 main/master（如果是则拒绝）
   - 保存当前分支名
   - 创建或切换到开发分支 `feature-{id}`
