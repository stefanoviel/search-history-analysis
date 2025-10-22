from bertopic import BERTopic
import pandas as pd
import os

from sentence_transformers import SentenceTransformer

embedding_model_name = "all-MiniLM-L6-v2"
MIN_TOPIC_SIZE = 150
OUTPUT_FILE_NAME = "data/search_topics.csv"

all_files = [f for f in os.listdir('data') if f.endswith('.csv')]
df_list = [pd.read_csv(os.path.join('data', f)) for f in all_files]
df = pd.concat(df_list, ignore_index=True)

embedding_model = SentenceTransformer(embedding_model_name)
topic_model = BERTopic(
    embedding_model=embedding_model,
    min_topic_size=MIN_TOPIC_SIZE,
    verbose=True,
    calculate_probabilities=True 
)

print("\nStarting BERTopic model training...")
df['text'] = df['text'].astype(str)
topics, probs = topic_model.fit_transform(df['text'].tolist())
print("\nModel training complete!")

topic_info_df = topic_model.get_topic_info()

outlier_count = topic_info_df[topic_info_df.Topic == -1]['Count'].values[0]
print(f"\nSaving results to {OUTPUT_FILE_NAME}...")

topic_names_map = {row.Topic: row.Name for index, row in topic_info_df.iterrows()}

probabilities = []
for topic, prob_array in zip(topics, probs):
    if topic == -1:
        probabilities.append(0.0) 
    else:
        probabilities.append(prob_array[topic]) 

df['Topic_ID'] = topics 
df['Topic_Name'] = [topic_names_map[t] for t in topics]
df['Probability'] = probabilities

df.to_csv(OUTPUT_FILE_NAME, index=False, encoding='utf-8')
print(f"Successfully saved all {len(df)} queries with their topics.")


