def generate_sql(question, schema):
    q = question.lower()

    # 🚫 guardrails
    if any(word in q for word in ["joke", "weather", "who is", "movie", "song"]):
        return "INVALID"

    if "top" in q and "customer" in q:
        return """
        SELECT customer_id, SUM(totalnetamount) as total
        FROM invoices
        GROUP BY customer_id
        ORDER BY total DESC
        LIMIT 5
        """

    if "total billing" in q:
        return """
        SELECT SUM(totalnetamount) as total_billing
        FROM invoices
        """

    if "all invoices" in q:
        return "SELECT * FROM invoices LIMIT 10"

    return "INVALID"


# ✅ ADD THIS FUNCTION (THIS WAS MISSING)
def generate_answer(question, sql, result):
    return f"Query executed successfully. Returned {len(result)} rows."