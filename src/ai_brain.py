import json
import os
import urllib.request
import urllib.error


API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openrouter/free"


def load_trends():
    with open("trends.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("trends", [])


def ask_ai(trends):
    api_key = os.environ.get("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is missing")

    trends_text = "\n".join(
        f"{i + 1}. {trend}"
        for i, trend in enumerate(trends)
    )

    system_prompt = """
You are the AI creative director for an automated short-video channel.

The channel creates family-friendly AI-generated videos for children,
teenagers and adults.

Choose ONE strong original video idea from today's trends.

RULES:
- Family friendly.
- No violence.
- No sexual content.
- No dangerous challenges.
- No political propaganda.
- Do not copy existing videos.
- Create an original concept inspired by the trend.
- Prefer visually spectacular ideas.
- The video should work even without understanding English.
- Suitable for YouTube Shorts, Instagram Reels and TikTok.
- Target length: 30-45 seconds.
- Use 5-7 visual scenes.
- Make the first 2 seconds a strong hook.
- Keep the story simple.

Create a complete video plan.
"""

    user_prompt = f"""
Today's internet trend candidates:

{trends_text}

Choose the best trend for a universal family-friendly AI Short.

Consider:
1. Viral potential
2. Visual potential
3. Kid appeal
4. Adult appeal
5. Originality
6. Ability to generate it with AI video

Return the complete video plan.
"""

    schema = {
        "type": "object",
        "properties": {
            "title": {
                "type": "string"
            },
            "concept": {
                "type": "string"
            },
            "hook": {
                "type": "string"
            },
            "script": {
                "type": "string"
            },
            "scenes": {
                "type": "array",
                "minItems": 5,
                "maxItems": 7,
                "items": {
                    "type": "object",
                    "properties": {
                        "scene": {
                            "type": "integer"
                        },
                        "duration": {
                            "type": "integer"
                        },
                        "visual_prompt": {
                            "type": "string"
                        },
                        "narration": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "scene",
                        "duration",
                        "visual_prompt",
                        "narration"
                    ],
                    "additionalProperties": False
                }
            },
            "caption": {
                "type": "string"
            },
            "hashtags": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        },
        "required": [
            "title",
            "concept",
            "hook",
            "script",
            "scenes",
            "caption",
            "hashtags"
        ],
        "additionalProperties": False
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 4000,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "video_plan",
                "strict": True,
                "schema": schema
            }
        },
        "provider": {
            "require_parameters": True
        }
    }

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com",
            "X-OpenRouter-Title": "AI Trend Shorts"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as error:
        body = error.read().decode(
            "utf-8",
            errors="replace"
        )

        raise RuntimeError(
            f"OpenRouter HTTP {error.code}: {body}"
        )

    except Exception as error:
        raise RuntimeError(
            f"OpenRouter request failed: {error}"
        )

    try:
        content = result["choices"][0]["message"]["content"]

    except (KeyError, IndexError, TypeError):
        raise RuntimeError(
            "Unexpected OpenRouter response:\n"
            + json.dumps(result, indent=2)
        )

    if not content:
        raise RuntimeError(
            "OpenRouter returned empty AI content"
        )

    if isinstance(content, dict):
        ai_data = content
    else:
        content = content.strip()

        if content.startswith("```"):
            content = content.replace(
                "```json",
                "",
                1
            )
            content = content.replace(
                "```",
                ""
            )
            content = content.strip()

        try:
            ai_data = json.loads(content)

        except json.JSONDecodeError:
            print("===== RAW AI RESPONSE =====")
            print(content)
            print("===========================")

            raise RuntimeError(
                "AI response was not valid JSON"
            )

    return ai_data


def main():

    print("====================================")
    print("AI TREND SHORTS - AI BRAIN")
    print("====================================")

    trends = load_trends()

    if not trends:
        raise RuntimeError(
            "No trends found in trends.json"
        )

    print(
        f"Analyzing {len(trends)} trends..."
    )

    result = ask_ai(trends)

    with open(
        "video_plan.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            result,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("\nAI SELECTED:")
    print(
        result.get(
            "title",
            "No title"
        )
    )

    print("\nCONCEPT:")
    print(
        result.get(
            "concept",
            "No concept"
        )
    )

    print("\nHOOK:")
    print(
        result.get(
            "hook",
            "No hook"
        )
    )

    print("\nSCENES:")

    for scene in result.get(
        "scenes",
        []
    ):
        print(
            f"Scene {scene.get('scene')}: "
            f"{scene.get('visual_prompt')}"
        )

    print("\nAI PLAN CREATED SUCCESSFULLY.")


if __name__ == "__main__":
    main()
