import unittest
from datetime import datetime
import json

from utils import (
    build_request_payload,
    load_json_file,
    save_file,
    send_request_to_api,
    verify_response_llm_as_a_judge,
    json_similarity,
)


def generate_prompt(today, schedule_data, weather_data):
    precondition = f"""You are an intelligent assistant that provides schedule updates and weather information. Based on the following input, provide an accurate response.

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
                        "temperature": {"type": "number"},
                        "humidity": {"type": "number"},
                    },
                    "required": [
                        "event_name",
                        "start_datetime",
                        "end_datetime",
                        "region",
                        "condition",
                        "temperature",
                        "humidity",
                    ],
                },
            }
        },
    }


class TestWeatherScheduleAssistant(unittest.TestCase):

    @classmethod
    def configure(
        cls,
        trip_schedule,
        weather_data,
        weather_trip_data,
        today_date,
        model_name,
        response_format,
        generated_prompt,
    ):
        cls.trip_schedule = trip_schedule
        cls.weather_data = weather_data
        cls.weather_trip_data = weather_trip_data
        cls.today_date = today_date
        cls.model_name = model_name
        cls.start_datetime = datetime.now().strftime("%Y%m%d%H%M")
        cls.response_format = response_format
        cls.generated_prompt = generated_prompt

    def test_generate_prompt(self):

        precondition, user_input = generate_prompt(
            self.today_date, self.trip_schedule, self.weather_data
        )
        self.assertIn(self.today_date, precondition)
        self.assertIn("Schedules:", precondition)
        self.assertIn("Weather:", precondition)

    def test_define_response_format(self):

        response_format = define_response_format()
        self.assertIn("type", response_format)
        self.assertIn("properties", response_format)
        self.assertIn("schedule", response_format["properties"])

    def test_send_request_with_format(self):

        precondition, user_input = generate_prompt(
            self.today_date, self.trip_schedule, self.weather_data
        )
        response_format = define_response_format()
        payload = build_request_payload(
            self.model_name, precondition + user_input, response_format
        )
        api_response = send_request_to_api(API_URL, payload)
        self.assertIn("response", api_response)
        response_field = api_response.get("response")
        save_file(
            self.model_name,
            f"{self.start_datetime}_with_format",
            response_field,
            "json",
        )

        score = json_similarity(json.loads(response_field), self.weather_trip_data)
        save_file(
            self.model_name,
            f"{self.start_datetime}_score",
            score,
            "json",
        )

    def test_send_request_without_format(self):
        print("Testing send_request_without_format:")
        precondition, user_input = generate_prompt(
            self.today_date, self.trip_schedule, self.weather_data
        )

        payload = build_request_payload(self.model_name, precondition + user_input)
        api_response = send_request_to_api(API_URL, payload)
        response_field = api_response.get("response")
        self.assertIsInstance(response_field, str)
        save_file(
            self.model_name,
            f"{self.start_datetime}_without_format",
            response_field,
            "md",
        )

        api_response = verify_response_llm_as_a_judge(
            API_URL, LLM_JUDGE, response_field, precondition, user_input
        )
        response_field = api_response.get("response")
        self.assertIsInstance(response_field, str)
        save_file(
            self.model_name,
            f"{self.start_datetime}_llm_verification",
            response_field,
            "md",
        )


if __name__ == "__main__":
    TODAY_DATE = "2025-01-21T09:00"
    API_URL = "http://localhost:11434/api/generate"
    TRIP_SCHEDULE_FILE = "trip_schedule_data.json"
    WEATHER_FILE = "weather_data.json"
    TRIP_WEATHER_FILE = "trip_weather_schedule_data.json"
    LLM_JUDGE = "phi4"
    MODEL_NAME = ["phi4", "deepseek-r1:14b", "llama3"]

    for model_name in MODEL_NAME:
        trip_schedule = load_json_file(TRIP_SCHEDULE_FILE)
        weather_data = load_json_file(WEATHER_FILE)
        weather_trip_data = load_json_file(TRIP_WEATHER_FILE)
        TestWeatherScheduleAssistant.configure(
            trip_schedule,
            weather_data,
            weather_trip_data,
            TODAY_DATE,
            model_name,
            define_response_format(),
            generate_prompt(TODAY_DATE, trip_schedule, weather_data),
        )
        unittest.TextTestRunner().run(
            unittest.defaultTestLoader.loadTestsFromTestCase(
                TestWeatherScheduleAssistant
            )
        )
