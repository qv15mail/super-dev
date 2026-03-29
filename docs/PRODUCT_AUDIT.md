# Super Dev 产品审查

这份文档只回答一件事：

- 如何从产品、交互、闭环和代码结构角度，审查当前项目是否真的“能用、能交付、能恢复”

---

## 命令入口

最直接的方式：

```bash
super-dev product-audit
```

会生成：

- `output/<project>-product-audit.md`
- `output/<project>-product-audit.json`

---

## 它审查什么

`product-audit` 不是单纯的代码扫描，它会同时看这几层：

1. 首次上手
2. 最短路径是否清晰
3. 用户是否知道成功标志是什么
4. 文档入口是否有断链
5. review / quality / proof-pack / release readiness 是否形成闭环
6. 是否存在会拖慢产品演进的超大核心模块

如果当前仓库本身就是 `super-dev` 项目，还会额外检查：

- 是否存在顶级 `PRODUCT` 专家
- 是否已经具备产品审查入口
- 是否把产品审查纳入 proof-pack 与 release readiness

---

## 推荐顺序

如果你要做一次完整的产品级审查，建议按这个顺序：

```bash
super-dev product-audit
super-dev feature-checklist
super-dev quality --type all
super-dev release proof-pack
super-dev release readiness
```

含义：

1. 先看产品闭环和首次上手
2. 再看功能范围缺口
3. 再看质量门禁
4. 最后汇总 proof-pack 与 release readiness

---

## 如何解释结果

`product-audit` 会输出：

- `score`
- `status`
- `strengths`
- `findings`
- `next_actions`

常见状态：

- `ready`: 当前没有阻断级产品问题
- `attention`: 存在需要尽快修复的缺口
- `revision_required`: 有 critical 问题，先修再继续交付

---

## 和 proof-pack / release readiness 的关系

从现在开始，`product-audit` 不应是独立动作。

它应该和下面两项一起使用：

- `super-dev release proof-pack`
- `super-dev release readiness`

也就是说，产品审查结果要进入交付证据，而不是只停留在讨论里。
