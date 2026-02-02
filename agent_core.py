import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage, HumanMessage, AIMessage, SystemMessage

# Import the search function from your existing search_tool.py
from search_tool import search_kg 

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = api_key 
os.environ["GEMINI_API_KEY"] = api_key

@tool
def knowledge_graph_search(entity_name: str) -> str:
    """
    Searches the Knowledge Graph (Neo4j) for all one-hop connections 
    (relations and neighboring entities) from the given entity name.
    """
    results = search_kg(entity_name)
    if not results:
        return f"No direct outgoing connections found for: {entity_name}."
    
    return "\n".join([f"- {res['relation']} -> {res['neighbor']} ({res['neighbor_type']})" for res in results])

@tool
def knowledge_generator(entity_name: str, desired_relation: str) -> str:
    """
    Used to hypothesize a missing fact when the database has no data.
    """
    return f"Hypothesized: {entity_name} has relation {desired_relation}."


PLANNER_PROMPT = (
    "You are the Planner. Analyze the question and decide the next step.\n"
    "1. To search, say: 'INSTRUCTION: PERFORM SEARCH for entity [Name]'.\n"
    "2. To hypothesize missing data, use 'knowledge_generator'.\n"
    "3. When finished, say: 'FINAL ANSWER: [Your Answer]'."
)

EXECUTOR_PROMPT = "You are the Executor. If told to search, use 'knowledge_graph_search' immediately."

def parse_content(content):
    """Ensures content is a string even if the API returns a list of parts."""
    if isinstance(content, str): return content
    if isinstance(content, list):
        return "".join([p.get("text", "") if isinstance(p, dict) else str(p) for p in content])
    return str(content)


def run_dual_agent(question: str, max_steps: int = 8):
    print(f"--- Starting Dual-Agent System ---")

    MODEL_NAME = "gemini-2.0-flash" 
    
    try:
        llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0)
        planner_llm = llm.bind_tools([knowledge_generator])
        executor_llm = llm.bind_tools([knowledge_graph_search])
    except Exception as e:
        print(f"Error initializing model: {e}")
        return

    kg_memory = []
    messages = [SystemMessage(content=PLANNER_PROMPT), HumanMessage(content=question)]

    for step in range(max_steps):
        print(f"\n> Step {step + 1}: Planner's Turn...")
        
        # Add memory context
        mem_str = f"\n[Memory: {'; '.join(kg_memory)}]" if kg_memory else ""
        try:
            planner_response = planner_llm.invoke(messages + [HumanMessage(content=mem_str)])
        except Exception as e:
            print(f"API Call Failed: {e}")
            break

        content_text = parse_content(planner_response.content)

        # Check for Tool Calls (Knowledge Generation)
        if planner_response.tool_calls:
            for tc in planner_response.tool_calls:
                if tc['name'] == "knowledge_generator":
                    print(f"   Planner: Hypothesizing missing data...")
                    res = knowledge_generator.invoke(tc['args'])
                    kg_memory.append(res)
                    messages.append(planner_response)
                    messages.append(ToolMessage(content=res, tool_call_id=tc['id']))
            continue

        # Check for Search Instruction
        if "INSTRUCTION: PERFORM SEARCH" in content_text:
            try:
                entity = content_text.split("entity")[1].strip(" :.[]")
                print(f"   Planner Instruction: Search for '{entity}'")
                
                exec_msg = [SystemMessage(content=EXECUTOR_PROMPT), HumanMessage(content=f"PERFORM SEARCH for entity {entity}")]
                exec_resp = executor_llm.invoke(exec_msg)
                
                if exec_resp.tool_calls:
                    search_res = knowledge_graph_search.invoke(exec_resp.tool_calls[0]['args'])
                    messages.append(AIMessage(content=f"Search Results for {entity}:\n{search_res}"))
                    print(f"   Executor: Found {len(search_res.splitlines())} connections.")
            except Exception as e:
                print(f"   Error in Executor step: {e}")
            continue

        # Check for Final Answer
        if "FINAL ANSWER:" in content_text:
            print(f"\n✅ {content_text}")
            return content_text

    print("\n Loop ended without final answer.")

if __name__ == "__main__":
    run_dual_agent("What movie did both Tom Hanks and Keanu Reeves act in?")