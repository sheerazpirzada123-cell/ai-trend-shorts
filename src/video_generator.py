import json
import os
import time
import urllib.request
import urllib.error


API_URL = "https://api.magichour.ai/v1/text-to-video"


def load_video_plan():
    with open("video_plan.json", "r", encoding="utf-8") as file:
        return json.load(file)


def create_video(prompt, duration):
    api_key = os.environ.get("MAGIC_HOUR_API_KEY")

    if not api_key:
        raise RuntimeError("MAGIC_HOUR_API_KEY is missing")

    payload = {
        "name": "AI Trend Shorts Scene",
        "end_seconds": duration,
        "aspect_ratio": "9:16",
        "resolution": "480p",
        "model": "wan-2.2",
        "audio": False,
        "style": {
            "prompt": prompt
        }
    }

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "accept": "application/json",
            "authorization": f"Bearer {api_key}",
            "content-type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as error:
        body = error.read().decode(
            "utf-8",
            errors="replace"
        )

        raise RuntimeError(
            f"Magic Hour HTTP {error.code}: {body}"
        )


def main():

    print("====================================")
    print("AI TREND SHORTS - VIDEO GENERATOR")
    print("====================================")

    plan = load_video_plan()

    scenes = plan.get("scenes", [])

    if not scenes:
        raise RuntimeError(
            "No scenes found in video_plan.json"
        )

    # TEST MODE:
    # Generate only the first scene.
    scene = scenes[0]

    prompt = scene.get("visual_prompt")

    if not prompt:
        raise RuntimeError(
            "First scene has no visual_prompt"
        )

    duration = int(
        scene.get("duration", 5)
    )

    # Keep test clip between 4 and 5 seconds.
    duration = max(4, min(duration, 5))

    print("\nGenerating TEST scene...")
    print(f"Duration: {duration} seconds")
    print(f"Prompt: {prompt}")

    result = create_video(
        prompt,
        duration
    )

    with open(
        "video_job.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            result,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("\n===== MAGIC HOUR RESPONSE =====")
    print(json.dumps(result, indent=2))

    print("\nVIDEO JOB CREATED SUCCESSFULLY.")
    print("Job information saved to video_job.json")


if __name__ == "__main__":
    main()
