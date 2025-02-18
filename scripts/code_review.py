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

def build_prompt(submission, role):
    """
    Construct the prompt for a specific code-review-focused role.
    We'll pull from the five data elements in the submission:
     1) README
     2) High-Level Explanation
     3) Hackathon Requirements
     4) Key Code Snippet
     5) Tech Stack
    """
    # Extract the data from submission
    readme_content = submission.get("readme", "")
    high_level_explanation = submission.get("high_level_explanation", "")
    hackathon_requirements = submission.get("hackathon_requirements", "")
    code_snippet = submission.get("code_snippet", "")
    tech_stack = submission.get("tech_stack", "")

    # Define specialized role descriptions
    role_descriptions = {
        "cto": """
You are a CTO Agent focusing on the project's Architecture, Scalability, and Security.

Key points to evaluate:
1. Project Structure & Organization
2. Scalability & Infrastructure
3. Security Practices
4. Code Efficiency & Performance
5. Overall Feasibility for Production
""",
        "fullstack": """
You are a Fullstack Developer Agent focusing on Readability, Maintainability, and Code Quality.

Key points to evaluate:
1. Code Readability & Documentation
2. Modularity & Reusability
3. Error Handling & Robustness
4. Overall Code Quality (linting, style, best practices)
5. Maintainability & Future Expansion
""",
        "crypto": """
You are a Crypto Engineer Agent focusing on Smart Contracts, Blockchain Security, and Gas Optimization.

Key points to evaluate:
1. Smart Contract Security & Potential Vulnerabilities
2. Gas Optimization & Cost Efficiency
3. Proper Blockchain Integration (Web3 calls, etc.)
4. Auditing or Testing Approach (if mentioned)
5. Alignment with Best Practices (e.g., OpenZeppelin standards)
""",
        "ai_engineer": """
You are an AI Engineer Agent focusing on ML Model Performance, Data Handling, and AI Accuracy.

Key points to evaluate:
1. Model Architecture & Accuracy
2. Data Handling & Preprocessing
3. Bias & Ethical Considerations
4. Performance Optimization (inference speed, resource usage)
5. Overall Feasibility & Scalability of the AI Solution
"""
    }

    # Grab the matching role description or a generic fallback
    role_text = role_descriptions.get(role, "You are an AI assistant evaluating a code submission.")

    # Build the prompt
    prompt_template = f"""
{role_text}

Below are 5 key inputs from the hackathon team:

1) README.md Submission:
{readme_content}

2) High-Level Explanation:
{high_level_explanation}

3) Hackathon Requirements Compliance:
{hackathon_requirements}

4) Key Code Snippet Submission:
{code_snippet}

5) Tech Stack Description:
{tech_stack}

Please score this submission on a scale of 1–5 for each of your 5 focus points, then provide:
- A concise 2–3 sentence summary of your overall code review.
- 2–3 open questions for the team if any ambiguities remain.

**Return your answer in valid JSON format** with no additional commentary or text.
For example:
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

def get_code_review_evaluation(submission):
    """
    Runs 4 AI evaluations based on different code-review roles.
    Returns a dictionary with 4 separate JSON responses.
    """
    # Define the four roles we want to evaluate
    roles = ["cto", "fullstack", "crypto", "ai_engineer"]
    results = {}

    for role in roles:
        prompt_text = build_prompt(submission, role)
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_text}],
                model=MODEL_NAME,
                temperature=0.0
            )
            ai_text = response.choices[0].message.content.strip()
            # Attempt to parse JSON from the AI response
            results[role] = json.loads(ai_text)
        except Exception as e:
            print(f"Error calling OpenAI API for role '{role}': {e}")
            results[role] = {}  # Return an empty dictionary if there's a failure

    return results

def main():
    """
    Reads a list of code submissions from datain/code_submissions.json, 
    uses 4 AI agents to evaluate each submission, 
    and saves each agent's review in dataout/codereview/<submission_id>_<role>.json.
    """
    # Read input from datain/code_submissions.json
    with open("datain/code_submissions.json", "r", encoding="utf-8") as f:
        submissions = json.load(f)

    # Ensure the output directory exists
    output_dir = "dataout/codereview"
    os.makedirs(output_dir, exist_ok=True)

    # Process each submission
    for sub in submissions:
        eval_results = get_code_review_evaluation(sub)

        # Save each role-based evaluation separately into dataout/codereview
        for role, evaluation in eval_results.items():
            filename = f"{output_dir}/{sub.get('id')}_{role}.json"
            with open(filename, "w", encoding="utf-8") as out:
                json.dump(evaluation, out, indent=2, ensure_ascii=False)

    print(f"Code reviews complete. Results saved in {output_dir}/")

if __name__ == "__main__":
    main()
