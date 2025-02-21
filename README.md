# Intellectual Preference Survey

A Python-based survey system that conducts automated intellectual preference surveys using LLM-powered question selection. The system intelligently selects questions based on previous responses, creating a personalized and coherent survey experience.

## Overview

This project implements an automated survey system that:
- Conducts surveys using a curated bank of 31 philosophical/theological questions
- Uses Google's Gemini 2.0 Flash model (via OpenRouter API) to intelligently select questions
- Limits each survey to 5 questions, ensuring focused and efficient data collection
- Prevents question repetition within each survey session
- Simulates user responses (yes/no) for testing purposes
- Saves survey results with timestamps in JSON format

## Features

- **Dynamic Question Selection**: Uses LLM to choose the most contextually appropriate next question based on previous responses
- **State Management**: Tracks conversation history and remaining questions to prevent duplicates
- **Persistent Storage**: Saves all survey results in a structured JSON format
- **Multiple Survey Support**: Can run multiple survey sessions in sequence
- **API Error Handling**: Robust error handling for API interactions
- **Configurable**: Supports custom API keys and save locations

## Prerequisites

- Python 3.7+
- OpenRouter API key
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/philipgalebach/intellectual-preference-survey.git
cd intellectual-preference-survey
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your OpenRouter API key:
```
OPENROUTER_API_KEY=your_api_key_here
```

## Usage

### Basic Usage

Run a single survey:
```bash
python survey.py
```

Run multiple surveys:
```bash
python survey.py 5  # Runs 5 survey sessions
```

### Output

Survey results are saved in `simulations/survey_results.json` with the following structure:
```json
[
  {
    "timestamp": "20250220_234416",
    "responses": [
      {
        "question": "Is doubt part of authentic faith?",
        "answer": "yes"
      },
      // ... more responses
    ]
  }
]
```

## Project Structure

```
intellectual-preference-survey/
├── survey.py           # Main survey implementation
├── requirements.txt    # Python dependencies
├── .env               # API key configuration
├── simulations/       # Survey results directory
│   └── survey_results.json
└── README.md          # This file
```

## Configuration

The survey system can be configured through:

1. Environment variables in `.env`:
   - `OPENROUTER_API_KEY`: Your OpenRouter API key

2. Command line arguments:
   - First argument: Number of survey runs (default: 1)
