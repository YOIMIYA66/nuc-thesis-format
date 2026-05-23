# nuc-thesis-format

Codex skill for writing, formatting, and checking Zhongbei University Software College thesis materials.

## Contents

- `SKILL.md`: skill instructions and guardrails.
- `references/format-rules.md`: thesis formatting rules and checklist.
- `scripts/check_docx_format.py`: automated DOCX structure and style pre-check.
- `assets/official-templates/`: source templates used when generating Word documents.
- `agents/openai.yaml`: display metadata for Codex.

## Usage

Install or copy this directory into a Codex skills directory, then invoke the skill for thesis drafts, abstracts, references, acknowledgements, foreign-language translation materials, or DOCX format checks.

For DOCX validation:

```bash
python C:/Users/86198/.codex/skills/nuc-thesis-format/scripts/check_docx_format.py --kind thesis path/to/file.docx
```

For foreign-language translation validation:

```bash
python C:/Users/86198/.codex/skills/nuc-thesis-format/scripts/check_docx_format.py --kind translation path/to/file.docx
```
