# LAB Submission Notes: Custom RAG Query

I created a custom text data source at `07_rag/data/webmethods_interview_rag.txt` based on IBM webMethods Hybrid Integration documentation because I want interview-focused revision material in one searchable place.  
My search function reads paragraph chunks and scores each chunk by keyword overlap with the user query, then returns the top matches as structured JSON context for generation.  
My system prompt instructs the LLM to answer using only retrieved context, clearly signal if context is insufficient, and format the output for interview prep with a short answer, key points, interview angle, and one follow-up question.  
This workflow gives me grounded responses that are easier to trust and reuse for concept revision before interviews.
