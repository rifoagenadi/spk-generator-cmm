from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle
import qrcode

# Function to generate and save a QR code
def generate_qr_code(data, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    img.save(filename)

# Create a function to generate the PDF
from constants import MONTH_ID_TO_NAME
def create_pdf(filename, df, head, yy, mm, dd, start_hour, end_hour, shift):
    c = canvas.Canvas(filename, pagesize=landscape(A4))  # Set pagesize to landscape
    
    # Set up the font and size
    c.setFont('Helvetica', size=8)
    
    c.drawImage('data/logo_cmm.png', 20, 500, width=75, height=75)
    # Set the starting point for text
    left_fields = [
        ["KEPALA BAGIAN", '=', head],
        ["TANGGAL", '=', f'{dd}-{MONTH_ID_TO_NAME[int(mm)-1]}-{yy}'],
        ["JAM KERJA", '=', f"{start_hour} - {end_hour}"]
    ]
    y = 550
    for field in left_fields:
        x = 100
        for part in field:
            c.drawString(x, y, part)
            if x == 100:
                x += 100
            else:
                x += 20
        y -= 15  # Move y-coordinate up for the next line

    c.setFont('Helvetica-Bold', size=16)
    from datetime import datetime
    shift_id = shift.split(' ')[-1]
    middle_fields = ["SURAT PERINTAH KERJA", f"CMM-SPK-{datetime(yy, mm, dd).strftime('%Y%m%d')}-{shift_id}", shift]
    y = 570
    x = 300
    for field in middle_fields:
        c.drawString(x, y, field)
        if y == 570:
            c.setFont('Helvetica-Bold', size=10)
            x += 55
            y -= 20
        else:
            x += 35
            y -= 15

    c.setFont('Helvetica', size=8)
    right_fields = [
        ["NOMOR", '=', 'FR-CMM-PPIC-001'],
        ["REVISI", '=', '1'],
        ["BERLAKU TANGGAL", '=', '29 MARET 2021']
    ]
    y = 550
    for field in right_fields:
        x = 550
        for part in field:
            c.drawString(x, y, part)
            if x == 550:
                x += 100
            else:
                x += 20
        y -= 15  # Move y-coordinate up for the next line
    
    # Example usage:
    data = middle_fields[1] # Replace with your data (URL, text, etc.)
    filename = "data/qr.png"  # Output file name
    generate_qr_code(data, filename)

    c.drawImage('data/qr.png', 750, 500, width=75, height=75)

    df = df.fillna('')
    values = df.values.tolist()
    values = [val[:6] + ['', '', ''] + val[-1:] + [''] for val in values]
    num_of_tasks_for_each_machine = []
    prev_machine = values[0][1]
    current_n_task = 1
    for i in range(1, len(values)):
        if values[i][1] == prev_machine:
            current_n_task += 1
        else:
            num_of_tasks_for_each_machine.append(current_n_task)
            current_n_task = 1
        prev_machine = values[i][1]
    num_of_tasks_for_each_machine.append(current_n_task)

    idx_pointer = 0
    idx = 1 # machine no, start from 1
    for n_task in num_of_tasks_for_each_machine:
        for _ in range(n_task):
            values[idx_pointer][0] = idx
            idx_pointer += 1
        idx += 1
        
    data = [
        ['NO', 'MESIN', 'PART NAME', 'PROSES', 'PROSES','QTY\nPCS', 'REALISASI', 'REALISASI', 'REALISASI', 'MATL SPEC SIZE', 'KETERANGAN'],
        ['NO', 'MESIN', 'PART NAME', 'PROSES', 'PROSES','QTY\nPCS', 'OK', 'NG', 'TRY', 'MATL SPEC SIZE', 'KETERANGAN'],
    ]
    data.extend(values)

    widths = [20, 80, 260, 60, 35, 35, 25, 25, 25, 140, 120]
    table = Table(data, colWidths=widths, rowHeights=15)
    table_style = [
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add border to all cells
        ('SPAN', (0, 0), (0, 1)),  # Merge cells A1 (first column, first row) and A2 (first column, second row)
        ('SPAN', (1, 0), (1, 1)),  # Merge cells B1 (second column, first row) and B2 (second column, second row)
        ('SPAN', (2, 0), (2, 1)),
        ('SPAN', (3, 0), (4, 1)),
        ('SPAN', (5, 0), (5, 1)),
        ('SPAN', (6, 0), (8, 0)),
        ('SPAN', (9, 0), (9, 1)),
        ('SPAN', (10, 0), (10, 1)),
        ('ALIGN', (0, 0), (-1, 1), 'CENTER'),  # Align all cells to center horizontally
        ('VALIGN', (0, 0), (-1, 1), 'MIDDLE'),  # Vertically align all cells to middle
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 2), (1, -1), 'TOP'),  # Vertically first two column to top
    ]

    DATA_FIRST_ROW = 2
    COL_TO_MERGE = [0, 1]
    merge_cells = []
    for col in COL_TO_MERGE:
        row_pointer = DATA_FIRST_ROW
        for n_task in num_of_tasks_for_each_machine:
            left_boundary = (col, row_pointer)
            right_boundary = (col, row_pointer+n_task-1)
            if left_boundary != right_boundary:
                current_styling = ('SPAN', left_boundary, right_boundary)
                merge_cells.append(current_styling)
            row_pointer += n_task

    COL_TO_REMOVE_LINE = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    remove_bottom_lines = []
    for col in COL_TO_REMOVE_LINE:
        row_pointer = DATA_FIRST_ROW
        for n_task in num_of_tasks_for_each_machine:
            for i in range(n_task-1):
                current_styling = ('LINEBELOW', (col, row_pointer+i), (col, row_pointer+i), 0, colors.white)
                remove_bottom_lines.append(current_styling)
            row_pointer += n_task

    add_right_lines = [('LINEAFTER', (i, j), (i, j), 1, colors.black) for i in range(2, 12) for j in range(2, len(values)+2)]
    style = TableStyle(table_style+merge_cells+remove_bottom_lines+add_right_lines)
    table.setStyle(style)

    table.wrapOn(c, 600, 500)  # Adjust the width and height as needed
    table.drawOn(c, 10, 100)   # Position the table on the page (72 dpi margin)

    c.setFont('Helvetica', size=6)
    c.drawString(20, 70, "Note")
    c.drawString(20, 60, "1. Dilakukan sesuai urutan pada setiap mesin")
    c.drawString(20, 50, "2. Apabila terjadi kendala pada tools/mesin segera informasikan kepada bagian PPIC")
    c.drawString(20, 40, "3. Loading dapat berubah apabila ada barang urgent")
    c.rect(10, 30, 270, 50)

    c.setFont('Helvetica', size=10)
    c.drawString(680, 75, "APPD")
    c.drawString(750, 75, "DRAFT")
    c.rect(660, 65, 70, 20)
    c.rect(730, 65, 70, 20)
    c.rect(660, 30, 70, 35)
    c.rect(730, 30, 70, 35)

    # Save the PDF
    c.save()
 