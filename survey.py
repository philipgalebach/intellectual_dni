"""
Intellectual Preference Survey Implementation
Conducts a survey using pre-defined questions and LLM-based question selection.
"""

import random
import json
import os
import requests
from typing import List, Tuple, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

# Define question bank with all 31 questions
QUESTION_BANK = [
    "If you could prove or disprove God's existence, would you want to know?",
    "Can reason alone lead us to religious truth?",
    "Is faith more about experience or tradition?",
    "Must the divine be personal to be meaningful?",
    "Can multiple religions all be true?",
    "Should religious truth adapt to modern knowledge?",
    "Is divine revelation necessary for moral knowledge?",
    "Does evil disprove a perfect God?",
    "Is the universe itself divine?",
    "Does genuine free will exist?",
    "Is religion more about transformation or truth?",
    "Can sacred texts contain errors?",
    "Is mystical experience trustworthy?",
    "Should faith seek understanding?",
    "Does divine hiddenness matter?",
    "Can finite minds grasp infinite truth?",
    "Is reality fundamentally good?",
    "Does prayer change anything?",
    "Is consciousness evidence of divinity?",
    "Can miracles violate natural law?",
    "Is there purpose in evolution?",
    "Can symbols contain ultimate truth?",
    "Is divine grace necessary for virtue?",
    "Should tradition limit interpretation?",
    "Can ritual create real change?",
    "Is doubt part of authentic faith?",
    "Must religion be communal?",
    "Can God's nature be known?",
    "Is suffering meaningful?",
    "Is love the ultimate reality?",
    "Does immortality give life meaning?"
]

# Load environment variables
load_dotenv()

# OpenRouter API Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

