import wikipedia
import os
import json
from typing import List
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Wikipedia MCP", host="0.0.0.0", port=8000)

# Directory to store Wikipedia articles
WIKI_DIR = os.path.join(os.path.dirname(__file__), "wiki_articles")

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
    
    # Create topic directory if it doesn't exist
    topic_dir = topic.lower().replace(" ", "_")
    topic_path = os.path.join(WIKI_DIR, topic_dir)
    os.makedirs(topic_path, exist_ok=True)
    
    # Store articles information
    articles_info = {}
    article_titles = []
    
    for title in search_results:
        try:
            page = wikipedia.page(title)
            articles_info[title] = {
                "title": page.title,
                "url": page.url,
                "summary": page.summary[:500] + "..." if len(page.summary) > 500 else page.summary,
                "content_preview": page.content[:1000] + "..." if len(page.content) > 1000 else page.content
            }
            article_titles.append(title)
        except Exception as e:
            print(f"Error processing article '{title}': {str(e)}")
            continue
    
    # Save articles info to JSON file
    articles_file = os.path.join(topic_path, "articles_info.json")
    with open(articles_file, 'w', encoding='utf-8') as f:
        json.dump(articles_info, f, indent=2, ensure_ascii=False)

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
    try:
        page = wikipedia.page(article_title)
        return page.content[:2000] + "..." if len(page.content) > 2000 else page.content
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Disambiguation error: '{article_title}' may refer to multiple articles. Options: {', '.join(e.options[:5])}"
    except wikipedia.exceptions.PageError:
        return f"Page error: No article found with title '{article_title}'"
    except Exception as e:
        return f"Error retrieving article: {str(e)}"

@mcp.resource("wiki://topics")
def get_available_topics() -> str:
    """
    List all available topic folders in the wiki_articles directory.
    
    This resource provides a simple list of all available topic folders.
    """
    topics = []
    
    # Get all topic directories
    if os.path.exists(WIKI_DIR):
        for topic_dir in os.listdir(WIKI_DIR):
            topic_path = os.path.join(WIKI_DIR, topic_dir)
            if os.path.isdir(topic_path):
                articles_file = os.path.join(topic_path, "articles_info.json")
                if os.path.exists(articles_file):
                    topics.append(topic_dir)
    
    # Create a simple markdown list
    content = "# Available Wikipedia Topics\n\n"
    if topics:
        for topic in topics:
            content += f"- {topic.replace('_', ' ').title()}\n"
        content += f"\nUse wiki://<topic> to access articles in that topic.\n"
    else:
        content += "No topics found. Search for articles first to create topics.\n"
    
    return content

@mcp.resource("wiki://{topic}")
def get_topic_articles(topic: str) -> str:
    """
    Get detailed information about Wikipedia articles on a specific topic.
    
    Args:
        topic: The topic to retrieve articles for
    """
    topic_dir = topic.lower().replace(" ", "_")
    articles_file = os.path.join(WIKI_DIR, topic_dir, "articles_info.json")
    
    if not os.path.exists(articles_file):
        return f"# No articles found for topic: {topic}\n\nTry searching for articles on this topic first."
    
    try:
        with open(articles_file, 'r', encoding='utf-8') as f:
            articles_data = json.load(f)
        
        # Create markdown content with article details
        content = f"# Wikipedia Articles on {topic.replace('_', ' ').title()}\n\n"
        content += f"Total articles: {len(articles_data)}\n\n"
        
        for article_title, article_info in articles_data.items():
            content += f"## {article_info['title']}\n"
            content += f"- **URL**: [{article_info['url']}]({article_info['url']})\n\n"
            content += f"### Summary\n{article_info['summary']}\n\n"
            content += f"### Content Preview\n{article_info['content_preview']}\n\n"
            content += "---\n\n"
        
        return content
    except json.JSONDecodeError:
        return f"# Error reading articles data for {topic}\n\nThe articles data file is corrupted."
    except Exception as e:
        return f"# Error accessing articles for {topic}\n\n{str(e)}"
    
@mcp.prompt()
def generate_wiki_game_prompt(topic: str, difficulty: str = "medium") -> str:
    """Generate a prompt for Claude to create a Hidden Word Wiki game using Wikipedia articles."""
    return f"""Create an interactive "Hidden Word Wiki" game based on Wikipedia articles about '{topic}'. 

**IMPORTANT: Use an artifact to create a complete, standalone HTML file with embedded CSS and JavaScript.**

Follow these steps:

1. **Search Phase:**
   - Use search_articles(topic='{topic}', max_results=3) to find Wikipedia articles
   - Use get_article_content() to get detailed content from the most relevant article

2. **Game Setup:**
   - Extract 5-8 key terms from the Wikipedia article (difficulty: {difficulty})
   - For {difficulty} difficulty:
     * Easy: 4-6 letter common terms
     * Medium: 6-8 letter specialized terms  
     * Hard: 8+ letter technical/scientific terms

3. **Create Interactive Game:**
   **Create a single HTML artifact containing:**
   - Complete HTML structure
   - Embedded CSS styling (in <style> tags)
   - Embedded JavaScript functionality (in <script> tags)
   - No external dependencies

4. **Game Features to Include:**
   - Game title: "Hidden Word Wiki: {topic}"
   - Word display with blanks (e.g., "_ _ _ _ _ _")
   - Interactive alphabet buttons for letter guessing
   - Hint system showing Wikipedia-based definitions
   - Score tracking (correct/incorrect guesses)
   - Lives counter (6 wrong guesses = game over)
   - "New Word" button to cycle through terms
   - "Show Hint" button revealing Wikipedia context
   - Visual feedback for correct/incorrect guesses
   - Win/lose animations and messages

5. **Technical Requirements:**
   - **Self-contained**: All code in one HTML file
   - **Responsive design**: Works on mobile and desktop
   - **Modern styling**: Clean, engaging UI with CSS animations
   - **Game state management**: Proper tracking of progress
   - **Accessibility**: Keyboard navigation and screen reader support
   - **No external libraries**: Pure HTML/CSS/JavaScript only

6. **Content Guidelines:**
   - All definitions sourced from Wikipedia article
   - Include attribution to Wikipedia
   - Educational context for each term
   - Terms relevant to '{topic}'

**Output the complete game as a single HTML artifact that can be opened directly in a browser.**

Make it engaging, educational, and fully functional with smooth animations and clear visual feedback."""


if __name__ == "__main__":
    # Initialize and run the server
    print('Starting server.-------')
    mcp.run(transport='sse')