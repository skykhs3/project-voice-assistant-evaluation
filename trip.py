import requests
import json

today = "2025-01-21T09:00"
url = "http://localhost:11434/api/generate"
model = "llama3.1:8b"
trip_schedule_json = "trip_schedule_data.json"
weather_json = "weather_data.json"
utterance = "오늘 내 일정과 관련된 날씨 알려줘"

def create_request_body():
    with open(weather_json, "r") as f:
        weather_data = json.load(f)
    with open(trip_schedule_json, "r") as f:
        schedule_data = json.load(f) 
    precondition = f"""
    오늘은 {today}입니다.
    일정: {schedule_data}
    날씨: {weather_data}
    """

    data = {
        "model": model,
        "prompt": precondition+utterance,
        "format": {
            "type": "object",
            "properties": {
                "related_weather": {
                    "type": "object"
                }
            },
            "required": ["related_weather"]
        },
        "stream": True,
    }

    return data

def requset_data(body):
    try:
        response = requests.post(url, json=body, stream=True)  # stream=True 설정

        print("Streaming response:")
        for chunk in response.iter_lines(decode_unicode=True):
            if chunk:
                try:
                    parsed_chunk = json.loads(chunk)
                    print(parsed_chunk["response"],end="")
                except json.JSONDecodeError as e:
                    print("JSON Decode Error:", e)

    except json.JSONDecodeError as e:
        print("JSONDecodeError:", e)
    except requests.exceptions.RequestException as e:
        print("Request error:", e)

def main():
    body = create_request_body()
    requset_data(body)

main()