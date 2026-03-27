"""
Agent-based review analysis using LangChain ReAct agent with tools.
Replaces the old Ollama/LLaMA3 approach with a proper tool-using agent.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


# ── LLM factory (lazy - no network calls at import time) ─────────────────────
def _get_llm():
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    if groq_key:
        from langchain_groq import ChatGroq
        return ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2, api_key=groq_key)
    if openai_key:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o-mini", temperature=0.2, api_key=openai_key)
    raise EnvironmentError(
        "No LLM API key found. Set GROQ_API_KEY (free at console.groq.com) or OPENAI_API_KEY."
    )


def generate_components_ai(product: str) -> List[str]:
    """
    Simple AI component generation function.
    Can be used directly in the pipeline without LangChain complexity.
    """
    try:
        # Load environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
        except ImportError:
            pass
        
        groq_key = os.getenv("GROQ_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if groq_key:
            # Use Groq
            from groq import Groq
            client = Groq(api_key=groq_key)
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{
                    "role": "user",
                    "content": f"You are a product engineer. List the physical components of: {product}. Return comma separated list only. Do not include performance metrics."
                }]
            )
            text = response.choices[0].message.content
            
        elif openai_key:
            # Use OpenAI
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user", 
                    "content": f"You are a product engineer. List the physical components of: {product}. Return comma separated list only. Do not include performance metrics."
                }]
            )
            text = response.choices[0].message.content
            
        else:
            # No API key available
            logger.warning("No API key for AI component generation")
            return ["body", "parts", "components", "materials", "structure"]
        
        # Process the response
        components = [x.strip().lower() for x in text.split(",") if x.strip()]
        
        # Clean and filter
        filtered_components = []
        skip_words = {"etc", "and", "with", "including", "such as", "various", "multiple", "features", "specifications"}
        
        for comp in components:
            if not any(skip in comp for skip in skip_words) and len(comp) > 1:
                filtered_components.append(comp)
        
        return filtered_components[:10]  # Limit to 10 components
        
    except Exception as e:
        logger.error(f"AI component generation failed: {e}")
        return ["body", "parts", "components", "materials", "structure"]


# ── Agent Tools (pure Python, no LLM needed) ─────────────────────────────────
def _tool_generate_components(product: str) -> str:
    """
    Generate components using AI based on product name.
    This replaces the knowledge base approach with dynamic AI generation.
    """
    try:
        llm = _get_llm()
        from langchain_core.messages import HumanMessage
        
        prompt = f"""You are a product engineer.

List the physical components of: {product}

Return comma separated list only.
Do not include performance metrics or features.
Only include tangible physical parts."""
        
        response = llm.invoke([HumanMessage(content=prompt)])
        components_text = response.content.strip()
        
        # Clean and split components
        components = [c.strip().lower() for c in components_text.split(",") if c.strip()]
        
        # Remove any common non-component words
        filtered_components = []
        skip_words = {"etc", "and", "with", "including", "such as", "various", "multiple"}
        
        for comp in components:
            if not any(skip in comp for skip in skip_words) and len(comp) > 1:
                filtered_components.append(comp)
        
        return json.dumps({"components": filtered_components[:10]})  # Limit to 10 components
        
    except Exception as e:
        logger.error(f"AI component generation failed: {e}")
        # Fallback to generic components
        fallback = ["body", "parts", "components", "materials", "structure"]
        return json.dumps({"components": fallback})


def _tool_summarize_component(input_str: str) -> str:
    try:
        data = json.loads(input_str)
        component = data.get("component", "unknown")
        reviews = data.get("reviews", [])
        if not reviews:
            return f"No reviews found for component: {component}"
        combined = " | ".join(reviews[:10])
        return f"Component '{component}' has {len(reviews)} reviews. Sample: {combined[:800]}"
    except Exception as e:
        return f"Error: {e}"


def _tool_sentiment_score(input_str: str) -> str:
    try:
        reviews = json.loads(input_str) if input_str.strip().startswith("[") else [input_str]
        pos_words = {"good","great","excellent","amazing","love","perfect","best","awesome",
                     "fantastic","happy","satisfied","recommend","quality","fast","easy",
                     "comfortable","durable","value","worth","nice","solid","reliable"}
        neg_words = {"bad","poor","terrible","awful","worst","hate","broken","defective",
                     "cheap","slow","difficult","uncomfortable","fragile","overpriced",
                     "waste","disappointed","return","refund","issue","problem","fail",
                     "horrible","useless","flimsy","disappointing"}
        pos = neg = 0
        for r in reviews:
            words = set(r.lower().split())
            pos += len(words & pos_words)
            neg += len(words & neg_words)
        total = pos + neg
        score = round((pos - neg) / total, 3) if total > 0 else 0.0
        label = "POSITIVE" if score > 0.1 else ("NEGATIVE" if score < -0.1 else "NEUTRAL")
        return json.dumps({"score": score, "label": label, "positive_signals": pos, "negative_signals": neg})
    except Exception as e:
        return f"Error: {e}"


def _tool_compare_products(input_str: str) -> str:
    try:
        data = json.loads(input_str)
        component = data.get("component", "general")
        products = data.get("products", {})
        pos_words = {"good","great","excellent","amazing","love","perfect","best","awesome",
                     "fantastic","happy","satisfied","quality","fast","easy","comfortable",
                     "durable","value","worth","nice","solid","reliable"}
        neg_words = {"bad","poor","terrible","awful","worst","hate","broken","defective",
                     "cheap","slow","difficult","uncomfortable","fragile","overpriced",
                     "waste","disappointed","issue","problem","fail","horrible","useless"}
        results = {}
        for name, reviews in products.items():
            pos = neg = 0
            for r in reviews:
                words = set(r.lower().split())
                pos += len(words & pos_words)
                neg += len(words & neg_words)
            total = pos + neg
            results[name] = round((pos - neg) / total, 3) if total > 0 else 0.0
        ranked = sorted(results.items(), key=lambda x: x[1], reverse=True)
        winner = ranked[0][0] if ranked else "N/A"
        return json.dumps({"component": component, "rankings": ranked, "winner": winner})
    except Exception as e:
        return f"Error: {e}"


def _tool_extract_complaints(input_str: str) -> str:
    try:
        reviews = json.loads(input_str) if input_str.strip().startswith("[") else [input_str]
        complaint_keywords = [
            "battery drain","slow","lag","freeze","crash","poor quality","bad sound",
            "uncomfortable","too small","too large","cheap","broke","defective",
            "overpriced","not worth","hard to assemble","difficult","confusing",
            "bad smell","faded","shrink","loose","tight","scratched","damaged",
            "stopped working","fell apart","peeling","blurry","noisy"
        ]
        counts: Dict[str, int] = {}
        for review in reviews:
            r_lower = review.lower()
            for kw in complaint_keywords:
                if kw in r_lower:
                    counts[kw] = counts.get(kw, 0) + 1
        top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return json.dumps({"top_complaints": top, "total_reviews_analyzed": len(reviews)})
    except Exception as e:
        return f"Error: {e}"


def _build_tools():
    from langchain.tools import Tool
    return [
        Tool(name="SummarizeComponent", func=_tool_summarize_component,
             description="Summarize reviews for a component. Input: JSON with 'component' and 'reviews' keys."),
        Tool(name="SentimentScore", func=_tool_sentiment_score,
             description="Calculate sentiment score for reviews. Input: JSON array of review strings."),
        Tool(name="CompareProducts", func=_tool_compare_products,
             description="Compare products on a component. Input: JSON with 'component' and 'products' (dict of product->reviews)."),
        Tool(name="ExtractComplaints", func=_tool_extract_complaints,
             description="Extract top complaints from reviews. Input: JSON array of review strings."),
    ]


def _build_prompt():
    from langchain_core.prompts import PromptTemplate
    return PromptTemplate.from_template("""You are a product intelligence agent. Analyze real-time scraped e-commerce reviews, compare products by components, identify customer pain points, and deliver actionable insights.

