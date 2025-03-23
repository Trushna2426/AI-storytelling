import json
import os

file_path = "story_data.json"

# Check if the file exists
if not os.path.exists(file_path):
    print("❌ Error: 'story_data.json' not found!")
    exit()

# Load JSON data
try:
    with open(file_path, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    if not dataset:
        print("⚠️ No stories found! Ensure 'story_data.json' has valid data.")
    else:
        print("✅ Dataset Loaded Successfully!")
        print(f"\nTotal Stories: {len(dataset)}\n")

        # Print the first story
        first_story = dataset[0]
        print(f"Story ID: {first_story['story_id']}")
        print(f"Prompt: {first_story['prompt']}")
        print("Choices:")
        for choice in first_story["choices"]:
            print(f"- {choice['choice_id']}: {choice['text']} ➝ {choice['outcome']}")

except json.JSONDecodeError:
    print("❌ Error: Invalid JSON format! Check 'story_data.json'.")
