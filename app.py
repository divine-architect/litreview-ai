# MIT License
# 
# Copyright (c) 2024 Sachit Ramesha Gowda
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import streamlit as st
from googlesearch import search
from ollama import chat
from datetime import datetime
import requests
from newspaper import Article
import time

def clean_text(text):
    """Clean and format extracted text."""
    if not text:
        return ""
    
    cleaned = ' '.join(text.split())
    return cleaned

def get_page_content(url):
    """Fetch and extract content from a webpage using newspaper3k."""
    try:
     
        article = Article(url)
        
        
        article.download()
        article.parse()
        
       
        try:
            article.nlp()
            summary = article.summary
        except:
            summary = ""
        
        # Get title and content; fall back to summary if article text is unavailable
        title = article.title if article.title else url
        content = summary if summary else article.text
        
        # Handle cases where content might be inaccessible
        if not title and not content:
            return {
                'title': url,
                'body': "Content not accessible - might be a PDF or protected content",
                'link': url
            }
        
        return {
            'title': clean_text(title),
            'body': clean_text(content[:1500]),  # Truncate content to avoid overly long previews
            'link': url
        }
    except Exception as e:
        # Graceful error handling for issues in content extraction
        return {
            'title': url,
            'body': f"Error extracting content: {str(e)}",
            'link': url
        }

def search_papers(query, max_results=10, search_domains=None):
    """Search for academic papers and articles using Google Search."""
    if not search_domains:
        # default
        search_domains = ["arxiv.org", "scholar.google.com"]
    
    
    domain_query = " OR ".join(f"site:{domain}" for domain in search_domains)
    academic_query = f"{query} (research OR paper OR study OR journal) ({domain_query})"
    
    try:
        results = []
        for url in search(academic_query, num_results=max_results):
           
            paper_info = get_page_content(url)
            if paper_info['body'] and not paper_info['body'].startswith("Error extracting content"):
                results.append(paper_info)
            # ratelimit lel
            time.sleep(2)
        return results
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return []

def analyze_paper(paper_info):
    """Use AI to analyze the paper information."""
    prompt = f"""
    Please analyze this research paper/article and provide:
    1. Key findings
    2. Main methodology
    3. Potential relevance to the research topic
    
    Paper Title: {paper_info['title']}
    Paper Link: {paper_info['link']}
    Description: {paper_info['body']}
    
    Please be concise and focus on the most important points.
    If the content is not accessible or unclear, please indicate that in your analysis.
    """
    
    try:
       
        response = chat(model='llama3.1', messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        return response['message']['content']
    except Exception as e:
        
        print(str(e))
        return f"Analysis error: {str(e)}"

def generate_markdown(papers_data, search_query):
    """Generate markdown formatted content from papers data."""
    markdown_content = f"""# Literature Review Results
## Search Query: {search_query}
*Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

"""
    for idx, paper in enumerate(papers_data, 1):
        markdown_content += f"""
## {idx}. {paper['title']}

**Link:** {paper['link']}

**Description:**
{paper['body']}

**AI Analysis:**
{paper['analysis']}

---
"""
    return markdown_content

def main():
    st.set_page_config(
        page_title="AI Literature Review Assistant",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 AI-Powered Literature Review Assistant")
    
    # Sidebar settings
    st.sidebar.title("⚙️ Search Settings")
    max_results = st.sidebar.slider("Maximum number of papers:", 1, 35, 5)
    search_domains = st.sidebar.multiselect(
        "Select search domains:",
        ["arxiv.org", "scholar.google.com", "researchgate.net", "sciencedirect.com", "ieee.org", "springer.com"],
        default=["arxiv.org", "scholar.google.com"]
    )
    
    st.markdown("""
    Enter your research topic below. The assistant will:
    1. Search for relevant academic papers
    2. Extract and analyze their content
    3. Generate a comprehensive review
    """)
    
    search_query = st.text_input("🔍 Enter your research topic:")
    
    if st.button("🚀 Search and Analyze"):
        if search_query:
            with st.spinner("🔍 Searching for papers..."):
                papers = search_papers(search_query, max_results, search_domains)
                
                if papers:
                    # Show progress during paper analysis
                    progress_container = st.empty()
                    progress_bar = st.progress(0)
                    
                    papers_data = []
                    for i, paper in enumerate(papers):
                        progress = (i + 1) / len(papers)
                        progress_bar.progress(progress)
                        progress_container.text(f"📑 Analyzing paper {i+1} of {len(papers)}")
                        
                        analysis = analyze_paper(paper)
                        papers_data.append({
                            'title': paper['title'],
                            'link': paper['link'],
                            'body': paper['body'],
                            'analysis': analysis
                        })
                    
                    # Clear progress indicators after analysis
                    progress_container.empty()
                    progress_bar.empty()
                    
                    markdown_content = generate_markdown(papers_data, search_query)
                    
                    st.subheader("📋 Literature Review Results")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            label="📥 Download as Markdown",
                            data=markdown_content,
                            file_name=f"literature_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown"
                        )
                    
                    with col2:
                        st.markdown("""
                            <button 
                                onclick="navigator.clipboard.writeText(document.getElementById('markdown-content').innerText);"
                                style="
                                    background-color: #4CAF50;
                                    border: none;
                                    color: white;
                                    padding: 0.5rem 1rem;
                                    text-align: center;
                                    text-decoration: none;
                                    display: inline-block;
                                    font-size: 16px;
                                    margin: 4px 2px;
                                    cursor: pointer;
                                    border-radius: 4px;">
                                📋 Copy Markdown
                            </button>
                            """, 
                            unsafe_allow_html=True
                        )
                    
                    st.markdown("### 📝 Preview:")
                    st.markdown(markdown_content)
                    
                    st.markdown(f"""
                        <div id="markdown-content" style="display: none;">
                            {markdown_content}
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                else:
                    st.warning("📭 No papers found. Try modifying your search query.")
        else:
            st.warning("⚠️ Please enter a search query.")

if __name__ == "__main__":
    main()
