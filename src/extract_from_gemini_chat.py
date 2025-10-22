from bs4 import BeautifulSoup
import pandas as pd
import re

file_path = '/Users/stefano/Downloads/Takeout 3/My Activity/Gemini Apps/MyActivity.html'

with open(file_path, 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

outer_cells = soup.find_all('div', class_='outer-cell')

extracted_data = []
for cell in outer_cells:
    regex = r"^Gemini AppsPrompted(.*?)([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}.*?)"
    match = re.search(regex, cell.get_text(strip=True), re.DOTALL)

    if match:
        text = match.group(1).strip()
        date_string = match.group(2)
    else: 
        continue    

    if len(text) < 1500:
        extracted_data.append((text, date_string))

df = pd.DataFrame(extracted_data, columns=['Prompt_Text', 'Date_String'])
df.to_csv('extracted_gemini_prompts.csv', index=False)
