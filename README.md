# AI Interviewer CLI (Ollama LLM)

An AI-powered technical interviewer that dynamically generates questions, evaluates answers, and provides detailed feedback. Built using **Python**, **LangGraph**, and **Ollama** for local LLM inference.

---

## Prerequisites

- Python >= 3.10
- Virtual environment recommended (`venv` or `conda`)
- **Ollama installed**: [https://ollama.com/docs](https://ollama.com/docs)
- Download a supported model in Ollama (e.g., `llama2`):

````bash
ollama pull llama2
````

## Installation

### Clone the repository:

```bash
git clone https://github.com/subhadeeppaul/ai-interviewer.git
cd ai-interviewer
````

## Setup Environment and Dependencies

### Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
````


## Setup Environment and Dependencies

### Windows

1. **Create and activate a virtual environment**

```bash
python -m venv .venv
.venv\Scripts\activate
````


## Install Python Dependencies

```bash
pip install -r requirements.txt
````

## Configure Ollama Environment (Optional)

```bash
export OLLAMA_MODEL="llama2"
````

### Windows

```bash
setx OLLAMA_MODEL "llama2"
````

## Usage

Run the CLI interview:

```bash
python -m src.app interview --topic "Machine Learning" --difficulty easy --questions 4 --type mixed --stdin
````


## Parameters

| Parameter    | Description                                         | Example                         |
|-------------|-----------------------------------------------------|---------------------------------|
| --topic      | Topic of interview questions                        | "Machine Learning"              |
| --difficulty | Difficulty level of questions (easy, medium, hard, mixed) | easy                            |
| --questions  | Number of main questions                            | 4                               |
| --type       | Question type (coding, theory, design, mixed)      | mixed                           |
| --stdin      | Enables manual multi-line input                     | (present for CLI input)         |

### Example Command

```bash
python -m src.app interview --topic "Python" --difficulty mixed --questions 3 --type coding --stdin
```

## How It Works

- **Next Question Node:** Picks a new question based on topic and difficulty.
- **Ask Node:** Displays the question and captures user input.
- **Evaluate Node:** Scores the answer using Ollama LLM on:
  - accuracy
  - clarity
  - depth
  - overall

  *Short or vague answers are penalized automatically.*

- **Follow-up Node:** Generates a follow-up question if the answer is weak.
  - Limited to `MAX_FOLLOWUPS_PER_Q` per main question
  - Ensures recursion stops and avoids `GraphRecursionError`

- **Increment/Finish Node:** Tracks progress and moves to the next main question or finishes the interview.
- **Summary Node:** Prints interview summary including:
  - Topics covered
  - Scores per topic
  - Strengths
  - Recommendations

### Persistent Issues / Caveats

- **Follow-ups:** Even vague answers may trigger follow-ups; limited by `MAX_FOLLOWUPS_PER_Q`.
- **Recursion errors:** LangGraph may throw `GraphRecursionError` if follow-ups aren’t capped or done-checks are missing. Current code resets `followup_mode` and `followup_depth` to prevent infinite loops.
- **Answer scoring:** Ollama evaluates any input, but very short or irrelevant answers may get low but non-zero scores.
- **Multi-line input:** Use an empty line to finish your answer.
- **LLM latency:** Responses depend on your local Ollama model and system speed.

### Example Run

```bash
$ python -m src.app interview --topic "Machine Learning" --difficulty easy --questions 2 --type mixed --stdin
```


### Example Output

### Example Interview Output

```text
Question 1 of 2 (Topic: Machine Learning, Difficulty: easy)
[Q] Can you explain supervised vs unsupervised learning?
Your answer (blank line to finish): Labelled data vs unlabelled data

→ Scores: accuracy=2.0, clarity=6.0, depth=3.0, overall=3.67
→ Rationale: Partially correct explanation; examples missing.
→ Follow-up flagged.

[Q] (Follow-up) Could you elaborate with concrete examples?
Your answer (blank line to finish): Clustering for unsupervised, regression for supervised

→ Scores: accuracy=6.0, clarity=7.0, depth=5.0, overall=6.0
→ Rationale: Examples provided, explanation improved.
```

````
