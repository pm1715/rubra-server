"""
Full-stack Rubra demo — no API key, no cost.

Instruments a small multi-tool agent, routes its LLM call and the goal-metric
judge through a local Ollama server (started automatically by
.devcontainer/start-ollama.sh), evaluates the resulting trace across all 36
metrics, and leaves the trace in the shared database so rubra-server's
dashboard can display and re-evaluate it.

Run inside the devcontainer/Codespace:
    python examples/full_stack_demo.py

Then open the forwarded port-8000 dashboard to inspect the trace.
"""
from __future__ import annotations

import os

import openai
import rubra

OLLAMA_MODEL = os.environ.get("RUBRA_DEMO_MODEL", "llama3.2:1b")
JUDGE_MODEL = f"ollama/{OLLAMA_MODEL}"

client = rubra.patch(
    openai.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
)


@rubra.tool
def get_weather(city: str) -> str:
    fake_data = {"paris": "18C, cloudy", "tokyo": "26C, sunny", "mumbai": "31C, humid"}
    return fake_data.get(city.lower(), "Unknown city")


@rubra.tool
def convert_celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 9 / 5 + 32


@rubra.agent(
    task="Report today's weather in Tokyo in both Celsius and Fahrenheit",
    expected_tool_calls=["get_weather", "convert_celsius_to_fahrenheit"],
)
def weather_agent(question: str) -> str:
    weather = get_weather("Tokyo")
    temp_c = float(weather.split("C")[0])
    temp_f = convert_celsius_to_fahrenheit(temp_c)

    response = client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": (
                    f"The weather in Tokyo is {weather}, which is {temp_f:.1f}F. "
                    "Write one short sentence reporting this to the user."
                ),
            },
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print(f"Using Ollama model '{OLLAMA_MODEL}' for both the agent and the judge.\n")

    result = weather_agent("What's the weather like in Tokyo today?")
    print("Agent said:", result)

    trace = rubra.get_last_trace()
    report = rubra.evaluate(trace, metrics="all", judge_model=JUDGE_MODEL)

    print()
    print(report.summary())
    print(f"\nTrace ID: {trace.trace_id}")
    print("Start the server (uvicorn app.main:app --reload) and open the")
    print("dashboard to inspect this trace and re-run evaluations from the UI.")
