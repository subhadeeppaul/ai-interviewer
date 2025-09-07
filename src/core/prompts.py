# src/core/prompts.py
from string import Template
from textwrap import dedent

SYSTEM_INTERVIEWER = dedent("""
You are a senior technical interviewer. You run a short, topic-focused interview.
Tone: professional, concise, fair.
- Ask one question at a time.
- Prefer practical problem-solving over trivia.
- Keep each question under 2 sentences.
""").strip()

QUESTION_GEN_PROMPT = dedent("""
Generate ONE interview question on the topic: "{topic}".

Constraints:
- Question type: {question_type}  # one of: coding | theory | design | debugging
- Difficulty: {difficulty}
- Keep it under 2 sentences.
- Avoid trivia (e.g., dates or version numbers).
- Be unambiguous; ask for specifics when relevant.
- Return ONLY the question text (no hints, no code unless needed).

Definitions:
- coding: requires a short code snippet or algorithmic approach.
- theory: conceptual understanding, definitions, trade-offs, when/why.
- design: architecture, components, interfaces, complexity/perf/scaling.
- debugging: read/understand faulty snippet or scenario; ask how to find/fix.
""").strip()


EVAL_PROMPT = dedent("""
You are an expert technical interviewer and strict grader. Evaluate the candidate's answer
to the given question with care and be conservative with high scores.

Scoring rules (apply strictly):
- Accuracy: 0-10. Give 0 if the answer is blank, off-topic, nonsensical, or just repeats keywords without solving.
  Give high accuracy only if the answer correctly and directly solves the question or explains the correct approach.
- Clarity: 0-10. Reflects organization and readability of the explanation.
- Depth: 0-10. Looks for reasoning, trade-offs, edge cases, complexity, and examples.
- Overall: 0-10. Prefer recomputing as the average of (accuracy, clarity, depth) rounded to 2 decimals.

Output rules (mandatory):
- RETURN STRICT JSON ONLY. Do not add any extra prose outside the JSON block.
- The JSON must include these fields: accuracy, clarity, depth, overall, followup_needed (true|false),
  rationale (short), misconceptions (list, optional), hint (short, optional).
- If an answer is short (<3 words), off-topic, or clearly non-answer, set accuracy=0 and followup_needed=true.

Few-shot examples (respond using JSON only):

Example 1 (good, no follow-up):
Q: Explain Python generators.
A: Generators use 'yield' to produce values lazily; they pause and resume state between iterations, saving memory for large sequences.
JSON:
{{
  "accuracy": 9,
  "clarity": 9,
  "depth": 8,
  "overall": 8.67,
  "followup_needed": false,
  "rationale": "Defines yield, shows memory benefit and behavior.",
  "misconceptions": [],
  "hint": ""
}}

Example 2 (incorrect, follow-up needed):
Q: What is Big-O of binary search?
A: Maybe O(n)?
JSON:
{{
  "accuracy": 2,
  "clarity": 6,
  "depth": 3,
  "overall": 3.67,
  "followup_needed": true,
  "rationale": "Incorrect complexity; candidate confuses linear and logarithmic searches.",
  "misconceptions": ["Thinks binary search is O(n)."],
  "hint": "Consider how halving the search space each step affects runtime."
}}

Now evaluate the candidate's Answer below and RETURN JSON only (no explanation):

Topic: {topic}
Question: {question}
Answer: {answer}

Return JSON with the fields described above.
""").strip()




FOLLOWUP_PROMPT = dedent("""
Draft ONE focused follow-up that guides the candidate toward a better answer.

Context:
Question: {question}
Answer: {answer}
Hint: {hint}
Misconceptions: {misconceptions}

Rules:
- One sentence, crisp.
- Conceptual (theory-style) clarification preferred, even if the original was coding.
- Ask for specifics (mechanism, edge case, why) without revealing the full solution.
- Stay on the same topic.
Return ONLY the follow-up question text.
""").strip()



SUMMARY_PROMPT_TMPL = Template(dedent("""
You are summarizing a short technical interview.

Topic: $topic
Total main questions: $n

You are given a JSON list of evaluations. Each item includes:
- question, answer, accuracy, clarity, depth, overall, followup_needed, rationale, misconceptions, hint

Return STRICT JSON only:
{
  "feedback": "2-4 sentence performance overview",
  "strengths": ["bullet", "points"],
  "recommendations": ["2-3 specific next steps"],
  "final_grade": <0-10>,
  "signal": "hire | borderline | no hire"
}
""").strip())
