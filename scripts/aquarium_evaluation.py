import os
import json
import csv
import openai

# export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = API_KEY

# define model here 4.5, mini etc. 
MODEL_NAME = "gpt-4" 

# Break down your steps here, objectives, and additional context 
QUESTION_CONTEXTS = {
    "q1": "The objective of the Residency is to build an impactful project on the XRP Ledger, you plan to do so as a...",
    "q2": (
        "If you are a project owner, what is your idea linked to the residency theme, and how far along are you? "
        "If you are a developer, what kind of project do you want to work on? Which Web3 projects inspire you?"
    ),
    "q3": "Insight into how the applicant discovered the program.",
    "q4": "What do you do for fun? What gets you up in the morning?",
    "q5": "What skills do you have (technical, non-technical, any field of expertise)?",
    "q6": "What legacy or impact do you hope to leave behind?",
    "q7": (
        "Drop-down (1-5):\n"
        "1. What is blockchain?\n"
        "2. I am learning\n"
        "3. I have already used blockchain for a project.\n"
        "4. I am a blockchain expert.\n"
        "5. I'm an XRP Ledger Ninja!"
    )
}

# define your agents here
AGENTS = [
    {
        "agent_name": "Blockchain Engineer",
        "role_prompt": (
            "You are a senior blockchain engineer with deep knowledge of the XRP Ledger. "
            "You will evaluate the applicant's project from a technical standpoint, focusing "
            "on security, feasibility, and alignment with XRPL's capabilities."
        )
    },
    {
        "agent_name": "Company Owner",
        "role_prompt": (
            "You are a business-minded entrepreneur looking for strong business models, ROI, "
            "and market impact. You care about how the applicant’s project could thrive commercially "
            "and attract funding or partnerships."
        )
    },
    {
        "agent_name": "AI Specialist",
        "role_prompt": (
            "You are an AI researcher specializing in machine learning and large language models. "
            "You will focus on the novelty of the applicant’s AI concepts, data usage, and the overall "
            "technical soundness of integrating AI with the XRPL."
        )
    },
    {
        "agent_name": "Ecosystem Visionary",
        "role_prompt": (
            "You have a broad view of the XRPL Commons ecosystem. You want to see projects that align "
            "with community values, can collaborate effectively in the cohort, and will have a long-term "
            "positive impact."
        )
    },
]

# scoring 
WEIGHTS = {
    "alignment_with_cohort_focus": 0.2,
    "feasibility_and_technical_strength": 0.2,
    "innovative_potential": 0.2,
    "ecosystem_fit": 0.2,
    "applicant_background_and_skills": 0.2
}

# Additional background info 
BACKGROUND_INFO = (
    "XRPL Commons Aquarium Cohort #6 focuses on the intersection of AI and blockchain "
    "using the XRP Ledger. Participants will explore how blockchain can enhance AI by "
    "providing secure, transparent, and decentralized environments for data and "
    "algorithmic processes. This cohort seeks innovative developers, entrepreneurs, and "
    "visionaries who can collaborate to push the boundaries of AI on the XRPL."
)

def build_agent_prompt(agent_role_prompt, applicant_type, applicant_responses, background_info):
    question_blocks = []
    for q_key, q_context in QUESTION_CONTEXTS.items():
        answer = applicant_responses.get(q_key, "")
        question_blocks.append(
            f"Question {q_key.upper()} Context: {q_context}\n"
            f"Applicant's Answer: {answer}\n"
        )

    all_questions_text = "\n".join(question_blocks)

    prompt = f"""
{agent_role_prompt}

You are reviewing an application to the XRPL Commons Aquarium Cohort #6.
The focus is on integrating AI and the XRP Ledger.

Applicant Type: {applicant_type}

Background Info:
{background_info}

Below are the applicant's answers to the 7 questions, each with contextual notes:

{all_questions_text}

Evaluate this applicant on the following 1-5 scale criteria:
1) alignment_with_cohort_focus
2) feasibility_and_technical_strength
3) innovative_potential
4) ecosystem_fit
5) applicant_background_and_skills

Then provide:
- A JSON object with these five scores.
- A brief 'summary' (1-3 sentences) explaining your reasoning.
- Up to 2-3 'open_questions' if anything is unclear about the application.
- 2-3 follow-up 'interview_questions' for the applicant.

# Json setup here 
Return ONLY valid JSON with exactly these keys:
{{
  "alignment_with_cohort_focus": <number>,
  "feasibility_and_technical_strength": <number>,
  "innovative_potential": <number>,
  "ecosystem_fit": <number>,
  "applicant_background_and_skills": <number>,
  "summary": "...",
  "open_questions": ["...", "..."],
  "interview_questions": ["...", "..."]
}}
"""
    return prompt.strip()

def get_agent_evaluation(role_prompt, applicant_type, applicant_responses, background_info):
    prompt_text = build_agent_prompt(role_prompt, applicant_type, applicant_responses, background_info)
    try:
        response = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt_text}],
            temperature=0.0
        )
        ai_text = response.choices[0].message.content.strip()
        result_json = json.loads(ai_text)
        return result_json
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return None

