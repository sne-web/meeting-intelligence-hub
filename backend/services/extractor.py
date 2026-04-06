import json
import re
from services.llm_client import ask_ai

# This is the system prompt — it tells the AI what role to play
# and what format to respond in
EXTRACTION_SYSTEM_PROMPT = """You are an expert meeting analyst. 
Your job is to carefully read meeting transcripts and extract:
1. Key decisions that were made
2. Action items that were assigned to specific people

Always respond with valid JSON only. No explanations, no markdown, just JSON."""

def extract_decisions_and_actions(transcript_text: str) -> dict:
    """
    Sends the transcript to the AI and asks it to extract
    decisions and action items as structured JSON.
    
    Returns a dict with 'decisions' and 'action_items' lists.
    """

    prompt = f"""Please analyse this meeting transcript and extract all decisions and action items.

TRANSCRIPT:
{transcript_text}

Return a JSON object in exactly this format:
{{
  "decisions": [
    {{
      "description": "what was decided",
      "context": "brief reason or context for the decision"
    }}
  ],
  "action_items": [
    {{
      "who": "person responsible",
      "what": "what they need to do",
      "by_when": "deadline if mentioned, otherwise 'Not specified'",
      "priority": "high/medium/low based on context"
    }}
  ]
}}

Rules:
- Only include things explicitly mentioned in the transcript
- For action items, extract the exact person's name if mentioned
- If no deadline is given, use "Not specified"
- Decisions are things the group agreed on
- Action items are tasks assigned to specific people"""

    try:
        response = ask_ai(prompt, system=EXTRACTION_SYSTEM_PROMPT, max_tokens=3000)
        
        # The AI should return pure JSON but sometimes adds extra text
        # This finds the JSON object within the response just in case
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(response)
            
        return result
    
    except json.JSONDecodeError:
        # If the AI returns something we can't parse, return empty results
        return {"decisions": [], "action_items": []}
    except Exception as e:
        raise Exception(f"Extraction failed: {str(e)}")