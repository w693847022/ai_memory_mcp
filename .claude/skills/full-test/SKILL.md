---
name: full-test
description: 执行 ./scripts/run_tests.sh 执行全量测试
allowed-tools: Bash
---

执行项目全量测试。

操作步骤：
1. 确认 `scripts/run_tests.sh` 存在且可执行
2. 在项目根目录执行 `./scripts/run_tests.sh`
3. 等待测试执行完成
4. 向用户报告测试结果（成功/失败）及关键输出摘要
