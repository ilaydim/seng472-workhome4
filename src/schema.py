CHATBOT_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "sql_query": {"type": "string", "description": "Generated SQL query"},
        "intent": {"type": "string", "description": "Brief intent (en/tr)"},
        "answer": {
            "type": "object",
            "properties": {
                "columns": {"type": "array", "items": {"type": "string"}},
                "rows": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["columns", "rows"]
        },
        "notes": {"type": "string", "description": "Any post-processing notes or warnings"}
    },
    "required": ["sql_query", "intent", "answer"]
}
