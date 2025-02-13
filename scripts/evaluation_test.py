import os
import json
from openai import OpenAI

# 1) Provide your API key here, or let it come from an environment variable
API_KEY = os.environ.get("OPENAI_API_KEY")
# Alternatively, you could inline your key:
# API_KEY = "sk-..."

# 2) Create the OpenAI client
client = OpenAI(api_key=API_KEY)

# 3) Choose your model name here
MODEL_NAME = "gpt-4"  
# Or "gpt-3.5-turbo", or any other valid name you have access to.

# 4) Define scoring weights
WEIGHTS = {
    "short_pitch": 0.1,
    "originality": 0.2,
    "feasibility": 0.2,
    "impact": 0.15,
    "theme_alignment": 0.15,
}

def build_prompt(high_level_pitch, project_pitch):
    """
    Construct the prompt describing the hackathon evaluation instructions.
    We'll ask the AI for a JSON response with scores and a summary.
    """
    prompt_template = f"""
You are an AI assistant helping to evaluate hackathon projects.

**HIGH-LEVEL PITCH**:
{high_level_pitch}

**DETAILED PROJECT PITCH**:
{project_pitch}

Evaluate the project according to these criteria (each on a 1–5 scale):
1) short_pitch_score
2) originality_score
3) feasibility_score
4) impact_score
5) theme_alignment_score

Then:
- Provide a concise 2–3 sentence summary of the project.
- List 2–3 open questions if there's any ambiguity.

Return your answer in JSON format without extra commentary, for example:

{{
  "short_pitch_score": <number>,
  "originality_score": <number>,
  "feasibility_score": <number>,
  "impact_score": <number>,
  "theme_alignment_score": <number>,
  "summary": "...",
  "open_questions": ["...", "..."]
}}
    """
    return prompt_template.strip()

def get_ai_evaluation(high_level_pitch, project_pitch):
    """
    Calls the new style:
        client.chat.completions.create(...)
    Then parses the result as JSON.
    """
    prompt_text = build_prompt(high_level_pitch, project_pitch)

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt_text}],
            model=MODEL_NAME,
            temperature=0.0
        )
        # The new interface returns an object with .choices
        ai_text = response.choices[0].message.content.strip()
        # Parse JSON from AI text
        result_json = json.loads(ai_text)
        return result_json
    
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None

def calculate_weighted_score(ai_result):
    """
    Given the AI's numeric scores and predefined WEIGHTS, compute an overall score.
    """
    if not ai_result:
        return 0.0

    total = 0.0
    short_pitch = ai_result.get("short_pitch_score", 0)
    total += short_pitch * WEIGHTS["short_pitch"]

    originality = ai_result.get("originality_score", 0)
    total += originality * WEIGHTS["originality"]

    feasibility = ai_result.get("feasibility_score", 0)
    total += feasibility * WEIGHTS["feasibility"]

    impact = ai_result.get("impact_score", 0)
    total += impact * WEIGHTS["impact"]

    theme = ai_result.get("theme_alignment_score", 0)
    total += theme * WEIGHTS["theme_alignment"]

    return round(total, 3)

def main():
    # Read input from datain/submissions.json
    with open("datain/submissions.json", "r", encoding="utf-8") as f:
        submissions = json.load(f)

    results = []

    for sub in submissions:
        # Extract pitch fields
        high_pitch = sub.get("high_level_pitch", "")
        proj_pitch = sub.get("project_pitch", "")

        # Evaluate via new 'client' interface
        ai_evaluation = get_ai_evaluation(high_pitch, proj_pitch)

        overall_score = 0
        if ai_evaluation:
            overall_score = calculate_weighted_score(ai_evaluation)

        # Build a result record
        result_entry = {
            "id": sub.get("id"),
            "name": sub.get("name"),
            "ai_evaluation": ai_evaluation or {},
            "overall_score": overall_score
        }
        results.append(result_entry)

    # Sort results by overall_score descending
    results.sort(key=lambda x: x["overall_score"], reverse=True)

    # Output to dataout/evaluate_submissions.json
    with open("dataout/evaluate_submissions.json", "w", encoding="utf-8") as out:
        json.dump(results, out, indent=2, ensure_ascii=False)

    print("Evaluation complete. Results written to dataout/evaluate_submissions.json")

if __name__ == "__main__":
    main()