import os
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

# ── Environment setup ──────────────────────────────────────────────────────────

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print("No API key found!")
else:
    print(f"OpenAI API Key exists and begins {api_key[:8]}")

# ── API Clients ────────────────────────────────────────────────────────────────

openai = OpenAI(api_key=api_key)

# Ollama is optional — only works if user has it installed locally
try:
    ollama_via_openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')
    ollama_available = True
except Exception:
    ollama_available = False

# ── Models ─────────────────────────────────────────────────────────────────────

MODELS = {
    'GPT-4o Mini': ('openai', 'gpt-4o-mini'),
    'LLaMA 3.2 (Local)': ('ollama', 'llama3.2'),
}

# ── System Prompt ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are an expert startup coach helping founders draft a 2-minute (120 second) 
pitch deck script based strictly on the given information about a business.

This is not a slide-by-slide script. It is a spoken pitch — for a stage presentation 
or a founder video recording. Clarity and passion are key.

Follow these rules exactly:

1. HOOK in the first 10 seconds — grab attention immediately
2. INVERTED PYRAMID structure — state the conclusion first, then follow with proof
3. SHOW, DON'T TELL — use real stories, real users, real numbers
4. PLAIN ENGLISH — no buzzwords, no jargon
5. INCLUDE THE FOUNDERS' STORY — make it personal and real
6. CLEAR DIFFERENTIATION — why will this win?
7. LARGE MARKET FRAMING — show the size of the opportunity
8. REAL TRACTION PROOF — if it exists, state it clearly

Structure to follow (not rigidly, but as a guide):
- Hook (10 seconds)
- Founders story + problem
- Solution
- Market opportunity
- Differentiation + traction
- Call to action / closing

Output the script in markdown without code blocks.
Target length: 120 seconds when spoken aloud (approximately 250-280 words).
"""

# ── Core function ──────────────────────────────────────────────────────────────

def stream_pitch(
    startup_name,
    founders_story,
    problem,
    solution,
    market_opportunity,
    traction,
    differentiation,
    team,
    model_choice
):
    # Input validation
    if not startup_name.strip() or not problem.strip() or not solution.strip():
        yield "Please fill in at least the Startup Name, Problem, and Solution fields."
        return

    # Build user prompt dynamically from Gradio inputs
    user_prompt = f"""
Please generate a 2-minute (120 second) pitch deck script for the following business.

Follow the system instructions exactly.

--- BUSINESS INFORMATION ---

Startup Name: {startup_name}

Founders Story:
{founders_story}

Problem:
{problem}

Solution:
{solution}

Market Opportunity:
{market_opportunity}

Traction:
{traction}

Differentiation:
{differentiation}

Team:
{team}

--- END OF BUSINESS INFORMATION ---

Remember:
- Hook in first 10 seconds
- Inverted pyramid structure
- Plain English, no buzzwords
- Show don't tell
- Include founders story
- Real traction proof
"""

    # Select model and API client
    if model_choice not in MODELS:
        yield "Invalid model selected."
        return

    client_name, model_id = MODELS[model_choice]

    if client_name == 'ollama' and not ollama_available:
        yield "LLaMA (Ollama) is not available. Please install Ollama or select GPT."
        return

    client = openai if client_name == 'openai' else ollama_via_openai

    try:
        stream = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            stream=True
        )

        result = ""
        for chunk in stream:
            result += chunk.choices[0].delta.content or ""
            yield result

    except Exception as e:
        yield f"Something went wrong: {e}"


# ── Gradio UI ──────────────────────────────────────────────────────────────────

with gr.Blocks(title="AI Pitch Deck Script Generator") as view:
    gr.Markdown("# AI Pitch Deck Script Generator")
    gr.Markdown("Fill in your business details and generate a 2-minute investor pitch script.")

    with gr.Row():
        with gr.Column():
            startup_name = gr.Textbox(label="Startup Name", placeholder="e.g. NexEve")
            founders_story = gr.Textbox(
                label="Founders Story",
                placeholder="How did you come up with this idea? What's your personal connection to the problem?",
                lines=4
            )
            problem = gr.Textbox(
                label="Problem",
                placeholder="What problem are you solving? Who has this problem?",
                lines=4
            )
            solution = gr.Textbox(
                label="Solution",
                placeholder="What does your product do? How does it solve the problem?",
                lines=4
            )
            market_opportunity = gr.Textbox(
                label="Market Opportunity",
                placeholder="How big is the market? What's the TAM/SAM/SOM?",
                lines=3
            )
            traction = gr.Textbox(
                label="Traction",
                placeholder="Users, revenue, pilots, design partners, interviews — anything real",
                lines=3
            )
            differentiation = gr.Textbox(
                label="Differentiation",
                placeholder="Why will you win? What do competitors miss?",
                lines=3
            )
            team = gr.Textbox(
                label="Team",
                placeholder="Who are the founders? What's your relevant background?",
                lines=3
            )
            model_selector = gr.Dropdown(
                choices=list(MODELS.keys()),
                value="GPT-4o Mini",
                label="Select Model"
            )
            submit_btn = gr.Button("Generate Pitch Script", variant="primary")

        with gr.Column():
            output = gr.Markdown(label="Your Pitch Script")

    submit_btn.click(
        fn=stream_pitch,
        inputs=[
            startup_name, founders_story, problem, solution,
            market_opportunity, traction, differentiation, team,
            model_selector
        ],
        outputs=output
    )

    gr.Examples(
        examples=[[
            "NexEve",
            "While organizing tech events through a nonprofit, we experienced firsthand the chaos of coordinating venues, catering, staffing, and last-minute changes.",
            "Event service providers lose $100K-$500K/year due to fragmented operations — spreadsheets, emails, and disconnected tools.",
            "AI-powered operations platform that centralizes staffing, scheduling, task execution, and reporting for event service providers.",
            "$8.4B market growing to $17.3B by 2030. Over 1M vendors globally. Core SaaS TAM: $750M.",
            "100+ customer interviews. 5 design partners committed to onboarding at launch.",
            "Competitors manage tasks. NexEve orchestrates operations. Domain-specific, mobile-first, AI-native.",
            "Maryam Ghaderi (CEO) — 8 years in AI. Amirhadi Tavakoli (CTO) — 2x founder.",
            "GPT-4o Mini"
        ]],
        inputs=[
            startup_name, founders_story, problem, solution,
            market_opportunity, traction, differentiation, team,
            model_selector
        ]
    )

view.launch(inbrowser=True)