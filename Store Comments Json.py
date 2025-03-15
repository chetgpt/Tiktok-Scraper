def store_comments_to_json(comments, filename="scraped_comments.json"):
    """Saves the scraped comments to a JSON file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(comments, f, ensure_ascii=False, indent=2)
        print(f"Comments saved to {filename}.")
    except Exception as e:
        print(f"Failed to save comments to {filename}. Error:", e)
