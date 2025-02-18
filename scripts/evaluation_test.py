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

def build_prompt(high_level_pitch, project_pitch, role):
    """
    Construct the prompt for a specific evaluator role.
    """
    role_descriptions = {
        "entrepreneur": """
You are an experienced entrepreneur evaluating hackathon projects. Focus on scalability, market potential, and the business opportunity this project represents. Consider whether this idea can attract investors, sustain growth, and differentiate itself in a competitive space.
""",
        "financial": """
You are a financial expert evaluating hackathon projects. Focus on the revenue model, investment potential, and financial sustainability of the project. Assess how well the business can scale profitably, attract funding, and manage operational costs.
""",
        "marketing": """
You are a marketing expert evaluating hackathon projects. Focus on the go-to-market strategy, branding, and customer acquisition potential. Assess the effectiveness of the project’s outreach strategy, its ability to generate interest, and its alignment with market needs.
""",
        "legal": """
You are a legal expert evaluating hackathon projects. Focus on regulatory compliance, intellectual property, and legal risks. Assess whether the project has considered legal frameworks, data privacy, and protection of proprietary information.
""",
        "cto": """
You are a CTO evaluating hackathon projects. Focus on the technical feasibility, infrastructure, and engineering decisions behind the project. Assess how scalable, secure, and efficient the technology is, as well as its potential for real-world implementation.
""",
        "developer": """
You are a software engineer evaluating hackathon projects. Focus on the code quality, implementation complexity, and maintainability. Assess whether the project follows best coding practices, is well-documented, and is efficient in execution.
"""
    }

    role_prompt = role_descriptions.get(role, "You are an AI assistant evaluating a hackathon project.")

    prompt_template = f"""
{role_prompt}

**HIGH-LEVEL PITCH**:
{high_level_pitch}

**DETAILED PROJECT PITCH**:
{project_pitch}

Evaluate the project according to these criteria (each on a 1–5 scale):

1) {role}_score_1
2) {role}_score_2
3) {role}_score_3
4) {role}_score_4
5) {role}_score_5

Then:
- Provide a concise 2–3 sentence summary of the project.
- List 2–3 open questions if there's any ambiguity.

Return your answer in JSON format without extra commentary, for example:

{{
  "{role}_score_1": <number>,
  "{role}_score_2": <number>,
  "{role}_score_3": <number>,
  "{role}_score_4": <number>,
  "{role}_score_5": <number>,
  "summary": "...",
  "open_questions": ["...", "..."]
}}
    """

    return prompt_template.strip()

def get_ai_evaluation(high_level_pitch, project_pitch):
    """
    Runs six AI evaluations based on different evaluator backgrounds.
    Returns six separate JSON responses.
    """
    roles = ["entrepreneur", "financial", "marketing", "legal", "cto", "developer"]
    results = {}

    for role in roles:
        prompt_text = build_prompt(high_level_pitch, project_pitch, role)

        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_text}],
                model=MODEL_NAME,
                temperature=0.0
            )
            ai_text = response.choices[0].message.content.strip()
            results[role] = json.loads(ai_text)  # Store each role's result separately
        
        except Exception as e:
            print(f"Error calling OpenAI API for {role}: {e}")
            results[role] = {}  # Return an empty dictionary for the failed role

    return results  # Returns a dictionary containing all six evaluations

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

    for sub in submissions:
        high_pitch = sub.get("high_level_pitch", "")
        proj_pitch = sub.get("project_pitch", "")

        ai_evaluations = get_ai_evaluation(high_pitch, proj_pitch)

        # Save each evaluation separately
        for role, evaluation in ai_evaluations.items():
            filename = f"dataout/{sub.get('id')}_{role}.json"
            with open(filename, "w", encoding="utf-8") as out:
                json.dump(evaluation, out, indent=2, ensure_ascii=False)

    print("Evaluations complete. Individual role-based results saved in dataout/")

if __name__ == "__main__":
    main()