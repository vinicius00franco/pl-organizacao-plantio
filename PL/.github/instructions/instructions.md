```markdown
---
applyTo: '**'
---
Primary source of project context and operational guidance is the file `AGENTS.MD` at the repository root.

Agent checklist:

- Read `AGENTS.MD` first to learn about repository structure, important files, and how to run the main notebook (`otimizacao_mix_culturas_v5_organized.ipynb`).
- Use `config/cenario/` YAMLs as scenario inputs and `otimizacao_mix_culturas_v5_organized.txt` as the primary log file.
- Follow the conventions in `AGENTS.MD`: use `print_and_log` for messages that must go to the master log; validate `LpStatus` after solving; check the area invariant (sum of plantio <= AREA_TOTAL_DISPONIVEL_HA).
- Keep edits minimal and well-scoped. If you change behavior, update `AGENTS.MD` and explain the change in the PR description.

```

---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.