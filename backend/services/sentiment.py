import json
import re
from services.llm_client import ask_ai

SENTIMENT_SYSTEM_PROMPT = """You are an expert in workplace communication and meeting dynamics.
Analyse meeting transcripts for sentiment, tone, and emotional dynamics.
Always respond with valid JSON only. No explanations, no markdown, just JSON."""

def analyse_sentiment(transcript_text: str, speakers: list) -> dict:
    """
    Analyses the overall sentiment and tone of a meeting transcript.
    Returns sentiment scores per speaker and overall meeting tone.
    """

    prompt = f"""Analyse the sentiment and tone of this meeting transcript.

TRANSCRIPT:
{transcript_text}

SPEAKERS IDENTIFIED: {', '.join(speakers) if speakers else 'Unknown'}

Return a JSON object in exactly this format:
{{
  "overall_sentiment": "positive/negative/neutral/mixed",
  "summary": "2-3 sentence summary of the meeting tone and dynamics",
  "speaker_sentiments": [
    {{
      "speaker": "name",
      "sentiment": "positive/negative/neutral",
      "notes": "brief observation about this speaker's tone"
    }}
  ],
  "segments": [
    {{
      "topic": "what was being discussed",
      "sentiment": "positive/negative/neutral/conflict/agreement",
      "intensity": "low/medium/high"
    }}
  ],
  "flags": {{
    "has_conflict": false,
    "has_strong_agreement": false,
    "has_frustration": false,
    "has_enthusiasm": false
  }}
}}

Rules:
- Be objective and professional
- Base analysis only on what is in the transcript"""

    try:
        response = ask_ai(prompt, system=SENTIMENT_SYSTEM_PROMPT, max_tokens=2000)
        
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(response)
            
        return result
    
    except json.JSONDecodeError:
        return {
            "overall_sentiment": "neutral",
            "summary": "Could not analyse sentiment.",
            "speaker_sentiments": [],
            "segments": [],
            "flags": {
                "has_conflict": False,
                "has_strong_agreement": False,
                "has_frustration": False,
                "has_enthusiasm": False
            }
        }
    except Exception as e:
        raise Exception(f"Sentiment analysis failed: {str(e)}")