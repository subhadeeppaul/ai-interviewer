# AI Interviewer CLI (Ollama LLM)

An AI-powered technical interviewer that dynamically generates questions, evaluates answers, and provides detailed feedback. Built using **Python**, **LangGraph**, and **Ollama** for local LLM inference.

---

## Features

- Interactive command-line interface (CLI) interview
- Supports dynamic question generation by topic and difficulty
- Evaluates answers based on **accuracy, clarity, and depth**
- Tracks per-topic performance and overall score
- Follow-up questions triggered for weak or incomplete answers
- Generates a final interview summary with strengths and recommendations

---

## Prerequisites

- Python >= 3.10
- Virtual environment recommended (`venv` or `conda`)
- **Ollama installed**: [https://ollama.com/docs](https://ollama.com/docs)
- Download a supported model in Ollama (e.g., `llama2` or `mistral`):

````bash
ollama pull llama2

## Installation

1. **Clone the repository:**

```bash
git clone <your-repo-url>
cd ai-interviewer


2. **Create and Activate Virtual Environment

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate
````
