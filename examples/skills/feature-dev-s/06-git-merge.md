## Stage 8: Git Branch Merge

**目标**: 在代码实现完成后，合并开发分支回原分支

**注意**: 目标分支一般不能是 main/master 分支，如果是需要向用户确认

**流程**:

1. 确定要合并的分支部位 main 或者 master，如果是暂停后向用户确认合并分支

2. 调用 `git-branch` 技能合并分支：
   ```
   Skill: git-branch, args: "merge <feature_id> feature"
   ```

3. 技能会：
   - 切换回起始分支
   - 拉取远程更新
   - 合并开发分支（尝试自动解决冲突）
   - 调用 git-commit 技能生成提交信息
   - 打 tag（使用开发分支名）
   - 删除开发分支

4. 合并完成后更新feature状态为completed

5. 整理开发记录note，补充合并信息

---

## 输出

```
merge_result: <合并结果对象>
feature_status: completed
```
