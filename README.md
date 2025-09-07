# AI Interviewer (Ollama + LangGraph)

Short, topic-focused **technical interviews** powered by a local LLM (Ollama) with **branching follow-ups, scoring, and a final summary**.

- **Stack:** Python, Ollama (Mistral by default), LangGraph, Typer (CLI)
- **Modes:** coding / theory / design / debugging (or **mixed**)
- **Branching:** weak answers trigger targeted follow-ups
- **Summary:** graded feedback with strengths & recommendations
- **Export:** `--log-json` saves full session

---

## Quickstart

```bash
# 1) Install deps (Windows: PowerShell one line)
python -m pip install -r requirements.txt

# 2) Make .env (values shown are safe defaults)
# .env
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral
OLLAMA_HOST=http://localhost:11434
INTERVIEW_DEFAULT_TOPIC=JavaScript
INTERVIEW_NUM_QUESTIONS=4
# Optional generation knobs
# OLLAMA_TEMPERATURE=0.3
# OLLAMA_TOP_P=0.9
# OLLAMA_NUM_CTX=2048
# OLLAMA_NUM_PREDICT=256

# 3) Pull the model locally
ollama pull mistral

# 4) Health check
python -m src.app ping Respond with exactly: pong
```

### Demo (Windows PowerShell)

Run an end-to-end flow (health check → single question → mini-interview → JSON log):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\demo.ps1 -Topic Python -Difficulty mixed -Questions 1 -Type mixed
```

**Seed questions:** place curated prompts in `data/questions.json`. The generator will use a seed for the requested topic/type if available, otherwise fall back to the LLM.
