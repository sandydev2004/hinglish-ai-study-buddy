"""
summarizer.py
-------------
Handles text chunking, prompt management, and interaction with the Gemini API
to generate exam-focused Hinglish study summaries.
"""

import os
from typing import List
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# ==========================================
# PROMPT CONFIGURATION (EASY TO EDIT & TUNE)
# ==========================================

# Core instruction explaining how to write Hinglish with technical terms
HINGLISH_GUIDELINE = (
    "Explain in conversational Hinglish (Hindi written in Roman script mixed naturally with English technical terms). "
    "Keep technical terms strictly in English (e.g., 'Deadlock', 'Paging', 'Polymorphism', 'Throughput'). "
    "Tone should be friendly and exam-focused, like a smart senior explaining to a junior before an exam."
)

# Prompt for Short Mode: exactly 10 bullet points
SHORT_SUMMARY_PROMPT = f"""
You are 'Hinglish AI Study Buddy', an AI tutor helping Indian college students revise for exams.

INSTRUCTIONS:
1. {HINGLISH_GUIDELINE}
2. Extract the most important concepts and provide EXACTLY 10 punchy, high-yield bullet points.
3. Every bullet point must have the technical keyword in English followed by a clear Hinglish explanation.

STUDY MATERIAL:
{{text}}

HINGLISH SUMMARY (10 BULLET POINTS):
"""

# Prompt for Detailed Mode: topic-wise structured study guide
DETAILED_SUMMARY_PROMPT = f"""
You are 'Hinglish AI Study Buddy', an AI tutor helping Indian college students revise for exams.

INSTRUCTIONS:
1. {HINGLISH_GUIDELINE}
2. Break down the material into clear topics with markdown headers (e.g. '### 1. Topic Name').
3. Under each topic, provide:
   - **Concept Explanation**: What it is, in intuitive Hinglish.
   - **Why it matters / Exam Tip**: Important points frequently asked in viva or university exams.

STUDY MATERIAL:
{{text}}

DETAILED HINGLISH STUDY GUIDE:
"""

# Prompt for combining intermediate chunk summaries into a final coherent summary
COMBINE_CHUNKS_PROMPT = f"""
You are 'Hinglish AI Study Buddy'.
Below are intermediate summaries extracted from different sections of a large chapter.

INSTRUCTIONS:
1. {HINGLISH_GUIDELINE}
2. Synthesize and consolidate these section summaries into a single cohesive {{mode_description}} summary.
3. Remove redundancies and maintain a logical flow of concepts.

INTERMEDIATE SECTION SUMMARIES:
{{text}}

FINAL CONSOLIDATED SUMMARY:
"""


class SummarizerError(Exception):
    """Custom exception raised when Gemini API call or configuration fails."""
    pass


# Function to configure Gemini API client
# Why: Validates that the API key exists before sending requests and initializes the client model.
def _get_configured_model() -> genai.GenerativeModel:
    """
    Validates the API key from environment variables and configures the Gemini model.

    Returns:
        genai.GenerativeModel: Configured Gemini generative model instance.

    Raises:
        SummarizerError: If GEMINI_API_KEY is not configured.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.strip() == "" or api_key == "your_gemini_api_key_here":
        raise SummarizerError(
            "GEMINI_API_KEY nahi mila! Kripya study-buddy/.env file me apna valid Gemini API key dalein."
        )

    genai.configure(api_key=api_key)
    # Using gemini-1.5-flash for fast and cost-effective responses
    return genai.GenerativeModel(model_name="gemini-3.8-flash")


# Function to split text into chunks based on word count
# Why: LLMs have token limits and perform better when given bite-sized context.
# Splitting into ~3000 words ensures we stay safely within context limits.
def chunk_text(text: str, chunk_size: int = 3000) -> List[str]:
    """
    Splits input text into a list of chunks, where each chunk has at most `chunk_size` words.

    Args:
        text: Raw text string to split.
        chunk_size: Maximum number of words per chunk (default: 3000).

    Returns:
        List[str]: List of text chunks.
    """
    words = text.split()
    if not words:
        return []

    if len(words) <= chunk_size:
        return [text]

    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk_slice = words[i : i + chunk_size]
        chunks.append(" ".join(chunk_slice))

    return chunks


# Function to generate summary for a single block of text
# Why: Reusable helper function that sends a formatted prompt to Gemini and returns clean text.
def _generate_gemini_response(model: genai.GenerativeModel, prompt: str) -> str:
    """
    Sends a prompt to Gemini and extracts the text response.

    Args:
        model: Configured Gemini model.
        prompt: Full formatted prompt string.

    Returns:
        str: Generated summary text.

    Raises:
        SummarizerError: If the API call fails (network issues, rate limits, etc.).
    """
    try:
        response = model.generate_content(prompt)
        if not response.text:
            raise SummarizerError("Gemini se empty response aaya. Please dobara try karein.")
        return response.text.strip()
    except Exception as e:
        if isinstance(e, SummarizerError):
            raise e
        raise SummarizerError(f"Gemini API error aaya: {str(e)}")


# Main summarization entry point orchestrating single-chunk or multi-chunk map-reduce flow
# Why: Hides complexity from app.py. The UI simply calls summarize(text, mode).
def summarize(text: str, mode: str = "short") -> str:
    """
    Generates a Hinglish summary for the provided text.
    Handles long texts automatically using a Map-Reduce chunking strategy.

    Args:
        text: Extracted PDF text.
        mode: Either "short" (10 bullet points) or "detailed" (topic-wise).

    Returns:
        str: Final Hinglish summary in Markdown format.

    Raises:
        SummarizerError: If text is empty, mode is invalid, or an API error occurs.
    """
    if not text or not text.strip():
        raise SummarizerError("Summarize karne ke liye text nahi mila.")

    mode_clean = mode.lower().strip()
    if "short" in mode_clean:
        selected_prompt_template = SHORT_SUMMARY_PROMPT
        mode_description = "10 bullet points"
    elif "detailed" in mode_clean:
        selected_prompt_template = DETAILED_SUMMARY_PROMPT
        mode_description = "detailed topic-wise"
    else:
        raise SummarizerError(f"Invalid mode '{mode}'. Choose 'short' or 'detailed'.")

    model = _get_configured_model()
    chunks = chunk_text(text, chunk_size=3000)

    # Case 1: Short / normal document (single chunk)
    if len(chunks) == 1:
        full_prompt = selected_prompt_template.format(text=chunks[0])
        return _generate_gemini_response(model, full_prompt)

    # Case 2: Long document (multiple chunks) -> Map-Reduce pattern
    # Step A (Map): Summarize each chunk individually
    chunk_summaries: List[str] = []
    for index, chunk in enumerate(chunks):
        intermediate_prompt = (
            f"Summarize this section of study notes in concise Hinglish bullet points:\n\n{chunk}"
        )
        intermediate_summary = _generate_gemini_response(model, intermediate_prompt)
        chunk_summaries.append(f"### Part {index + 1} Summary:\n{intermediate_summary}")

    # Step B (Reduce): Combine all chunk summaries into the final requested format
    combined_intermediate_text = "\n\n".join(chunk_summaries)
    final_prompt = COMBINE_CHUNKS_PROMPT.format(
        mode_description=mode_description,
        text=combined_intermediate_text
    )

    return _generate_gemini_response(model, final_prompt)

