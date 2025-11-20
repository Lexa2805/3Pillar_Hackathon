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


def create_openrouter_llm(model: str = "openai/gpt-4o"):
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
    print("\n" + "="*50)
    print("🤖 IDEA AGENT (Solution Architect) Started")
    print("="*50)
    
    llm = create_openrouter_llm()
    
    system_message = SystemMessage(content="""You are a Senior Solution Architect at a top tech consultancy. 
Your goal is to design innovative, scalable technical solutions for client problems. 
You rely on past case studies to ensure success. You are creative but practical.
If web search results are provided, use them to inform your designs with current trends and technologies.
Format your response as a technical proposal or a set of architectural options.""")
    
    # Enhance prompt with web search if enabled
    user_content = state["user_prompt"]
    if is_web_search_enabled():
        print(f"\n📡 Idea Agent requesting web search...")
        print(f"   Query: {state['user_prompt'][:100]}...")
        
        # Target technical/architectural sources
        tech_domains = [
            "aws.amazon.com",
            "cloud.google.com", 
            "azure.microsoft.com",
            "github.com",
            "stackoverflow.com",
            "medium.com",
            "dev.to",
            "techcrunch.com"
        ]
        
        search_context = search_for_context(
            state["user_prompt"], 
            max_results=5,
            search_depth="advanced",
            include_domains=tech_domains
        )
        if search_context and "No web search results" not in search_context:
            user_content = f"{state['user_prompt']}\n\nContext from web search:\n{search_context}"
            print("✅ Web search completed - enhanced prompt with current information")
            print(f"   Context length: {len(search_context)} characters")
        else:
            print("⚠️ No web search results found")
    else:
        print("ℹ️ Web search is disabled for Idea Agent")
    
    human_message = HumanMessage(content=user_content)
    
    print("\n💭 Generating architectural solutions...")
    print(f"   Sending {len(user_content)} characters to GPT-4o...")
    response = llm.invoke([system_message, human_message])
    
    print(f"\n✅ Idea Agent completed!")
    print(f"   Response length: {len(response.content)} characters")
    print(f"   First 200 chars: {response.content[:200]}...")
    state["idea_response"] = response.content
    state["current_agent"] = "idea"
    
    return state


def critic_agent(state: AgentState) -> AgentState:
    """
    Critic Agent: Selects the best idea, researches it, and points out weaknesses
    """
    print("\n" + "="*50)
    print("⚖️ CRITIC AGENT (Review Board) Started")
    print("="*50)
    
    llm = create_openrouter_llm()
    
    # Step 1: Select the best idea
    print("\n🤔 STEP 1: Critic is selecting the best solution...")
    print(f"   Analyzing {len(state['idea_response'])} chars from Idea Agent")
    selection_system_message = SystemMessage(content="""You are a Technical Review Board member. 
Your first task is to review the proposed technical solutions and select the single best one based on architectural soundness and scalability.
Return ONLY the text of the selected solution.""")
    
    selection_human_message = HumanMessage(content=f"""User Prompt: {state['user_prompt']}

Ideas Generated:
{state['idea_response']}

Please select the best solution.""")
    
    print("   Sending selection request to GPT-4o...")
    selected_idea_response = llm.invoke([selection_system_message, selection_human_message])
    selected_idea = selected_idea_response.content
    print(f"\n✅ SELECTED SOLUTION:")
    print(f"   {selected_idea[:200]}...")
    print(f"   (Total: {len(selected_idea)} chars)")
    
    # Step 2: Research the selected idea
    search_context = ""
    print("\nℹ️ Critic Agent does NOT search the web - uses only Idea Agent's input")
    
    # Step 3: Critique the selected idea
    print("\n⚠️ STEP 2: Critic analyzing security risks and weaknesses...")
    print("   Focus areas: OWASP Top 10, Scalability, GDPR/HIPAA compliance")
    critique_system_message = SystemMessage(content="""You are a Strict Technical Review Board member. 
You are an expert in Cybersecurity (OWASP Top 10) and Scalability. 
Your job is NOT to be nice; it is to find flaws. 
You critique every proposal for security risks, performance bottlenecks, and missing requirements (like HIPAA or GDPR).
Use the provided web search context to support your critique if available.
Format your response as:
**Selected Solution:**
[The solution you selected]

**Technical Review:**
[Your analysis of security risks, scalability issues, and compliance gaps]""")
    
    critique_human_message = HumanMessage(content=f"""Selected Solution: {selected_idea}

Web Search Context:
{search_context}

Please provide a critical analysis of this solution.""")
    
    print("   Sending critique request to GPT-4o...")
    response = llm.invoke([critique_system_message, critique_human_message])
    
    print(f"\n✅ Critic Agent completed!")
    print(f"   Review length: {len(response.content)} characters")
    print(f"   First 200 chars: {response.content[:200]}...")
    state["critic_response"] = response.content
    state["current_agent"] = "critic"
    
    return state


def builder_agent(state: AgentState) -> AgentState:
    """
    Builder Agent: Improves the selected idea based on critiques
    """
    print("\n" + "="*50)
    print("🔨 BUILDER AGENT (Product Owner) Started")
    print("="*50)
    
    llm = create_openrouter_llm()
    
    system_message = SystemMessage(content="""You are an efficient Technical Product Owner. 
Your job is to take a technical architecture and break it down into actionable work. 
You generate clean, formatted User Stories (in Gherkin syntax) and a list of Technical Tasks for the development team.
Address the issues raised by the Technical Review Board in your stories and tasks.""")
    
    human_message = HumanMessage(content=f"""User Prompt: {state['user_prompt']}

Technical Review:
{state['critic_response']}

Please provide the User Stories and Technical Tasks based on this review.""")
    
    print("\n📋 Generating User Stories (Gherkin) and Technical Tasks...")
    print(f"   Processing {len(state['critic_response'])} chars from Critic review")
    print("   Expected output: Gherkin-style User Stories + Task breakdown")
    print("   Sending to GPT-4o...")
    response = llm.invoke([system_message, human_message])
    
    print(f"\n✅ Builder Agent completed!")
    print(f"   Output length: {len(response.content)} characters")
    print(f"   First 200 chars: {response.content[:200]}...")
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
