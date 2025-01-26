import requests
import json

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
    오늘은 {today}입니다.
    일정: {schedule_data}
    날씨: {weather_data}
    """
    utterance = "오늘 내 일정과 관련된 날씨 알려줘"
    return precondition + utterance

def define_response_format():
    """Define the desired response format."""
    return {
        "type": "object",
        "properties": {
            "related_weather": {
                "type": "object"
            }
        },
        "required": ["related_weather"]
    }

def build_request_payload(model, prompt, response_format):
    """Build the request payload for the API."""
    return {
        "model": model,
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
        print("Response:", json.dumps(parsed_data["response"], indent=4, ensure_ascii=False))

        return parsed_data["response"]

    except json.JSONDecodeError as error:
        print("JSON Decode Error:", error)
    except requests.exceptions.RequestException as error:
        print("Request error:", error)

def verify_response(response):
    return True

def main(model="phi4"):
    trip_schedule = load_json_file(TRIP_SCHEDULE_FILE)
    weather_data = load_json_file(WEATHER_FILE)

    prompt = generate_prompt(TODAY_DATE, trip_schedule, weather_data)
    response_format = define_response_format()

    #TODO: Offer other prompts and examine.
    request_payload = build_request_payload(model, prompt, response_format)
    response = send_request_to_api(request_payload)
    verification = verify_response(response)

    return verification

if __name__ == "__main__":
    print(main());
