# 原始 Git 历史

`cup-world-original.bundle` 保存出版前的全部本地分支及原始提交对象，保留提交编号、作者、日期和父子关系。

```sh
git clone cup-world-original.bundle cup-world-original
cd cup-world-original
git checkout revision-illustrated
git log --all --oneline
```

GitHub 上同时按原先顺序重放每个版本，方便在线查看改动；因上传接口重新创建提交，在线提交编号与原始编号不同。原始历史以 bundle 为准。
