# AI Pitch Script Generator

Generate a 2-minute investor pitch script from your startup details using GPT-4.
Follows Y Combinator pitch best practices — hook, inverted pyramid structure, 
plain English, no buzzwords.

## Demo

![Demo](assets/demo.gif)

## Features

- Fill in your startup details via a clean Gradio form
- Generates a spoken 2-minute pitch script (not slide-by-slide)
- Follows YC pitch rules: hook, show don't tell, inverted pyramid structure
- Supports GPT-4o Mini and LLaMA 3.2 (local via Ollama)
- Streams the response in real time

## Tech Stack

- Python
- OpenAI API
- Gradio
- Ollama (optional, for local LLaMA model)

## Getting Started

### 1. Clone the repo
git clone https://github.com/ghaderimaryam/ai-pitch-script-generator.git
cd ai-pitch-script-generator

### 2. Install dependencies
pip install -r requirements.txt

### 3. Set up environment variables
cp .env.example .env
# Add your OpenAI API key to .env

### 4. Run the app
python3 app.py

## Project Structure

ai-pitch-script-generator/
├── app.py               ← main application
├── requirements.txt     ← dependencies
├── .env.example         ← API key template
├── .gitignore           ← excludes .env and cache
├── assets/
│   └── demo.gif         ← demo recording
└── README.md

## Pitch Script Structure

The generated script follows this flow:
- Hook (first 10 seconds)
- Founders story + problem
- Solution
- Market opportunity
- Differentiation + traction
- Call to action

## Acknowledgements

Pitch framework inspired by Y Combinator application guidelines.
