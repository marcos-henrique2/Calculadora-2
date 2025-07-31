import io
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def create_budget_pdf(client_name, quote_items):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # --- Cabeçalho (sem alterações) ---
    c.setFont("Helvetica-Bold", 24)
    c.drawString(72, height - 72, "ORÇAMENTO")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, height - 100, "MALLKI PRINT")
    c.setFont("Helvetica", 10)
    c.drawString(72, height - 130, f"Cliente: {client_name}")
    c.drawString(72, height - 145, f"Data: {datetime.now().strftime('%d/%m/%Y')}")

    # --- Tabela de Itens ---
    table_data = [
        ["Qtd.", "Descrição", "Material", "Peso est.un/g", "Tempo \nem horas", "Pintura \nmanual", "Valor"]
    ]
    
    total_price = 0
    for item in quote_items:
        price = item.get('final_price', 0)
        table_data.append([
            item.get('quantity', 1),
            item.get('item_name', 'N/A'),
            item.get('material_type', 'N/A'),
            f"{item.get('weight_g', 0):.2f}g",
            f"{item.get('print_hours', 0):.1f}h",
            item.get('painting', 'Não'),
            f"R$ {price:.2f}"
        ])
        total_price += price

    # --- AJUSTE NA LARGURA DAS COLUNAS ---
    # Diminuímos a "Descrição" de 2.2 para 1.8 polegadas e redistribuímos o espaço.
    item_table = Table(table_data, colWidths=[0.6*inch, 1.8*inch, 0.9*inch, 1*inch, 1*inch, 1*inch, 0.9*inch])
    
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTSIZE', (0,1), (-1,-1), 9),
    ])
    item_table.setStyle(style)

    # Desenha a tabela no PDF
    table_width, table_height = item_table.wrapOn(c, width, height)
    item_table.drawOn(c, 40, height - 170 - table_height)

    # --- Rodapé Completo (sem alterações) ---
    y_position = height - 190 - table_height
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, y_position, f"Total: R$ {total_price:.2f}")
    c.setFont("Helvetica", 10)
    y_position -= 30
    c.drawString(72, y_position, "Pagamento: 40% junto ao pedido e 60% na entrega")
    y_position -= 15
    c.drawString(72, y_position, "Prazo: 7 Dias Úteis")
    c.setFont("Helvetica-Oblique", 10)
    y_position -= 50
    signature_x_start = (width / 2) - 100
    c.drawString(signature_x_start, y_position, "_".center(40))
    y_position -= 15
    c.drawCentredString(width / 2, y_position, "Anna Vitória")
    y_position -= 12
    c.drawCentredString(width / 2, y_position, "Orçamentista")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer