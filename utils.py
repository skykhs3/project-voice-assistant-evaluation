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
    prompt = """You are an evaluation expert tasked with verifying the quality of a voice assistant's response based on given user input, assistant response, preconditions, and a defined checklist. Your role is to determine how well the assistant's response aligns with both the user query and the checklist criteria. Assign a score from 1 to 5, where 1 indicates a poor response and 5 indicates a perfect response. Provide a detailed explanation for your evaluation.

**Instructions:**

1. Read the provided **User Input** and the **Assistant Response**.
2. Refer to the **Precondition** (the contextual data or facts the assistant has access to).
3. Review the **Checklist** for specific response criteria.
4. Evaluate the assistant's response based on the checklist and assign a score from 1 to 5:
   - **5 (Excellent):** Fully satisfies all checklist criteria.
   - **4 (Good):** Satisfies most checklist criteria, with only minor issues.
   - **3 (Average):** Partially satisfies the checklist, with noticeable gaps or errors.
   - **2 (Poor):** Barely satisfies the checklist, with significant errors or omissions.
   - **1 (Very Poor):** Fails to satisfy the checklist and may provide irrelevant or incorrect information.
5. Provide a clear, concise justification for the score, highlighting both strengths and weaknesses of the response.

**Inputs:**

1. **User Input:** [Input text from the user]
2. **Assistant Response:** [Response text from the assistant]
3. **Precondition:** [JSON or other structured data containing relevant context]
4. **Checklist:** [List of criteria the response should meet]

**Output Format:**

- **Score:** [1-5]
- **Justification:** [Explain why this score was assigned, referencing the checklist and precondition.]

---

**Example Prompt with Inputs:**

**User Input:**
{user_input}

**Assistant Response:
{assistant_response}

**Precondition:**
{precondition}

**Checklist:**
1. Does the response include the title of the event(s)?
2. Does the response provide the start and end times of the event(s)?
3. Is the information accurate based on the precondition data?

**Output Example:**

- **Score:** 4  
- **Justification:** The assistant's response includes the title of the event ("dinner appointment") and the start time ("7 PM"), but it does not mention the end time ("10 PM") as specified in the precondition. While the response is accurate and informative, it is slightly incomplete according to the checklist.
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
