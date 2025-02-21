
### Updated Plan and Architecture

#### **Revised Objective**
Create a Python application that:
- Conducts an intellectual preference survey using the provided list of 31 questions.
- Ensures no question is asked twice by removing each asked question from the pool of available options.
- Limits the survey to a **maximum of 5 questions**, stopping after the 5th question is answered.
- Uses the OpenAI Gemini 2.0 Flash model (via OpenRouter API) to dynamically select each question based on prior responses.
- Simulates user responses with a random yes/no function.
- Saves the results in `/Users/philip.galebach/coding-projects/alexandria/intellectual_dna`.

---

#### **Key Changes**
1. **Question Limit**: The survey stops after 5 questions, even though 26 questions remain unasked.
2. **Repetition Prevention**: Maintain the mechanism of removing each asked question from `remaining_questions` to ensure no duplicates within the 5-question limit.
3. **Loop Termination**: Update the control loop to exit after 5 iterations instead of when `remaining_questions` is empty.

---

#### **Updated Architecture Overview**

##### **Components (Refined)**
1. **Question Bank**:
   - Static list of 31 questions (unchanged).
   - Example: `["If you could prove or disprove God's existence, would you want to know?", ...]`.

2. **Remaining Questions**:
   - Dynamic list, initialized as a copy of the question bank (31 questions).
   - Shrinks by 1 each time a question is asked, down to 26 after 5 questions.

3. **Conversation History**:
   - List storing each asked question and its simulated response.
   - Grows to a maximum of 5 entries.
   - Example: `[("Q1 text", "yes"), ("Q2 text", "no"), ..., ("Q5 text", "yes")]`.

4. **User Response Simulator**:
   - Unchanged: Randomly generates "yes" or "no".

5. **LLM Question Selector**:
   - Takes `conversation_history` and `remaining_questions` as input.
   - Selects the next question from `remaining_questions`, which is then removed after being asked.

6. **Main Control Loop**:
   - Updated: Runs for exactly 5 iterations (or fewer if manually stopped).
   - Removes each asked question from `remaining_questions` to prevent repetition.
   - Stops after the 5th question is answered.

7. **File Output**:
   - Saves the final `conversation_history` (max 5 entries) as JSON.

---

#### **Revised Program Flow**
1. **Initialization**:
   - Load the 31 questions into `question_bank`.
   - Create `remaining_questions` as a copy of `question_bank` (31 questions).
   - Initialize an empty `conversation_history` list.
   - Set a counter (`question_count`) to track the number of questions asked, starting at 0.

2. **Starting the Survey**:
   - Send `remaining_questions` to the LLM: "Here are the questions: [0: Q1, 1: Q2, ..., 30: Q31]. Select the starting question. Respond with the number."
   - LLM returns a number (e.g., "0" for Q1).
   - Ask Q1, simulate a response (e.g., "yes").
   - Append (Q1, "yes") to `conversation_history`.
   - Remove Q1 from `remaining_questions`.
   - Increment `question_count` to 1.

3. **Main Loop**:
   - While `question_count < 5`:
     - Send `conversation_history` and updated `remaining_questions` to the LLM: "History: [Q1: yes]. Remaining questions: [0: Q2, 1: Q3, ...]. Select the next question. Respond with the number."
     - LLM returns a number (e.g., "0" for Q2).
     - Ask Q2, simulate a response (e.g., "no").
     - Append (Q2, "no") to `conversation_history`.
     - Remove Q2 from `remaining_questions`.
     - Increment `question_count` (e.g., to 2).
   - Repeat until `question_count == 5`.

4. **LLM Interaction**:
   - **Prompt Design** (Unchanged):
     - Initial: "Here are the questions: [0: Q1, 1: Q2, ..., 30: Q31]. Select the starting question. Respond with the number."
     - Subsequent: "History: [Q1: yes, Q2: no, ...]. Remaining questions: [0: Q3, 1: Q4, ...]. Select the next question that logically follows. Respond with the number."
   - Parse the LLM’s response, ask the question, and remove it from `remaining_questions`.

5. **Termination**:
   - Stop after `question_count` reaches 5 (after the 5th question is answered).
   - At this point:
     - `conversation_history` has 5 entries.
     - `remaining_questions` has 26 questions left.

6. **Output**:
   - Save `conversation_history` to `survey_history.json`.

---

