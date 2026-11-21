def invoice_email(customer_email, total):
    return {"to": customer_email, "subject": "Your invoice", "body": f"Total: {total}"}
