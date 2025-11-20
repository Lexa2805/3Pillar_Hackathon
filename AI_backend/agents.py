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
    critic_approved: bool  # Whether the critic has approved the idea
    revision_count: int  # Number of times the idea has been revised
    critic_feedback: str  # Feedback from critic for revision
    max_revisions: int  # Maximum number of revision loops allowed


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
    Can revise ideas based on critic feedback
    """
    print("\n" + "="*50)
    print("🤖 IDEA AGENT (Solution Architect) Started")
    if state.get("revision_count", 0) > 0:
        print(f"   🔄 REVISION #{state['revision_count']}")
    print("="*50)
    
    llm = create_openrouter_llm()
    
    # Check if this is a revision based on critic feedback
    if state.get("critic_feedback"):
        print(f"\n🔄 Revising solution based on critic feedback...")
        print(f"   Previous idea length: {len(state.get('idea_response', ''))} chars")
        
        system_message = SystemMessage(content="""You are a Senior Solution Architect at a top tech consultancy. 
You are revising your technical proposal based on feedback from the Technical Review Board.
Your goal is to address ALL the concerns raised while maintaining the core strengths of your original proposal.
Be thorough and specific in addressing each criticism.
Format your response as an improved technical proposal.""")
        
        human_message = HumanMessage(content=f"""User's Original Request: {state['user_prompt']}

Your Previous Proposal:
{state['idea_response']}

Critic's Feedback (MUST ADDRESS):
{state['critic_feedback']}

Please revise your proposal to address all the concerns raised by the critic.""")
        
        print(f"   Sending revision request to GPT-4o...")
        response = llm.invoke([system_message, human_message])
        
        print(f"\n✅ Idea Agent revision completed!")
        print(f"   Revised proposal length: {len(response.content)} characters")
        print(f"   First 200 chars: {response.content[:200]}...")
    else:
        # Initial idea generation with web search
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
    Critic Agent: Reviews the idea and decides if it's acceptable or needs revision
    Can send feedback back to the Idea Agent for improvements
    """
    print("\n" + "="*50)
    print("⚖️ CRITIC AGENT (Review Board) Started")
    if state.get("revision_count", 0) > 0:
        print(f"   🔄 Reviewing REVISION #{state['revision_count']}")
    print("="*50)
    
    llm = create_openrouter_llm()
    
    # For revisions, we already have the solution - skip selection
    if state.get("revision_count", 0) > 0:
        print(f"\n📋 Reviewing revised solution...")
        print(f"   Solution length: {len(state['idea_response'])} chars")
        selected_idea = state['idea_response']
    else:
        # Initial review - select the best solution
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
    
    # Critique and decide if acceptable
    print("\n⚠️ STEP 2: Critic performing technical review...")
    print("   Focus areas: OWASP Top 10, Scalability, GDPR/HIPAA compliance")
    
    critique_system_message = SystemMessage(content="""You are a Strict Technical Review Board member. 
You are an expert in Cybersecurity (OWASP Top 10) and Scalability. 
Your job is to determine if the proposed solution is acceptable or needs revision.

You MUST respond in this exact format:

**DECISION: [APPROVED or NEEDS_REVISION]**

**Selected Solution:**
[The solution being reviewed]

**Technical Review:**
[Your detailed analysis]

**Critical Issues:** (only if NEEDS_REVISION)
- [List specific issues that MUST be addressed]

Be strict but fair. Only approve solutions that properly address security, scalability, and compliance concerns.""")
    
    critique_human_message = HumanMessage(content=f"""User's Original Request: {state['user_prompt']}

Solution to Review:
{selected_idea}

Please provide your technical review and decision (APPROVED or NEEDS_REVISION).""")
    
    print("   Sending critique request to GPT-4o...")
    response = llm.invoke([critique_system_message, critique_human_message])
    
    # Parse the response to determine if approved
    response_text = response.content
    is_approved = "DECISION: APPROVED" in response_text or "DECISION:APPROVED" in response_text
    
    if is_approved:
        print(f"\n✅ CRITIC APPROVED the solution!")
        state["critic_approved"] = True
        state["critic_feedback"] = ""  # Clear feedback on approval
    else:
        print(f"\n❌ CRITIC REJECTED - Requesting revision")
        # Increment revision count here since conditional edges cannot update state
        new_revision_count = state.get('revision_count', 0) + 1
        print(f"   Revision count updated to: {new_revision_count}")
        state["revision_count"] = new_revision_count
        
        state["critic_approved"] = False
        state["critic_feedback"] = response_text
    
    print(f"   Review length: {len(response_text)} characters")
    print(f"   First 200 chars: {response_text[:200]}...")
    
    state["critic_response"] = response_text
    state["current_agent"] = "critic"
    
    return state


