# Embedded Workspace

This repository is a **central workspace** that brings together multiple tools, experiments, and integrations related to **data ingestion, indexing, chat storage, and LLM-based systems**.

If you are here looking for a **specific capability**, use the guide below to quickly find what you need.

---

## 🔍 How to Navigate This Repository

### I want to...
- **Read data from external platforms** (Jira, Twitter, Dropbox, OneDrive, etc.)
  → Look under **`readers/`**

- **Index documents, notes, or repositories**
  → Look under **`indexing/`**

- **Store or manage chat history**
  → Look under **`chat-stores/`**

- **Work with LLMs or build LLM-powered tools**
  → Look under **`llm/`**

- **Explore experiments or test setups**
  → Look under **`tests/`**

- **Prepare for interviews or internships**
  → Look under **`internship/`**

---

## 📁 Directory Guide

### 🔌 `readers/`
Tools that **connect to external services** and extract data in a structured way.

Includes:
- Jira readers
- Twitter readers
- Cloud storage readers (Dropbox, OneDrive)

Use this if your goal is **data ingestion**.

---

### 🗂️ `indexing/`
Projects focused on **processing, parsing, and indexing content** for search or retrieval.

Includes:
- OCR-based PDF parsing
- Note indexing (Obsidian)
- Repository indexing (GitLab)

Use this if your goal is **search, retrieval, or knowledge indexing**.

---

### 💬 `chat-stores/`
Storage backends for **chat history and conversational memory**.

Includes:
- Redis-based chat stores
- DynamoDB-backed chat storage

Use this if your goal is **persistent chat memory**.

---

### 🤖 `llm/`
LLM-related tools and assistants.

Includes:
- Repository assistants
- Query engines built on Ollama
- LLM experimentation projects

Use this if your goal is **building LLM-powered systems**.

---

### 🧪 `tests/`
Experimental repositories and test setups.

Use this if you are **exploring or prototyping**.

---

### 🎓 `internship/`
Learning materials and preparation notes.

Use this if you are **studying or preparing for interviews**.

---

## 🧭 Where to Start?

If you are new:
1. Identify your goal (ingestion, indexing, chat memory, LLM)
2. Jump to the corresponding directory above
3. Each project contains its own README with usage details

---

## 🕰️ About History

All projects were imported using **git subtree**, preserving:
- Original commit history
- Authors and timestamps

You can inspect history per project using:
```bash
git log -- <project-path>
