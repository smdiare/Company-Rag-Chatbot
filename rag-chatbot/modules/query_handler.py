from modules.embed import embed_text, upsert_documents_to_pinecone
from modules.pinecone_ops import search_pinecone
from modules.llm_response import ask_llm
from modules.supabase_ops import log_query_response
from langchain_core.documents import Document

def handle_query(user_question):
    query_vec = embed_text([user_question])[0]
    results = search_pinecone(query_vec)
    matches = results.get("matches", [])

    relevant = [m for m in matches if m["score"] >= 0.7]
    context = "\n\n".join([m["metadata"].get("text", "") for m in relevant])

    if not context.strip():
        print("⚠️ No relevant context retrieved!")
        return "Sorry, I couldn't find anything related in the documents."

    answer = ask_llm(user_question, context)
    log_query_response(user_question, answer)

    # 🔁 Reinforce if valid and confident match
    best_score = max((m["score"] for m in matches), default=0)
    if best_score >= 0.75 and answer.strip() and "couldn't find" not in answer.lower():
        print(f"✅ Reinforcing answer (Best Match Score: {best_score:.2f})")

        qa_text = f"Q: {user_question}\nA: {answer}"
        doc = Document(
            page_content=qa_text,
            metadata={
                "source": "context_reinforced",
                "score": best_score,
                "question": user_question
            }
        )

        upsert_count = upsert_documents_to_pinecone(
            [doc],
            file_id="reinforced_qa",
            namespace="reinforced_qa"
        )

        print(f"🧠 Reinforcement upserted: {upsert_count} vector(s)")
    else:
        print(f"⚠️ Skipped reinforcement — Score: {best_score:.2f}, Valid: {answer.strip() != ''}")

    return answer
