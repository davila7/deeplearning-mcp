import streamlit as st
import os
import json
import wikipedia
from typing import List
from dotenv import load_dotenv
import anthropic

# constants
WIKI_DIR = "wiki_articles"

# Tool Functions
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

# Tool Schema
tools = [
    {
        "name": "search_articles",
        "description": "Search for articles on Wikipedia based on a topic and store their information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The topic to search for"
                }, 
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to retrieve",
                    "default": 5
                }
            },
            "required": ["topic"]
        }
    },
    {
        "name": "extract_info",
        "description": "Search for information about a specific article across all topic directories.",
        "input_schema": {
            "type": "object",
            "properties": {
                "article_title": {
                    "type": "string",
                    "description": "The title of the article to look for"
                }
            },
            "required": ["article_title"]
        }
    },
    {
        "name": "get_article_content",
        "description": "Get the full content of a Wikipedia article.",
        "input_schema": {
            "type": "object",
            "properties": {
                "article_title": {
                    "type": "string",
                    "description": "The title of the article to retrieve"
                }
            },
            "required": ["article_title"]
        }
    }
]

# Tool Mapping
mapping_tool_function = {
    "search_articles": search_articles,
    "extract_info": extract_info,
    "get_article_content": get_article_content
}

def execute_tool(tool_name, tool_args):
    
    result = mapping_tool_function[tool_name](**tool_args)

    if result is None:
        result = "The operation completed but didn't return any results."
        
    elif isinstance(result, list):
        result = ', '.join(result)
        
    elif isinstance(result, dict):
        # Convert dictionaries to formatted JSON strings
        result = json.dumps(result, indent=2)
    
    else:
        # For any other type, convert using str()
        result = str(result)
    return result

# Load environment variables
load_dotenv()

# Initialize the Anthropic client
client = anthropic.Anthropic()

# Define the chat function
def process_query(query):
    # Inicializar o recuperar el historial de chat
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Agregar la consulta del usuario al historial
    st.session_state.messages.append({'role': 'user', 'content': query})
    
    # Mostrar la consulta del usuario en la interfaz
    with st.chat_message("user"):
        st.write(query)
    
    # Preparar mensajes para la API
    api_messages = [{'role': m['role'], 'content': m['content']} for m in st.session_state.messages]
    
    # Llamar a la API de Anthropic
    response = client.messages.create(
        max_tokens=2024,
        model='claude-3-7-sonnet-20250219',
        tools=tools,
        messages=api_messages
    )
    
    process_query = True
    while process_query:
        assistant_content = []

        for content in response.content:
            if content.type == 'text':
                # Mostrar el texto de respuesta
                with st.chat_message("assistant"):
                    st.write(content.text)
                
                assistant_content.append(content)
                
                # Guardar la respuesta en el historial
                if len(response.content) == 1:
                    st.session_state.messages.append({'role': 'assistant', 'content': content.text})
                    process_query = False

            elif content.type == 'tool_use':
                assistant_content.append(content)
                
                tool_id = content.id
                tool_args = content.input
                tool_name = content.name
                
                # Mostrar la llamada a la herramienta en un acordeón
                with st.chat_message("assistant"):
                    with st.expander(f"🛠️ Usando herramienta: {tool_name}", expanded=False):
                        st.json(tool_args)
                        
                        # Ejecutar la herramienta y mostrar el resultado
                        result = execute_tool(tool_name, tool_args)
                        st.markdown("### Resultado:")
                        if tool_name == "get_article_content":
                            st.markdown(result)
                        else:
                            try:
                                # Intentar formatear como JSON si es posible
                                st.json(json.loads(result))
                            except:
                                st.markdown(result)
                
                # Actualizar los mensajes para la API
                api_messages.append({'role': 'assistant', 'content': assistant_content})
                api_messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": result
                        }
                    ]
                })
                
                # Llamar nuevamente a la API con el resultado de la herramienta
                response = client.messages.create(
                    max_tokens=2024,
                    model='claude-3-7-sonnet-20250219',
                    tools=tools,
                    messages=api_messages
                )
                
                if len(response.content) == 1 and response.content[0].type == "text":
                    with st.chat_message("assistant"):
                        st.write(response.content[0].text)
                    
                    st.session_state.messages.append({'role': 'assistant', 'content': response.content[0].text})
                    process_query = False

# Streamlit app
st.title("Chatbot de Wikipedia con Streamlit")

st.write("Escribe tus consultas abajo:")

# Inicializar el historial de chat si no existe
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Mostrar el historial de chat
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.write(message['content'])

# Campo de entrada para la consulta
query = st.chat_input("Escribe tu consulta aquí")

if query:
    process_query(query)
