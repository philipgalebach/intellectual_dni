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
        """Save survey results to JSON file."""
        results = [
            {"question": q, "answer": a} 
            for q, a in self.conversation_history
        ]
        
        with open(self.save_path, 'w') as f:
            json.dump(results, f, indent=2)

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
        
        try:
            response = requests.post(
                url=OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/martian-engineering/alexandria",
                    "X-Title": "Alexandria Survey",
                },
                json={
                    "model": "google/gemini-2.0-flash-001",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            )
            response.raise_for_status()
            
            # Parse response to get question index
            result = response.json()
            selected_idx = self._parse_llm_response(result['choices'][0]['message']['content'])
            
            if selected_idx is not None and 0 <= selected_idx < len(self.remaining_questions):
                selected_question = self.remaining_questions[selected_idx]
                self.remaining_questions.pop(selected_idx)
                return selected_question
            
        except Exception as e:
            print(f"Error selecting next question: {e}")
        
        return None

    def _create_selection_prompt(self) -> str:
        """Create prompt for LLM to select next question."""
        prompt = "You are an expert survey conductor specializing in intellectual preference surveys. "
        prompt += "Your task is to select the most appropriate next question based on previous responses.\n\n"
        
        # Add conversation history
        history = self.format_history_for_llm()
        prompt += f"{history}\n\n"
        
        # Add remaining questions
        questions = self.format_remaining_questions()
        prompt += f"{questions}\n\n"
        
        prompt += "Based on the previous responses, select the most logical next question. "
        prompt += "Respond with ONLY the number (index) of the chosen question. "
        prompt += "For example: '2' or '15'"
        
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

if __name__ == "__main__":
    # Path for saving results
    save_path = Path(__file__).parent / "survey_results.json"
    
    # Create and run survey
    survey = IntellectualPreferenceSurvey(str(save_path))
    survey.run_survey()
