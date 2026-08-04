# VulnHub 靶场索引

本文件夹专门存放 VulnHub 靶场通关笔记。每台靶机一个子文件夹，内含主笔记（解题步骤 + 核心思路 + payload 技巧）与可跨靶机复用的辅助资料。

## 已收录靶机

| 靶机 | 难度 | 状态 | 主笔记 | 官方页面 |
|------|------|------|--------|----------|
| DarkHole:1 | Easy | 已通关 | [[vuln-lab/VulnHub/DarkHole-1/DarkHole-1-通关writeup\|DarkHole-1 通关笔记]] | https://www.vulnhub.com/entry/darkhole-1,724/ |

## 组织约定

- 每台靶机一个文件夹：`VulnHub/<靶机名>/`
- 主笔记命名：`<靶机名>-通关writeup.md`，三合一内容（解题步骤 + 核心思路 + payload）
- 辅助笔记命名：`payload与技巧提炼.md`，沉淀可跨靶机复用的 payload 模板
- 写作规范：中文、无 emoji、每阶段用 `>` 引用块写"核心思路"、Obsidian 双向链接互链