class IntellectualPreferenceSurvey:
    def __init__(self, save_path: str, api_key: Optional[str] = None):
        """
        Initialize the survey with question bank and tracking variables.
        
        Args:
            save_path (str): Path where survey results will be saved
        """
        self.question_bank = QUESTION_BANK
        self.remaining_questions = QUESTION_BANK.copy()  # Copy to avoid modifying original
        self.conversation_history: List[Tuple[str, str]] = []
        self.question_count = 0
        self.save_path = Path(save_path)
        
        # API configuration
        self.api_key = api_key or OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("OpenRouter API key not provided and not found in environment")
        
        # Ensure save directory exists
        self.save_path.parent.mkdir(parents=True, exist_ok=True)

    def simulate_response(self) -> str:
        """Simulate a yes/no response."""
        return random.choice(["yes", "no"])

    def format_history_for_llm(self) -> str:
        """Format conversation history for LLM prompt."""
        if not self.conversation_history:
            return "No previous questions asked."
        
        formatted = "Previous questions and answers:\n"
        for question, answer in self.conversation_history:
            formatted += f"Q: {question}\nA: {answer}\n"
        return formatted

    def format_remaining_questions(self) -> str:
        """Format remaining questions for LLM prompt."""
        formatted = "Available questions:\n"
        for idx, question in enumerate(self.remaining_questions):
            formatted += f"{idx}: {question}\n"
        return formatted

    def save_results(self) -> None:
        """Save survey results by appending to a single JSON file."""
        from datetime import datetime
        
        # Create results with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_result = {
            "timestamp": timestamp,
            "responses": [
                {"question": q, "answer": a} 
                for q, a in self.conversation_history
            ]
        }
        
        # Ensure simulations directory exists
        simulations_dir = self.save_path.parent
        simulations_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing results or create new list
        existing_results = []
        if self.save_path.exists():
            with open(self.save_path, 'r') as f:
                try:
                    existing_results = json.load(f)
                except json.JSONDecodeError:
                    existing_results = []
        
        # Append new results
        existing_results.append(new_result)
        
        # Save updated results
        with open(self.save_path, 'w') as f:
            json.dump(existing_results, f, indent=2)

    def is_complete(self) -> bool:
        """Check if survey is complete (5 questions asked)."""
        return self.question_count >= 5

    def select_next_question(self) -> Optional[str]:
        """
        Use LLM to select the next most appropriate question based on conversation history.
        
        Returns:
            str: Selected question text, or None if LLM response is invalid
        """
        if self.is_complete() or not self.remaining_questions:
            return None

        prompt = self._create_selection_prompt()
        print("Sending prompt to LLM...")
        
        try:
            print("\nSending request to OpenRouter API...")
            request_data = {
                "model": "google/gemini-2.0-flash-001",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            print(f"Request data: {json.dumps(request_data, indent=2)}")
            
            response = requests.post(
                url=OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/martian-engineering/alexandria",
                    "X-Title": "Alexandria Survey",
                },
                json=request_data
            )
            
            print(f"\nResponse status: {response.status_code}")
            if response.status_code != 200:
                print(f"Error response: {response.text}")
            response.raise_for_status()
            
            # Parse response to get question index
            result = response.json()
            print(f"LLM Response: {result}")
            selected_idx = self._parse_llm_response(result['choices'][0]['message']['content'])
            print(f"Selected index: {selected_idx}")
            
            if selected_idx is not None and 0 <= selected_idx < len(self.remaining_questions):
                selected_question = self.remaining_questions[selected_idx]
                self.remaining_questions.pop(selected_idx)
                return selected_question
            
        except Exception as e:
            print(f"Error selecting next question: {e}")
        
        return None

    def _create_selection_prompt(self) -> str:
        """Create prompt for LLM to select next question."""
        prompt = "Task: Select the most appropriate next question number from the available options.\n\n"
        
        if self.conversation_history:
            prompt += "Previous responses:\n"
            for q, a in self.conversation_history:
                prompt += f"Q: {q}\nA: {a}\n"
            prompt += "\n"
        
        prompt += "Available questions (select one number):\n"
        for idx, q in enumerate(self.remaining_questions):
            prompt += f"{idx}. {q}\n"
        
        prompt += "\nProvide ONLY the question number (e.g. '2' or '15'). Do not explain your choice."
        
        return prompt

    def _parse_llm_response(self, response: str) -> Optional[int]:
        """
        Parse LLM response to get question index.
        
        Args:
            response (str): Raw LLM response text
            
        Returns:
            Optional[int]: Parsed question index or None if invalid
        """
        try:
            # Extract first number from response
            import re
            numbers = re.findall(r'\d+', response)
            if numbers:
                return int(numbers[0])
        except Exception:
            pass
        return None

    def run_survey(self) -> None:
        """
        Run the complete survey until 5 questions are asked.
        """
        while not self.is_complete():
            # Select next question
            question = self.select_next_question()
            if not question:
                print("Failed to select next question")
                break
                
            # Simulate response
            answer = self.simulate_response()
            
            # Record interaction
            self.conversation_history.append((question, answer))
            self.question_count += 1
            
            # Display progress
            print(f"\nQuestion {self.question_count}/5:")
            print(f"Q: {question}")
            print(f"A: {answer}\n")
        
        # Save results
        self.save_results()
        print("Survey complete. Results saved.")

        # Reset survey state for potential reuse
        self.remaining_questions = QUESTION_BANK.copy()
        self.conversation_history = []
        self.question_count = 0

def test_api_connection(api_key: str) -> bool:
    """Test the API connection with a simple request."""
    try:
        response = requests.post(
            url=OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "google/gemini-2.0-flash-001",
                "messages": [{"role": "user", "content": "Respond with only the number: 1"}]
            }
        )
        print(f"API test response: {response.status_code}")
        print(f"Response content: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"API test failed: {e}")
        return False

if __name__ == "__main__":
    # Path for saving results
    base_path = Path(__file__).parent
    save_path = base_path / "simulations" / "survey_results.json"
    
    # Load API key and test connection
    api_key = os.getenv('OPENROUTER_API_KEY')
    print(f"Testing API connection with key: {api_key[:10]}...")
    if not test_api_connection(api_key):
        print("Failed to connect to OpenRouter API. Please check your API key and connection.")
        exit(1)
    
    # Get number of runs from command line argument or use default
    import sys
    num_runs = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        
    # Create and run survey multiple times
    survey = IntellectualPreferenceSurvey(str(save_path))
    for run in range(num_runs):
        print(f"\nStarting survey run {run + 1}/{num_runs}")
        survey.run_survey()
