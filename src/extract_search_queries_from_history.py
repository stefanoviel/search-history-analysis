import json
from datetime import datetime
import os
import pandas as pd
from Levenshtein import distance as levenshtein_distance

file_path = '/Users/stefano/Downloads/diario/History.json'

with open(file_path, 'r') as f:
    data = json.load(f)


max_distance =7  # Define a threshold for levenshtein distance
filtered_searches = []
all_search = []

for current_entry in data['Browser History']:
    dt_object = datetime.fromtimestamp(current_entry['time_usec'] / 1_000_000)
    current_entry_with_time = {
        'text': current_entry['title'],
        'timestamp': dt_object
    }

    if filtered_searches:
        last_filtered_entry = filtered_searches[-1]

        distance = levenshtein_distance(
            current_entry_with_time['text'].lower(),
            last_filtered_entry['text'].lower()
        )

        if distance <= max_distance: # They are similar. Replace the 'last_filtered_entry' with the 'current_entry'
            filtered_searches[-1] = current_entry_with_time
        else:
            filtered_searches.append(current_entry_with_time)
    else:
        filtered_searches.append(current_entry_with_time)

os.makedirs('data', exist_ok=True)
pd.DataFrame(filtered_searches).to_csv('data/filtered_search_queries.csv', index=False)