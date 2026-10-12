# 原始 Git 历史

已将原始 Git 对象完整恢复到远端，提交编号、作者、日期和父子关系保持不变。

- `original-main`：完整首版，提交 `8543b9e19786176cbe3b9dc31c2fa45f9880c136`。
- `original-revision-illustrated`：图解修订版，提交 `71c7f079919c833365d875e10e2ae2f86bab0d25`，包括全部 7 次写作提交。
- `main`：最新阅读交付文件、字体、构建脚本与说明。在线重放版本的提交说明中也记录对应的原始提交编号。

```sh
git clone https://github.com/YZYExp/Learn-A-Cup-Of-World.git
cd Learn-A-Cup-Of-World
git log origin/original-revision-illustrated --oneline
git switch --track origin/original-revision-illustrated
```

`cup-world-original.bundle` 额外保存全部原始本地分支和提交，可离线完整恢复：

```sh
git clone cup-world-original.bundle cup-world-original
cd cup-world-original
git checkout revision-illustrated
git log --all --oneline
```
