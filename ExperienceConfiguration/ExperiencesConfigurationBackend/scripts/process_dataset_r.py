
import praw
import json

reddit = praw.Reddit(
	client_id="lV7Rys9pG6sbf1YAfkQSrA",
	client_secret="1oRrUc_rPvvJADHrryp7_ZynW6YWPg",
	user_agent="saved-app",
	username="Souplesse3",
	password="R_bQNc%gUB26bY3"
)

def load_existing_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_data_to_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as file:
        reversed_data = data[::-1]
        json.dump(reversed_data, file, indent=4, ensure_ascii=False)

# Function to read ignored URLs from a file
def read_ignored_urls(filename):
    try:
        with open(filename, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print("Ignored URLs file not found.")
        return []

# Load ignored URLs
ignored_urls = read_ignored_urls('./scripts/ignored_urls.txt')


# List to store extracted data
comments_data = []
posts_data = []



existing_data = load_existing_data('dataP.json')
existing_ids = {item['id'] for item in existing_data}

for item in reddit.user.me().saved(limit=None):
    if isinstance(item, praw.models.Comment) or isinstance(item, praw.models.Submission):
        if item.permalink not in ignored_urls and item.id not in existing_ids:
            data_item = {
                "metadata": {
                    "id": item.id,
                    "url": "https://www.reddit.com" + item.permalink,
                    "type": "Reddit",#"reaction" if isinstance(item, praw.models.Comment) else "post",
                    "tags": [],
                    "processed": False, # If it has been manually processed
                    "quality": 0.5,
                    "positivityRating" : 0.5 # the more it is toward 0, the more it is toxic, negative (example: roast), the more it is toward 1 the more it is positive (nobody might be offended)
                },
                "english": {
                    "instruction": "",
                    "input": "",
                    "output": item.body if isinstance(item, praw.models.Comment) else "",
                    "additional_info": ""
                },
                "french": {
                    "instruction": "",
                    "input": "",
                    "output": "",
                    "additional_info": ""
                }
            }

            existing_data.append(data_item)
            existing_ids.add(item.id)

save_data_to_json('saved_data.json', existing_data)

for item in existing_data:
    print(item)

averageToken = 70
tokenNumberObjective = 300000

print("In total, there is " + str(len(existing_data)) + "items")
print("Estimated token count : " + str(len(existing_data) * averageToken))
print("Token progression : " + str(((len(existing_data) * averageToken)/tokenNumberObjective)*100)[:4] + "%")