def builder_agent(state: AgentState) -> AgentState:
    """
    Builder Agent: Creates actionable tasks based on the approved solution
    Only runs after the Critic has approved the idea
    """
    print("\n" + "="*50)
    print("🔨 BUILDER AGENT (Product Owner) Started")
    print("="*50)
    
    llm = create_openrouter_llm()
    
    system_message = SystemMessage(content="""You are an efficient Technical Product Owner. 
Your job is to take an APPROVED technical architecture and break it down into actionable work. 
You generate clean, formatted User Stories (in Gherkin syntax) and a list of Technical Tasks for the development team.
The solution has already been reviewed and approved by the Technical Review Board.""")
    
    human_message = HumanMessage(content=f"""User Prompt: {state['user_prompt']}

Approved Solution (from Idea Agent):
{state['idea_response']}

Technical Review (APPROVED):
{state['critic_response']}

Please provide the User Stories (Gherkin format) and Technical Tasks for implementation.""")
    
    print("\n📋 Generating User Stories (Gherkin) and Technical Tasks...")
    print(f"   Processing approved solution ({len(state['idea_response'])} chars)")
    print(f"   Including review notes ({len(state['critic_response'])} chars)")
    print("   Expected output: Gherkin-style User Stories + Task breakdown")
    print("   Sending to GPT-4o...")
    response = llm.invoke([system_message, human_message])
    
    print(f"\n✅ Builder Agent completed!")
    print(f"   Output length: {len(response.content)} characters")
    print(f"   First 200 chars: {response.content[:200]}...")
    state["builder_response"] = response.content
    state["current_agent"] = "builder"
    
    return state


def should_continue_to_builder(state: AgentState) -> str:
    """
    Routing function: Decide whether to send back to Idea Agent or proceed to Builder
    Returns: "revise" to loop back to idea_agent, "approve" to proceed to builder
    """
    max_revisions = state.get("max_revisions", 3)
    current_revisions = state.get("revision_count", 0)
    
    # Check if critic approved
    if state.get("critic_approved", False):
        print(f"\n🎯 ROUTING: Critic approved → Proceeding to Builder Agent")
        return "approve"
    
    # Check if we've hit max revisions
    if current_revisions > max_revisions:
        print(f"\n⚠️ ROUTING: Max revisions ({max_revisions}) reached → Forcing approval to Builder")
        print(f"   Note: Solution was not approved but proceeding anyway")
        return "approve"
    
    # Need revision
    print(f"\n🔄 ROUTING: Critic rejected → Sending back to Idea Agent for revision")
    print(f"   Current revisions: {current_revisions}/{max_revisions}")
    return "revise"


