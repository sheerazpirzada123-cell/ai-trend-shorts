import json
import os
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
        "model": "ltx-2.3",
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

    print(f"\nFound {len(scenes)} scenes.")

    jobs = []

    for index, scene in enumerate(scenes, start=1):

        prompt = scene.get("visual_prompt")

        if not prompt:
            print(f"Skipping Scene {index}: no visual_prompt")
            continue

        duration = int(scene.get("duration", 5))

        # Keep each generated scene between 4 and 5 seconds
        duration = max(4, min(duration, 5))

        print("\n====================================")
        print(f"GENERATING SCENE {index}/{len(scenes)}")
        print("====================================")
        print(f"Duration: {duration} seconds")
        print(f"Prompt: {prompt}")

        result = create_video(
            prompt,
            duration
        )

        jobs.append({
            "scene": index,
            "duration": duration,
            "visual_prompt": prompt,
            "magic_hour": result
        })

        print(f"Scene {index} job created successfully.")

    with open(
        "video_job.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "total_scenes": len(jobs),
                "jobs": jobs
            },
            file,
            ensure_ascii=False,
            indent=2
        )

    print("\n====================================")
    print("ALL VIDEO JOBS CREATED")
    print("====================================")

    print(f"Total jobs: {len(jobs)}")
    print("Saved to video_job.json")


if __name__ == "__main__":
    main()
