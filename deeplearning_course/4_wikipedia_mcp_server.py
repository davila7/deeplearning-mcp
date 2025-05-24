import wikipedia
import json
import os
from typing import List
from mcp.server.fastmcp import FastMCP

# constants
WIKI_DIR = "wiki_articles"

# Initialize FastMCP server
mcp = FastMCP("research")

@mcp.tool()
def search_articles(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for articles on Wikipedia based on a topic and store their information.
    
    Args:
        topic: The topic to search for
        max_results: Maximum number of results to retrieve (default: 5)
        
    Returns:
        List of article titles found in the search
    """
    
    # Use Wikipedia to find articles
    search_results = wikipedia.search(topic, results=max_results)
    
    # Create directory for this topic
    path = os.path.join(WIKI_DIR, topic.lower().replace(" ", "_"))
    os.makedirs(path, exist_ok=True)
    
    file_path = os.path.join(path, "articles_info.json")

    # Try to load existing articles info
    try:
        with open(file_path, "r") as json_file:
            articles_info = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        articles_info = {}

    # Process each article and add to articles_info  
    article_titles = []
    for title in search_results:
        try:
            # Get the Wikipedia page
            page = wikipedia.page(title)
            
            article_titles.append(title)
            article_info = {
                'title': page.title,
                'summary': page.summary,
                'url': page.url,
                'content_length': len(page.content)
            }
            articles_info[title] = article_info
            
        except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError) as e:
            # Handle disambiguation or page not found errors
            if isinstance(e, wikipedia.exceptions.DisambiguationError):
                article_info = {
                    'title': title,
                    'error': 'disambiguation',
                    'options': e.options[:5]  # Store first 5 options
                }
            else:
                article_info = {
                    'title': title,
                    'error': 'page_not_found'
                }
            articles_info[title] = article_info
    
    # Save updated articles_info to json file
    with open(file_path, "w") as json_file:
        json.dump(articles_info, json_file, indent=2)
    
    print(f"Results are saved in: {file_path}")
    
    return article_titles

@mcp.tool()
def extract_info(article_title: str) -> str:
    """
    Search for information about a specific article across all topic directories.
    
    Args:
        article_title: The title of the article to look for
        
    Returns:
        JSON string with article information if found, error message if not found
    """
 
    for item in os.listdir(WIKI_DIR):
        item_path = os.path.join(WIKI_DIR, item)
        if os.path.isdir(item_path):
            file_path = os.path.join(item_path, "articles_info.json")
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r") as json_file:
                        articles_info = json.load(json_file)
                        if article_title in articles_info:
                            return json.dumps(articles_info[article_title], indent=2)
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    print(f"Error reading {file_path}: {str(e)}")
                    continue
    
    return f"There's no saved information related to article '{article_title}'."

@mcp.tool()
def get_article_content(article_title: str) -> str:
    """
    Get the full content of a Wikipedia article.
    
    Args:
        article_title: The title of the article to retrieve
        
    Returns:
        String with article content if found, error message if not found
    """
    try:
        page = wikipedia.page(article_title)
        return page.content[:2000] + "..." if len(page.content) > 2000 else page.content
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Disambiguation error: '{article_title}' may refer to multiple articles. Options: {', '.join(e.options[:5])}"
    except wikipedia.exceptions.PageError:
        return f"Page error: No article found with title '{article_title}'"
    except Exception as e:
        return f"Error retrieving article: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')