def create_agent_graph():
    """
    Create the LangGraph workflow with feedback loop
    Flow: Idea → Critic → [If approved: Builder, If not: back to Idea] → END
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes for each agent
    workflow.add_node("idea", idea_agent)
    workflow.add_node("critic", critic_agent)
    workflow.add_node("builder", builder_agent)
    
    # Define the flow with conditional routing
    workflow.set_entry_point("idea")
    workflow.add_edge("idea", "critic")
    
    # Conditional edge: critic can either approve (go to builder) or request revision (go back to idea)
    workflow.add_conditional_edges(
        "critic",
        should_continue_to_builder,
        {
            "approve": "builder",
            "revise": "idea"
        }
    )
    
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
        builder_chunks=[],
        critic_approved=False,
        revision_count=0,
        critic_feedback="",
        max_revisions=3
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


async def run_all_agents(user_prompt: str, session_id: str = None, max_revisions: int = 3) -> dict:
    """
    Run all three agents with feedback loop
    The Critic can send the idea back to the Idea Agent for revision
    
    Args:
        user_prompt: The user's request
        session_id: Optional session identifier
        max_revisions: Maximum number of revision loops (default: 3)
    """
    initial_state = AgentState(
        user_prompt=user_prompt,
        idea_response="",
        critic_response="",
        builder_response="",
        current_agent="",
        idea_chunks=[],
        critic_chunks=[],
        builder_chunks=[],
        critic_approved=False,
        revision_count=0,
        critic_feedback="",
        max_revisions=max_revisions
    )
    
    print(f"\n{'='*60}")
    print(f"🚀 STARTING AGENT WORKFLOW")
    print(f"   Max revisions allowed: {max_revisions}")
    print(f"{'='*60}")
    
    # Run the full graph with feedback loop
    final_state = agent_graph.invoke(initial_state)
    
    print(f"\n{'='*60}")
    print(f"🏁 WORKFLOW COMPLETED")
    print(f"   Total revisions: {final_state.get('revision_count', 0)}")
    print(f"   Critic approved: {final_state.get('critic_approved', False)}")
    print(f"{'='*60}\n")
    
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
        "builder_chunks": builder_chunks,
        "revision_count": final_state.get("revision_count", 0),
        "critic_approved": final_state.get("critic_approved", False)
    }


async def run_single_agent_chat(agent_type: str, user_prompt: str, context: List[Dict[str, str]], session_id: str = None) -> dict:
    """
    Run a specific agent in a chat context.
    
    Args:
        agent_type: 'idea', 'critic', or 'builder'
        user_prompt: The user's new message
        context: List of previous messages [{"role": "user/assistant", "content": "..."}]
        session_id: Optional session ID
    """
    llm = create_openrouter_llm()
    
    # Define system prompts for each persona
    system_prompts = {
        "idea": """You are the Idea Agent (Solution Architect). 
You are creative, innovative, and knowledgeable about technical architectures.
You help users brainstorm solutions, explore options, and design systems.
Use the conversation context to inform your responses.""",

        "critic": """You are the Critic Agent (Technical Review Board).
You are strict, security-conscious, and focused on scalability and compliance (OWASP, GDPR, etc.).
You review ideas, point out flaws, and suggest improvements.
Use the conversation context to understand what is being discussed.""",

        "builder": """You are the Builder Agent (Product Owner).
You are practical, organized, and focused on implementation details.
You turn ideas into user stories, tasks, and execution plans.
Use the conversation context to understand the project requirements."""
    }
    
    system_message = SystemMessage(content=system_prompts.get(agent_type, "You are a helpful AI assistant."))
    
    # Build message history
    messages = [system_message]
    
    # Add context messages
    for msg in context:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            # Map agent names to AI responses
            messages.append(SystemMessage(content=f"[{msg['role'].upper()}]: {msg['content']}"))
            
    # Add current prompt
    messages.append(HumanMessage(content=user_prompt))
    
    # Run LLM
    response = llm.invoke(messages)
    
    # Generate chunks for the response
    chunks_data = chunk_and_embed_text(
        response.content,
        metadata={
            "agent": agent_type,
            "user_prompt": user_prompt,
            "session_id": session_id,
            "type": "chat_response"
        }
    )
    
    return {
        "agent": agent_type,
        "response": response.content,
        "chunks": chunks_data
    }
