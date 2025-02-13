# Blockchain-Hackathon-AI-Evaluator
A modular AI-powered evaluation framework designed to assist judges in blockchain hackathons. Automates initial project screening and technical assessment, reducing workload and improving scoring accuracy.

Here’s a **README.md** file for your GitHub repository:  

---

## 🏆 AI Hackathon Judging System  

### 🚀 Overview  
This repository contains an **AI-assisted evaluation system** for blockchain hackathons. It automates the initial project review process by using **OpenAI’s GPT-4** to evaluate project pitches and provide structured feedback. This system helps **streamline judging, reduce workload, and ensure fairness** by applying **consistent scoring criteria** across all submissions.  

### 🎯 Features  
✅ **Automated Project Scoring** – Evaluates hackathon submissions based on predefined criteria  
✅ **AI-Powered Analysis** – Uses OpenAI’s GPT-4 to assess originality, feasibility, impact, and theme alignment  
✅ **JSON-Based Output** – Stores structured evaluation data for easy review  
✅ **Weighted Scoring System** – Calculates an overall score based on predefined weights  
✅ **Batch Processing** – Processes multiple submissions efficiently  

---

## 🛠️ Installation  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/ShaneSCalder/Blockchain-Hackathon-AI-Evaluator.git  
cd Blockchain-Hackathon-AI-Evaluator
```

### 2️⃣ Set Up a Virtual Environment (Optional but Recommended)  
```bash
python -m venv venv  
source venv/bin/activate   # On macOS/Linux  
venv\Scripts\activate      # On Windows  
```

### 3️⃣ Install Dependencies  
```bash
pip install openai
```

### 4️⃣ Set Your OpenAI API Key  
You need an OpenAI API key to run the script. Set it as an environment variable:  

```bash
export OPENAI_API_KEY="your-api-key-here"  # On macOS/Linux  
set OPENAI_API_KEY="your-api-key-here"     # On Windows  
```

Alternatively, you can hardcode it in `API_KEY` inside the script (not recommended for security reasons).  

---

## 🏗️ How It Works  

1️⃣ **Provide Hackathon Submissions**  
- Place a `submissions.json` file in the `datain/` directory.  
- The file should contain a list of hackathon projects in the following format:  

```json
[
  {
    "id": "1",
    "name": "Project Alpha",
    "high_level_pitch": "A decentralized identity verification system.",
    "project_pitch": "Project Alpha uses blockchain and zero-knowledge proofs to verify user identities while preserving privacy."
  },
  {
    "id": "2",
    "name": "Project Beta",
    "high_level_pitch": "A DeFi lending platform.",
    "project_pitch": "Project Beta allows users to stake assets and earn yield while ensuring security through smart contract audits."
  }
]
```

2️⃣ **Run the Evaluation Script**  
Execute the main script to evaluate all submissions:  

```bash
python main.py
```

3️⃣ **Get AI Evaluation Results**  
- The AI processes each project and assigns scores based on:  
  - **Short Pitch Clarity** (10%)  
  - **Originality** (20%)  
  - **Feasibility** (20%)  
  - **Impact** (15%)  
  - **Theme Alignment** (15%)  
- The final results are saved in `dataout/evaluate_submissions.json`  

Example Output:  
```json
[
  {
    "id": "1",
    "name": "Project Alpha",
    "ai_evaluation": {
      "short_pitch_score": 4,
      "originality_score": 5,
      "feasibility_score": 4,
      "impact_score": 4,
      "theme_alignment_score": 5,
      "summary": "Project Alpha introduces a privacy-preserving identity verification mechanism using blockchain.",
      "open_questions": ["How will user adoption be incentivized?", "What are the regulatory considerations?"]
    },
    "overall_score": 4.25
  }
]
```

---

## 📁 Project Structure  

```
📂 your-repo-name/
 ├── 📂 datain/             # Input folder for hackathon submissions (JSON format)
 │   ├── submissions.json   # Hackathon project submissions
 ├── 📂 dataout/            # Output folder for AI evaluations
 │   ├── evaluate_submissions.json  # AI evaluation results
 ├── main.py                # Main script for processing submissions
 ├── README.md              # Documentation for the project
 ├── requirements.txt       # Required dependencies
```

---

## 🏆 Scoring Criteria  

| Criteria             | Weight  | Description |
|----------------------|--------|-------------|
| **Short Pitch**      | 10%    | How well does the high-level pitch summarize the project? |
| **Originality**      | 20%    | How unique and innovative is the idea? |
| **Feasibility**      | 20%    | Is the project technically and practically achievable? |
| **Impact**          | 15%    | Does the project solve a meaningful problem? |
| **Theme Alignment** | 15%    | How well does the project align with the hackathon theme? |

---

## 🛡️ License  

This project is released under a Non-Commercial Open Source License.

License Terms:
Free to use for personal, educational, and research purposes.
Commercial use is strictly prohibited.
If used in an organizational setting, proper attribution is required.

 
