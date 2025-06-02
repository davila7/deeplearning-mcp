import wikipedia
from typing import List
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Wikipedia MCP", host="0.0.0.0", port=8000)

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
    print("call search_article")
    # Use Wikipedia to find articles
    search_results = wikipedia.search(topic, results=max_results)
    
    # Process each article and add to articles_info  
    article_titles = []
    for title in search_results:
        article_titles.append(title)
        
    return article_titles

@mcp.tool()
def get_article_content(article_title: str) -> str:
    """
    Get the full content of a Wikipedia article.
    
    Args:
        article_title: The title of the article to retrieve
        
    Returns:
        String with article content if found, error message if not found
    """
    print("call get_article_content")
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
    mcp.run(transport="sse")
    #mcp.run(transport='stdio')