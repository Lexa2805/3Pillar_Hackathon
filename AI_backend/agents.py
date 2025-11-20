"""
Multi-Agent System using LangGraph and OpenRouter
"""
import os
from typing import TypedDict, Annotated, Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from vector_utils import chunk_and_embed_text, prepare_vector_document
from web_search import search_for_context, is_web_search_enabled

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


class AgentState(TypedDict):
    """State that gets passed between agents"""
    user_prompt: str
    idea_response: str
    critic_response: str
    builder_response: str
    current_agent: str
    idea_chunks: List[Dict[str, Any]]
    critic_chunks: List[Dict[str, Any]]
    builder_chunks: List[Dict[str, Any]]


def create_openrouter_llm(model: str = "openai/gpt-4o-mini"):
    """Create an OpenRouter-compatible LLM instance"""
    return ChatOpenAI(
        model=model,
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.7,
    )


def idea_agent(state: AgentState) -> AgentState:
    """
    Idea Agent: Generates creative ideas based on user prompt
    Enhanced with web search for current information
    """
    llm = create_openrouter_llm()
    
    system_message = SystemMessage(content="""You are an Idea Agent specialized in creative brainstorming.
Your role is to generate 3-5 innovative and practical ideas based on the user's prompt.
Be creative, think outside the box, but keep ideas feasible and actionable.
If web search results are provided, use them to inform your ideas with current trends and information.
Format your response as a numbered list with brief descriptions for each idea.""")
    
    # Enhance prompt with web search if enabled
    user_content = state["user_prompt"]
    if is_web_search_enabled():
        print(f"🔍 Searching web for: {state['user_prompt'][:100]}...")
        search_context = search_for_context(state["user_prompt"], max_results=3)
        if search_context and "No web search results" not in search_context:
            user_content = f"{state['user_prompt']}\n\nContext from web search:\n{search_context}"
            print("✅ Web search completed - enhanced prompt with current information")
    
    human_message = HumanMessage(content=user_content)
    
    response = llm.invoke([system_message, human_message])
    
    state["idea_response"] = response.content
    state["current_agent"] = "idea"
    
    return state


def critic_agent(state: AgentState) -> AgentState:
    """
    Critic Agent: Evaluates ideas and points out weaknesses
    """
    llm = create_openrouter_llm()
    
    system_message = SystemMessage(content="""You are a Critic Agent specialized in critical analysis.
Your role is to evaluate the ideas provided and point out potential risks, weaknesses, and challenges.
Be constructive but thorough in identifying problems. Consider feasibility, market fit, technical challenges, and potential pitfalls.
Format your response with clear critique points for each idea.""")
    
    human_message = HumanMessage(content=f"""User Prompt: {state['user_prompt']}

Ideas Generated:
{state['idea_response']}

Please provide critical analysis of these ideas.""")
    
    response = llm.invoke([system_message, human_message])
    
    state["critic_response"] = response.content
    state["current_agent"] = "critic"
    
    return state


def builder_agent(state: AgentState) -> AgentState:
    """
    Builder Agent: Improves ideas based on critiques
    """
    llm = create_openrouter_llm()
    
    system_message = SystemMessage(content="""You are a Builder Agent specialized in improvement and problem-solving.
Your role is to take the ideas and criticisms and propose concrete improvements and solutions.
Address the weaknesses pointed out by the Critic and enhance the original ideas.
Be practical and provide actionable next steps.""")
    
    human_message = HumanMessage(content=f"""User Prompt: {state['user_prompt']}

Original Ideas:
{state['idea_response']}

Critiques:
{state['critic_response']}

Please provide improved versions of the ideas with solutions to the identified problems.""")
    
    response = llm.invoke([system_message, human_message])
    
    state["builder_response"] = response.content
    state["current_agent"] = "builder"
    
    return state


def create_agent_graph():
    """
    Create the LangGraph workflow for multi-agent collaboration
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes for each agent
    workflow.add_node("idea", idea_agent)
    workflow.add_node("critic", critic_agent)
    workflow.add_node("builder", builder_agent)
    
    # Define the flow
    workflow.set_entry_point("idea")
    workflow.add_edge("idea", "critic")
    workflow.add_edge("critic", "builder")
    workflow.add_edge("builder", END)
    
    return workflow.compile()


# Create a single instance of the graph
agent_graph = create_agent_graph()


async def run_idea_agent_only(user_prompt: str, session_id: str = None) -> dict:
    """
    Run only the Idea Agent and return its response with chunks and embeddings
    """
    initial_state = AgentState(
        user_prompt=user_prompt,
        idea_response="",
        critic_response="",
        builder_response="",
        current_agent="",
        idea_chunks=[],
        critic_chunks=[],
        builder_chunks=[]
    )
    
    # Run just the idea agent
    result = idea_agent(initial_state)
    
    # Generate chunks and embeddings
    chunks_data = chunk_and_embed_text(
        result["idea_response"],
        metadata={
            "agent": "idea",
            "user_prompt": user_prompt,
            "session_id": session_id
        }
    )
    
    return {
        "agent": "idea",
        "response": result["idea_response"],
        "user_prompt": user_prompt,
        "chunks": chunks_data
    }


async def run_all_agents(user_prompt: str, session_id: str = None) -> dict:
    """
    Run all three agents in sequence and return their responses with chunks and embeddings
    """
    initial_state = AgentState(
        user_prompt=user_prompt,
        idea_response="",
        critic_response="",
        builder_response="",
        current_agent="",
        idea_chunks=[],
        critic_chunks=[],
        builder_chunks=[]
    )
    
    # Run the full graph
    final_state = agent_graph.invoke(initial_state)
    
    # Generate chunks and embeddings for each agent's response
    idea_chunks = chunk_and_embed_text(
        final_state["idea_response"],
        metadata={"agent": "idea", "user_prompt": user_prompt, "session_id": session_id}
    )
    
    critic_chunks = chunk_and_embed_text(
        final_state["critic_response"],
        metadata={"agent": "critic", "user_prompt": user_prompt, "session_id": session_id}
    )
    
    builder_chunks = chunk_and_embed_text(
        final_state["builder_response"],
        metadata={"agent": "builder", "user_prompt": user_prompt, "session_id": session_id}
    )
    
    return {
        "user_prompt": user_prompt,
        "idea_response": final_state["idea_response"],
        "critic_response": final_state["critic_response"],
        "builder_response": final_state["builder_response"],
        "idea_chunks": idea_chunks,
        "critic_chunks": critic_chunks,
        "builder_chunks": builder_chunks
    }
