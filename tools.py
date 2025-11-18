# tools.py
import os
import google.generativeai as genai
from google.generativeai import types
from googleapiclient.discovery import build

GSEARCH_API_KEY = os.getenv("GSEARCH_API_KEY")
GSEARCH_CX_ID = os.getenv("GSEARCH_CX_ID")

def search_google(query: str):
    """
    Fungsi ini dipanggil oleh AI saat ia membutuhkan riset.
    """
    try:
        service = build("customsearch", "v1", developerKey=GSEARCH_API_KEY)
        res = service.cse().list(q=query, cx=GSEARCH_CX_ID, num=5).execute() 
        snippets = [item['snippet'] for item in res.get('items', [])]
        if not snippets:
            return "Tidak ada hasil ditemukan untuk: " + query
        return "Hasil riset untuk '" + query + "':\n" + "\n".join(snippets)
    except Exception as e:
        return f"Error saat mencari di Google: {e}"

# Daftarkan 'search_google' sebagai alat yang bisa digunakan AI
google_search_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="search_google",
            description="Mencari di Google untuk tren desain terbaru, standar coding, CDN library, atau data publik lainnya.",
            parameters={
                "type": "object", 
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Kata kunci pencarian yang spesifik"
                    }
                },
                "required": ["query"]
            }
        )
    ]
)