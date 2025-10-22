
# Plotting search topics

The code allows you to plot the topic from you search history and the gemini chats. 

You can download both of them from [Google Takeout](https://takeout.google.com/)
* `History.json` From Chrome data.
* `MyActivity.html` with all you gemini chats from "My Activity" data (in the folder that gets downloaded there will be many images and file, but only one html file)

To extract the search query run `src/extract_from_gemini_chat.py` (you'll have you change the variable `file_path` in the file). A similar process needs to be run for `src/extract_search_queries_from_history.py`.

Then with `src/extract_topics.py` we run a BERT-topic pipeline to extract the topic of each entry and `src/plotting.py` can be used for plotting. 
