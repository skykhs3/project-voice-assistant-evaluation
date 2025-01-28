import requests
import json
from datetime import datetime

# Constants
TODAY_DATE = "2025-01-21T09:00"
API_URL = "http://localhost:11434/api/generate"
TRIP_SCHEDULE_FILE = "trip_schedule_data.json"
WEATHER_FILE = "weather_data.json"

def load_json_file(file_path):
    """Load JSON data from a file."""
    with open(file_path, "r") as file:
        return json.load(file)

def generate_prompt(today, schedule_data, weather_data):
    """Generate the prompt for the model."""
    precondition = f"""
    You are an intelligent assistant that provides schedule updates and weather information. Based on the following input, provide an accurate response.

    Today' date:
    ```{today}```

    Schedules:
    ```{schedule_data}```
    
    Weather:
    ```{weather_data}```

    Task:
    - For each scheduled event, match it with the corresponding weather data based on date, time, and location.
    - Provide specific weather details (e.g., condition, temperature, humidity) for each event.
    - Highlight any adverse weather conditions (e.g., rain, extreme cold) and suggest precautions or adjustments if necessary.
    - Summarize the overall weather trends for the day, and optionally suggest the best times for outdoor activities.

    """
    user_input = "Tell me about the weather for my schedule"
    return precondition, user_input

def define_response_format():
    """Define the desired response format."""
    return {
        "type": "object",
        "properties": {
            "schedule": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "event_name": {"type": "string"},
                        "start_datetime": {"type": "string"},
                        "end_datetime": {"type": "string"},
                        "region": {"type": "string"},
                        "condition": {"type": "string"},
                        "temperature": {"type": "string"},
                        "humidity": {"type": "string"},
                    },
                    "required": ["event_name", "start_datetime", "end_datetime", "region","condition","temperature","humidity"],
                },

            }
        },
    }

def build_request_payload(model_name, prompt, response_format=None):
    """Build the request payload for the API."""
    return {
        "model": model_name,
        "prompt": prompt,
        "format": response_format,
        "stream": False,
    }

def send_request_to_api(payload):
    """Send a request to the API and handle the response."""
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        parsed_data = response.json()

        return parsed_data["response"]

    except json.JSONDecodeError as error:
        print("JSON Decode Error:", error)
    except requests.exceptions.RequestException as error:
        print("Request error:", error)

def verify_response_heuristic_as_a_judge(assistant_response, standard_output):
    pass

def verify_response_llm_as_a_judge(model_name, assistant_response, precondition, user_input):
    prompt="""You are an evaluation expert tasked with verifying the quality of a voice assistant's response based on given user input, assistant response, preconditions, and a defined checklist. Your role is to determine how well the assistant's response aligns with both the user query and the checklist criteria. Assign a score from 1 to 5, where 1 indicates a poor response and 5 indicates a perfect response. Provide a detailed explanation for your evaluation.

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

    payload=build_request_payload(model_name, prompt)
    response = send_request_to_api(payload)
    return response

def save_file(model_name,file_name, content):
    
    with open(f"results/{model_name}_{file_name}", "w") as file:
        file.write(content)

    
def main(model_name="llama3"):
    trip_schedule = load_json_file(TRIP_SCHEDULE_FILE)
    weather_data = load_json_file(WEATHER_FILE)

    precondition, user_input= generate_prompt(TODAY_DATE, trip_schedule, weather_data)
    standard_output = "The weather for your schedule is sunny with a temperature of 75°F."

    time = datetime.now().strftime("%Y%m%d%H%M")
    response_format = define_response_format()
    request_payload_with_format= build_request_payload(model_name, precondition+user_input, response_format)
    assistant_response_with_format = send_request_to_api(request_payload_with_format)
    verification_json = verify_response_heuristic_as_a_judge(assistant_response_with_format, standard_output)
    save_file(model_name,f"{time}_with_format.json",assistant_response_with_format)

    request_payload_without_format= build_request_payload(model_name, precondition+user_input)
    assistant_response_without_format = send_request_to_api(request_payload_without_format)
    save_file(model_name,f"{time}_without_format.md",assistant_response_without_format)

    verification = verify_response_llm_as_a_judge("phi4", assistant_response_without_format, precondition, user_input)
    save_file(model_name,f"{time}_llm_verification.md",verification)

if __name__ == "__main__":
    main()