def calculate_weighted_score(ai_result):
    if not ai_result:
        return 0.0
    total = 0.0
    total += ai_result.get("alignment_with_cohort_focus", 0) * WEIGHTS["alignment_with_cohort_focus"]
    total += ai_result.get("feasibility_and_technical_strength", 0) * WEIGHTS["feasibility_and_technical_strength"]
    total += ai_result.get("innovative_potential", 0) * WEIGHTS["innovative_potential"]
    total += ai_result.get("ecosystem_fit", 0) * WEIGHTS["ecosystem_fit"]
    total += ai_result.get("applicant_background_and_skills", 0) * WEIGHTS["applicant_background_and_skills"]
    return round(total, 3)

def main():
    # 1) Read applicant submissions from aquariumdatain/submissions.json
    input_file = "aquariumdatain/submissions.json"
    with open(input_file, "r", encoding="utf-8") as f:
        submissions = json.load(f)

    results = []

    # 2) Iterate over each applicant
    for sub in submissions:
        applicant_id = sub.get("id")
        applicant_type = sub.get("applicant_type", "Unknown")
        applicant_responses = sub.get("responses", {})

        agent_evaluations = []
        for agent in AGENTS:
            agent_eval = get_agent_evaluation(
                agent["role_prompt"], applicant_type, applicant_responses, BACKGROUND_INFO
            )
            if agent_eval:
                w_score = calculate_weighted_score(agent_eval)
                agent_eval["agent_name"] = agent["agent_name"]
                agent_eval["weighted_score"] = w_score
            else:
                # If there's an error, store it to preserve the agent_name
                agent_eval = {
                    "agent_name": agent["agent_name"],
                    "error": True
                }

            agent_evaluations.append(agent_eval)

        # Calculate overall score for the applicant
        valid_evals = [ae for ae in agent_evaluations if not ae.get("error")]
        if valid_evals:
            overall_score = sum(ae["weighted_score"] for ae in valid_evals) / len(valid_evals)
        else:
            overall_score = 0

        # Store the final record
        results.append({
            "id": applicant_id,
            "agent_evaluations": agent_evaluations,
            "overall_score": round(overall_score, 3)
        })

    # 3) Sort descending by overall_score
    results.sort(key=lambda x: x["overall_score"], reverse=True)

    # 4) Write JSON results to aquariumdataout/questions1_7/evaluations.json
    output_folder = "aquariumdataout/questions1_7"
    os.makedirs(output_folder, exist_ok=True)
    output_json_file = os.path.join(output_folder, "evaluations.json")
    with open(output_json_file, "w", encoding="utf-8") as out:
        json.dump(results, out, indent=2, ensure_ascii=False)
    print(f"Evaluation complete. Full JSON results written to {output_json_file}")

    # 5) Create a summary CSV with [id, overall_score] for easy import into Google Sheets
    output_csv_file = os.path.join(output_folder, "eval_summary.csv")
    with open(output_csv_file, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Write a header row
        writer.writerow(["id", "overall_score"])
        # Write each applicant row
        for entry in results:
            writer.writerow([entry["id"], entry["overall_score"]])
    print(f"Summary CSV with [id, overall_score] written to {output_csv_file}")

    # 6) Optionally, pick top N candidates (e.g., top 3) for quick reference
    top_n = 3
    top_candidates = results[:top_n]
    print("\nTop Candidates:")
    for idx, candidate in enumerate(top_candidates, start=1):
        print(f"{idx}. ID = {candidate['id']}, Overall Score = {candidate['overall_score']}")

    # 7) Create a detailed CSV for the top N, including each agent's scores, summary, questions
    top_details_file = os.path.join(output_folder, "top_candidates_details.csv")
    with open(top_details_file, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Write a header row for the detailed table
        writer.writerow([
            "rank",
            "id",
            "overall_score",
            "agent_name",
            "alignment_with_cohort_focus",
            "feasibility_and_technical_strength",
            "innovative_potential",
            "ecosystem_fit",
            "applicant_background_and_skills",
            "summary",
            "open_questions",
            "interview_questions"
        ])

        for rank, candidate in enumerate(top_candidates, start=1):
            for agent_eval in candidate["agent_evaluations"]:
                if agent_eval.get("error"):
                    # If an agent had an error, skip or record partial info
                    continue

                # Flatten open_questions and interview_questions into strings
                open_qs = ", ".join(agent_eval.get("open_questions", []))
                interview_qs = ", ".join(agent_eval.get("interview_questions", []))

                row = [
                    rank,
                    candidate["id"],
                    candidate["overall_score"],
                    agent_eval["agent_name"],
                    agent_eval.get("alignment_with_cohort_focus", ""),
                    agent_eval.get("feasibility_and_technical_strength", ""),
                    agent_eval.get("innovative_potential", ""),
                    agent_eval.get("ecosystem_fit", ""),
                    agent_eval.get("applicant_background_and_skills", ""),
                    agent_eval.get("summary", ""),
                    open_qs,
                    interview_qs
                ]
                writer.writerow(row)

    print(f"Detailed CSV for top {top_n} candidates written to {top_details_file}")

if __name__ == "__main__":
    main()

