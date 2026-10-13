# 原始历史与成品审计

## 已保留的原始提交

原始写作历史已在远端分支保存，提交编号、作者、日期与父子关系保持原样。2026年10月13日核对的分支头如下：

| 分支 | 提交 |
| --- | --- |
| `original-main` | `8543b9e19786176cbe3b9dc31c2fa45f9880c136` |
| `original-revision-illustrated` | `71c7f079919c833365d875e10e2ae2f86bab0d25` |

图解修订分支包含全部 7 次原始写作提交。主要公开提交的用途见 [CHANGELOG.md](../CHANGELOG.md)。

```bash
git fetch origin original-revision-illustrated:refs/remotes/origin/original-revision-illustrated
git log origin/original-revision-illustrated --oneline
git switch --track origin/original-revision-illustrated
```

`main` 今后保存书稿、配图与构建脚本。重复的 `cup-world-original.bundle` 和一次性恢复 workflow 已移除；需要离线备份时，可以自行在仓库目录之外生成 Git bundle。

## 本次审计

审计基准为 PR #7 合并后的 `11ecfe51bbd2b5734fc7a8469f25d2c57a2af395`。完整数据见 [artifact-audit-before.json](artifact-audit-before.json)。

| 当前目录中的对象 | 文件数 | 合计大小 |
| --- | ---: | ---: |
| `books/` 中的成品与重复导出 | 30 | 46.61 MiB |
| 可重绘的矢量 PDF 图稿 | 21 | 0.31 MiB |
| 重复的历史 bundle | 1 | 8.27 MiB |
| 全部受版本管理文件 | — | 97.97 MiB |

本次移除前三项，当前文件树减少约 **55.18 MiB**，保留约 **42.8 MiB** 的源码、实际配图、字体与说明。重复目录中的图片可能与源码图片共用 Git 对象，所以文件树减量不能直接当成 Git 对象库减量。

沿该基准提交的 `main` 历史，审计识别到 152 个与上述成品路径关联的唯一 blob，未压缩大小约 122.64 MiB。这不是克隆流量、pack 大小或可立即回收的空间；其中有对象仍可能被其他路径、分支或 PR 引用。审计不包含其他分支的独立历史。

复核方法：

```bash
python scripts/audit_artifact_history.py --ref 11ecfe5
```

## 为什么本次 PR 不会缩小已有完整历史

普通删除提交只改变新的文件树，旧提交仍能访问旧 PDF、ZIP 和 bundle。PR 合并时会增加一个提交，不会替换旧提交的父链。浅克隆可以直接取新的轻量文件树；已有完整克隆的 `.git` 不能靠这次删除自动缩小。

本次先停止未来继续积累成品：不再提交 `books/`、矢量 PDF 图稿和历史 bundle；不再默认导出逐章 PDF 或 ZIP；网页按章阅读，发布时附一个全书 PDF。

## 若后续需要清理旧大文件

历史重写需要单独协调：它会改变受影响提交的 SHA，需检查活动分支、旧 PR 引用和协作者的本地克隆。建议按以下顺序进行，而不是在普通 PR 分支里重写 `main`：

1. 在独立镜像克隆中备份全部 refs，备份文件保存在仓库之外；记录上述两个原始历史分支的 SHA。
2. 在备份后的镜像副本中用 `git filter-repo` 去除成品路径：`books/`、`history/cup-world-original.bundle`、`assets/figures/*.pdf`。
3. 检查过滤前后的源码树、书稿、实际图片、署名与许可；运行完整构建。核对原始历史分支是否仍保持记录的 SHA，若发生变化则先调整过滤范围。
4. 提供过滤报告、提交映射与体积变化供维护者审阅，再协调哪些远端分支需要替换、归档或删除。
5. 完成远端历史替换后，协作者重新克隆或按新 refs 更新。若旧 PR 或其他托管 refs 仍保留对象，需再检查托管端的回收范围。

本次 PR 没有强推、删除远端分支或改写原始历史。
