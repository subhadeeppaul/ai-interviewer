# AI Interviewer (pre-work)

I’m building a small tool that simulates a short, adaptive technical interview (3–5 questions). If an answer is weak, it asks one follow-up. At the end it gives a short, useful summary.

## Why

Most mock interviews feel static: fixed question lists and vague feedback. I want something closer to a real interviewer: it should adapt, probe when needed, and then clearly explain how the candidate did.

## What it does (snapshot)

- Asks 3–5 topic-based questions (e.g., JavaScript, Machine Learning).
- Branches after each answer: if it’s weak → one follow-up; otherwise next question.
- Keeps track of context and verdicts.
- Ends with a short summary (strengths, areas to improve, optional score).

## How I’m building it

- LangGraph to orchestrate the branching flow.
- LLM (OpenAI to start; can swap to local models) to generate questions, evaluate answers, and write the summary.
- State & memory to keep the conversation coherent and one-question-at-a-time.
- Prompt engineering to maintain a consistent interviewer tone.

## Requirements (from the pre-work)

- LangChain or LangGraph (I’m using LangGraph).
- LLM integration (OpenAI / Anthropic / Gemini or local LLaMA/Mistral via Ollama/Transformers).
- Branching logic with follow-ups for weak answers.
- Memory / conversation state.
- Prompt engineering.
- Optional: vector store for vetted questions; answer scoring.

## Status

- Level 1 (this commit): repo scaffold and plan.
- Next: minimal CLI loop, strict JSON evaluation, and branching (incorrect → one follow-up → proceed).

## Run locally

```bash
python -m venv .venv
# mac/linux
source .venv/bin/activate
# windows
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # add your key later
python -m src.app
```
