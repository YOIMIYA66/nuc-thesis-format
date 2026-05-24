---
name: nuc-thesis-format
description: Strong formatting and writing guardrails for 中北大学软件学院2026届毕业设计说明书、毕业论文草稿、DOC/DOCX排版、中文摘要、英文摘要、参考文献、致谢和外文翻译材料。Use when Codex needs to write, revise, format, review, generate, or validate a NUC software college thesis or foreign-language translation package under strict school-template compliance.
---

# 中北大学论文格式强约束

## 必须先做

1. 读取 `references/format-rules.md`，按其中的硬性规则执行；不得只凭常见论文格式推断。
2. 若用户要生成或排版 Word 文件，必须优先复制 `assets/official-templates/` 中对应空白模板作为起点，不得从空白 Word 自建格式。
3. 若用户只要 Markdown/纯文本草稿，也必须保留装订顺序、三级标题编号、摘要关键词、引用编号和参考文献数量等内容约束。
4. 缺少姓名、学号、班级、指导教师、日期、题目、专业方向等元数据时，用 `【待补：字段名】` 标记，并在最终回复列出，不得编造。
5. 缺少可核验文献时，不得编造作者、题名、期刊、DOI、年份或链接；用 `【待补：参考文献】` 或要求用户提供来源。

## 写作与排版流程

1. 确认任务类型：毕业设计说明书、中文摘要、英文摘要、目录、正文、参考文献、致谢、外文翻译、优秀毕业设计摘要。
2. 套用图片主装订顺序：封面、中文摘要、英文摘要、目录、正文、参考文献、致谢；主要符号表、附录和优秀毕业设计摘要等可选材料仅在学校模板、指导教师或任务明确要求时插入。
3. 正文标题只用三级编号：`1`、`1.1`、`1.1.1`。三级以下只用`（1）`、`①`等规范序号；禁止用`一、二、三`、`1）`、孤立字母编号。
4. 所有图、表、公式、附注按章编号：`图1.1`、`表2.3`、`式(4.3)`。图题在图下，表题在表上，编号与题名之间空一格。
5. 正文中每个引用按出现顺序标为`[1]`、`[2]`；参考文献列表顺序必须与正文引用顺序一致。
6. 生成 DOCX 后运行：

```bash
python C:/Users/86198/.codex/skills/nuc-thesis-format/scripts/check_docx_format.py --kind thesis path/to/file.docx
```

外文翻译材料运行：

```bash
python C:/Users/86198/.codex/skills/nuc-thesis-format/scripts/check_docx_format.py --kind translation path/to/file.docx
```

## 强制验收

交付前必须做一轮自检，并在最终回复说明：

- `已满足`：明确列出已按规范处理的结构、标题、摘要、关键词、页眉页脚、参考文献、图表编号、三线表要求等。
- `待人工确认`：页数、查重率、AIGC率、Word自动目录、分页、页码显示、打印效果等无法由当前环境完全验证的项目。
- `未满足/缺材料`：列出具体缺失字段或无法完成的规范，不得笼统说“格式已按要求完成”。

## 硬性禁止

- 禁止跳过官方模板直接新建空白 Word 文件。
- 禁止把封面、摘要、目录纳入正文阿拉伯页码。
- 禁止让目录从“摘要”开始；目录从“引言/绪论”作为正文第1章开始。
- 禁止把正文一级标题写成“第一章”；统一使用 `1  标题` 形式。
- 禁止在参考文献不足20篇、英文不足5篇时宣称合格。
- 禁止编造查重率、AIGC率、页数或指导教师审核结论。

## 资源

- `references/format-rules.md`：完整格式规则与检查清单。
- `assets/official-templates/`：压缩包中的官方 `.doc` 模板和规范文档，生成 Word 时优先使用。
- `assets/format-summary.png`：用户提供的格式要求汇总图，作为人工核对依据。
- `scripts/check_docx_format.py`：DOCX格式和结构的自动化初检脚本；脚本不能替代 Word/WPS 的人工最终校验。