You have access to these tools:
{tools}

Use this EXACT format:
Question: the input question
Thought: think about what to do
Action: tool name (one of [{tool_names}])
Action Input: input to the tool
Observation: result
... (repeat Thought/Action/Observation as needed)
Thought: I now have enough information
Final Answer: your complete analysis

Question: {input}
{agent_scratchpad}""")


# ── Main Agent Class ──────────────────────────────────────────────────────────
class ProductIntelligenceAgent:
    def __init__(self):
        from langchain.agents import AgentExecutor, create_react_agent
        self.llm = _get_llm()
        tools = _build_tools()
        prompt = _build_prompt()
        agent = create_react_agent(self.llm, tools, prompt)
        self.executor = AgentExecutor(
            agent=agent, tools=tools,
            verbose=True, max_iterations=8,
            handle_parsing_errors=True
        )

    def analyze(self, query: str, component_data: Dict[str, Dict[str, List[str]]]) -> Dict[str, Any]:
        product_summaries = []
        for product, components in list(component_data.items())[:8]:
            comp_list = ", ".join(f"{c}({len(r)} reviews)" for c, r in components.items())
            product_summaries.append(f"- {product}: {comp_list}")
        context = "\n".join(product_summaries)

        prompt = f"""Analyze these real-time scraped products for query: "{query}"

Products and their review components:
{context}

Tasks:
1. Score sentiment for each major component across products
2. Compare products and identify the best performer per component
3. Extract the top 5 customer complaints overall
4. Give 3 strategic improvement recommendations
5. Write an executive summary (3-4 sentences)

Use your tools to perform the analysis step by step."""

        try:
            result = self.executor.invoke({"input": prompt})
            answer = result.get("output", "No output from agent.")
        except Exception as e:
            logger.error(f"Agent error: {e}")
            answer = f"Agent encountered an error: {e}"

        return {
            "query": query,
            "agent_analysis": answer,
            "products_analyzed": len(component_data),
            "components_found": list({c for comps in component_data.values() for c in comps}),
        }

    def quick_insights(self, product_title: str, reviews: List[str]) -> str:
        if not reviews:
            return "No reviews available for analysis."
        from langchain_core.messages import HumanMessage
        sample = reviews[:15]
        try:
            msg = HumanMessage(content=f"""You are a product review analyst. Given these reviews for "{product_title}", provide:
1. Overall sentiment (positive/negative/mixed)
2. Top 3 strengths
3. Top 3 weaknesses
4. One-line recommendation for buyers

Reviews:
{chr(10).join(f"- {r}" for r in sample)}""")
            response = self.llm.invoke([msg])
            return response.content
        except Exception as e:
            return f"Could not generate insights: {e}"
