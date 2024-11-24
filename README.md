# litreview-ai
Literature review is time consuming and boring... let AI do it for you!

## Background
Our uni gets us to do a minimum of 25 pages of literature review for each semesters engineering project, this is both tedious, boring and time
consuming.
I got claude to write me a boilerplate code for streamlit and I added the ollama functionality to it with web scraping.

## Features:
1. scrapes web for research papers (arxiv, google scholar, etc)
2. displays description, AI analysis and paper link
3. downloadable markdown file for you to use!!

## What do I need?
- python
- a beefy PC (at least a 3050 recommended)
- ollama

## Installation and usage
I won't be hosting web scraping apps so this project is self hostable.
 ```sh
 pip install streamlit ollama googlesearch-python newspaper3k
 ```

Install ollama, an LLM interface for open source LLMs (has an Open AI API as well incase you want to use that) \
Download it from here: [ollama.com](https://ollama.com/)

Download llama3.1/3.2/3 or any other capable LLM (make sure to change it in the app.py)

and then run `streamlit run app.py`

## License
MIT license

## Todo
- Add groq interface for users who cannot use ollama
