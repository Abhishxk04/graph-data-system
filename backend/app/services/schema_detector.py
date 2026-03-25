def detect_foreign_keys(tables):
    relationships = []

    for table_name, df in tables.items():
        cols = df.columns

        if "customer_id" in cols:
            relationships.append({
                "from_table": table_name,
                "from_column": "customer_id",
                "to_table": "customers",
                "to_column": "id"
            })

        if "order_id" in cols:
            relationships.append({
                "from_table": table_name,
                "from_column": "order_id",
                "to_table": "orders",
                "to_column": "id"
            })

        if "invoice_id" in cols:
            relationships.append({
                "from_table": table_name,
                "from_column": "invoice_id",
                "to_table": "invoices",
                "to_column": "id"
            })

    return relationships