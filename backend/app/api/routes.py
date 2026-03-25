# app/api/routes.py

from fastapi import APIRouter
from sqlalchemy import create_engine
import pandas as pd

router = APIRouter()

engine = create_engine("sqlite:///./business.db")

@router.get("/graph")
def get_graph():
    df = pd.read_sql("SELECT * FROM invoices LIMIT 5000", engine)

    # ✅ filter valid invoices
    df = df[df["id"].notna()]

    nodes = []
    edges = []
    added_nodes = set()

    for _, row in df.iterrows():

        invoice_id = str(row["id"])

        customer_id = row.get("customer_id") or row.get("customer")
        order_id = row.get("salesorder") or row.get("order_id")

        # ---------------- INVOICE ----------------
        if invoice_id not in added_nodes:
            nodes.append({
                "id": f"invoice_{invoice_id}",
                "type": "invoice",
                "data": {"label": f"Invoice {invoice_id}"}
            })
            added_nodes.add(invoice_id)

        # ---------------- CUSTOMER ----------------
        if pd.notna(customer_id):
            customer_id = str(customer_id)

            if customer_id not in added_nodes:
                nodes.append({
                    "id": f"customer_{customer_id}",
                    "type": "customer",
                    "data": {"label": f"Customer {customer_id}"}
                })
                added_nodes.add(customer_id)

            edges.append({
                "id": f"cust_{invoice_id}",
                "source": f"customer_{customer_id}",
                "target": f"invoice_{invoice_id}"
            })

        # ---------------- ORDER ----------------
        if pd.notna(order_id):
            order_id = str(order_id)

            if order_id not in added_nodes:
                nodes.append({
                    "id": f"order_{order_id}",
                    "type": "order",
                    "data": {"label": f"Order {order_id}"}
                })
                added_nodes.add(order_id)

            edges.append({
                "id": f"order_{invoice_id}",
                "source": f"order_{order_id}",
                "target": f"invoice_{invoice_id}"
            })

    # remove duplicates
    edges = list({(e['source'], e['target']): e for e in edges}.values())

    return {
        "nodes": nodes,
        "edges": edges
    }