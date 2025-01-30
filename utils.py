import json
import requests


def build_request_payload(model_name, prompt, response_format=None):
    return {
        "model": model_name,
        "prompt": prompt,
        "format": response_format,
        "stream": False,
    }


def load_json_file(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def send_request_to_api(api_url, payload):
    response = requests.post(api_url, json=payload)
    response.raise_for_status()
    return response.json()


def verify_response_heuristic_as_a_judge(assistant_response, standard_output):
    pass


def verify_response_llm_as_a_judge(
    api_url, model_name, assistant_response, precondition, user_input
):
    prompt = f"""You are an expert evaluator responsible for assessing the quality of a voice assistant's response. Your evaluation must consider multiple aspects, including **accuracy, fluency, semantic coherence, and response diversity**. Your goal is to assign a score for each criterion and provide a detailed justification for the evaluation.

---

### **Evaluation Criteria (각 항목별 점수 1~5점 척도)**

1. **Accuracy (정확성)**:  
   - The response correctly reflects the facts from the precondition.
   - All necessary details (e.g., event title, start/end times, location) are included.
   - No factual inconsistencies or missing key information.  

2. **Fluency (유창성)**:  
   - The response is grammatically correct and easy to read.
   - The wording is natural and human-like rather than robotic.  

3. **Semantic Coherence (의미적 일관성)**:  
   - The response maintains logical consistency.
   - It avoids contradictions and ensures smooth transitions.  

4. **Diversity (다양성)**:  
   - The response uses varied and engaging phrasing rather than repetition.
   - If multiple events are described, they are well-structured and clearly differentiated.  

---

### **Instructions:**
1. Review the **User Input**, **Assistant Response**, and **Precondition Data**.
2. Compare the assistant's response against the **Evaluation Criteria**.
3. Assign a **score from 1 to 5 for each criterion**:
   - **5 (Excellent):** Fully meets all criteria.
   - **4 (Good):** Mostly meets the criteria, with minor issues.
   - **3 (Average):** Somewhat meets the criteria, but with noticeable gaps.
   - **2 (Poor):** Significant issues, missing key details or inconsistent information.
   - **1 (Very Poor):** Fails to meet expectations, highly inaccurate or unhelpful.
4. Provide a **detailed justification** for each score, explaining any strengths or weaknesses.

---

### **User Input:**
{user_input}

### **Assistant Response:**
{assistant_response}

### **Precondition Data:**
{precondition}

---

### **Checklist Compliance:**
1. **Event Title Included:** (Yes/No)
2. **Start and End Time Provided:** (Yes/No)
3. **Information Accuracy Based on Precondition:** (Yes/No)

---

### **Final Evaluation**

| Criterion                | Score (1-5) | Justification |
|--------------------------|------------|--------------|
| **Accuracy (정확성)**       | [ ]        | [Explain Accuracy] |
| **Fluency (유창성)**        | [ ]        | [Explain Fluency] |
| **Semantic Coherence (일관성)** | [ ]        | [Explain Coherence] |
| **Diversity (다양성)**      | [ ]        | [Explain Diversity] |

---

### **Overall Feedback:**  
[Summarize the evaluation, highlighting the assistant's strengths and areas for improvement.]

---
"""

    payload = build_request_payload(model_name, prompt)
    response = send_request_to_api(api_url, payload)
    return response


def save_file(model_name, file_name, content, file_format="json"):
    if file_format == "json":
        file_path = f"results/{model_name}_{file_name}.json"
        with open(file_path, "w", encoding="utf-8") as file:
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON content: {e}")

            json.dump(content, file, ensure_ascii=False, indent=4)

    elif file_format == "md":
        file_path = f"results/{model_name}_{file_name}.md"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(
                content if isinstance(content, str) else str(content)
            )  # Save as plain text/Markdown
    else:
        raise ValueError("Unsupported file format. Use 'json' or 'md'.")