#### **Updated Data Structures**
- **Question Bank**: Static list of 31 strings (unchanged).
- **Remaining Questions**: Starts with 31 questions, ends with 26 after 5 iterations.
  - Example: `[Q1, Q2, ..., Q31]` → `[Q2, Q3, ..., Q31]` → ... → `[Q6, Q7, ..., Q31]`.
- **Conversation History**: Grows to exactly 5 entries.
  - Example: `[("Q1", "yes"), ("Q2", "no"), ("Q3", "yes"), ("Q4", "no"), ("Q5", "yes")]`.

---

#### **Sample Workflow (Revised for 5 Questions)**
1. **Start**:
   - `question_bank`: [Q1, Q2, ..., Q31]
   - `remaining_questions`: [Q1, Q2, ..., Q31]
   - `conversation_history`: []
   - `question_count`: 0
   - LLM selects "0" (Q1).
   - Ask Q1: "If you could prove or disprove God's existence, would you want to know?"
   - Answer: "Yes"
   - `conversation_history`: [(Q1, "yes")]
   - Remove Q1, `remaining_questions`: [Q2, Q3, ..., Q31]
   - `question_count`: 1

2. **Second Question**:
   - LLM selects "0" (Q2 from new list).
   - Ask Q2: "Can reason alone lead us to religious truth?"
   - Answer: "No"
   - `conversation_history`: [(Q1, "yes"), (Q2, "no")]
   - Remove Q2, `remaining_questions`: [Q3, Q4, ..., Q31]
   - `question_count`: 2

3. **Third Question**:
   - LLM selects "2" (Q5 from new list).
   - Ask Q5: "Can multiple religions all be true?"
   - Answer: "Yes"
   - `conversation_history`: [(Q1, "yes"), (Q2, "no"), (Q5, "yes")]
   - Remove Q5, `remaining_questions`: [Q3, Q4, Q6, ..., Q31]
   - `question_count`: 3

4. **Fourth Question**:
   - LLM selects "1" (Q4 from new list).
   - Ask Q4: "Must the divine be personal to be meaningful?"
   - Answer: "No"
   - `conversation_history`: [(Q1, "yes"), (Q2, "no"), (Q5, "yes"), (Q4, "no")]
   - Remove Q4, `remaining_questions`: [Q3, Q6, Q7, ..., Q31]
   - `question_count`: 4

5. **Fifth Question**:
   - LLM selects "0" (Q3 from new list).
   - Ask Q3: "Is faith more about experience or tradition?"
   - Answer: "Yes"
   - `conversation_history`: [(Q1, "yes"), (Q2, "no"), (Q5, "yes"), (Q4, "no"), (Q3, "yes")]
   - Remove Q3, `remaining_questions`: [Q6, Q7, ..., Q31]
   - `question_count`: 5
   - Stop.

6. **Output**:
   - Save to `survey_history.json`.

---

#### **Key Design Updates**
- **Stopping Condition**: Use `question_count < 5` instead of checking if `remaining_questions` is empty.
- **Repetition Prevention**: Remains intact—each asked question is removed from `remaining_questions`, ensuring no duplicates within the 5-question limit.
- **Scope**: Only 5 of the 31 questions are used, leaving 26 unasked.

---

#### **Technical Considerations (Updated)**
- **Counter**: Add `question_count` to track iterations, incrementing after each question is asked.
- **Loop Control**: Use a `while question_count < 5` condition to enforce the 5-question limit.
- **File Output**: Ensure the JSON file reflects only the 5 asked questions.

---

#### **Output File**
- **Path**: `/Users/philip.galebach/coding-projects/alexandria/intellectual_dna/survey_history.json`
- **Format** (Example):
  ```json
  [
    {"question": "If you could prove or disprove God's existence, would you want to know?", "answer": "yes"},
    {"question": "Can reason alone lead us to religious truth?", "answer": "no"},
    {"question": "Can multiple religions all be true?", "answer": "yes"},
    {"question": "Must the divine be personal to be meaningful?", "answer": "no"},
    {"question": "Is faith more about experience or tradition?", "answer": "yes"}
  ]
  ```

---

#### **Validation**
- **No Repetition**: Each question is removed after being asked, ensuring the 5 questions are unique.
- **Max 5 Questions**: The loop stops after 5 iterations, enforced by `question_count`.
- **Logical Flow**: The LLM still selects questions based on prior responses, maintaining coherence within the shorter survey.

This updated plan should now fully align with your requirements: no question is asked twice, and the survey caps at 5 questions. Let me know if there’s anything else to tweak before we proceed to coding!
