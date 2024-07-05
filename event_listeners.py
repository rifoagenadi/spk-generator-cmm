import gradio as gr
from constants import uname_and_pass2credential
import os
import pandas as pd

base_path = r'C:\Users\AZKA\Downloads\spk_generator_output' 
# base_path = '/Users/bebek/Downloads/spk_generator_output'
def get_credential(username, password):
    uname_and_pass = (username, password)
    if uname_and_pass in uname_and_pass2credential:
        gr.Info(f"Login Berhasil, {username.upper()}: {uname_and_pass2credential[uname_and_pass].upper()}")
        return uname_and_pass2credential[uname_and_pass]
    elif username == '' or password == '':
        gr.Warning("Mohon masukkan username dan password untuk melanjutkan")
        return None
    else:
        gr.Warning("Username atau password salah")
        return None

def export_material_necessity_to_excel(df):
    excel_writer = pd.ExcelWriter(f'{base_path}/kekurangan_material.xlsx', engine='xlsxwriter')

    # Write each DataFrame to a specific sheet.
    df.to_excel(excel_writer, sheet_name='Sheet1', index=False)

    # Close the Pandas Excel writer and output the Excel file.
    gr.Info(f"SPK telah disimpan di {base_path}/kekurangan_material.xlsx")
    excel_writer.close()


def export_stock_to_excel(df_parts_stock, df_materials_stock):
    excel_writer = pd.ExcelWriter(f'{base_path}/stok.xlsx', engine='xlsxwriter')

    # Write each DataFrame to a specific sheet.
    df_parts_stock.to_excel(excel_writer, sheet_name='Stok Part', index=False)
    df_materials_stock.to_excel(excel_writer, sheet_name='Stok Material', index=False)

    # Close the Pandas Excel writer and output the Excel file.
    gr.Info(f"SPK telah disimpan di {base_path}/stok.xlsx")
    excel_writer.close()

def convert_pdf_to_image():
    proposed_spk_list = [f.split('.')[0] for f in os.listdir(f"{base_path}/proposed_spk") if f.endswith('.pdf')]
    poppler_path = r'C:\PROJECT CMM\poppler-24.02.0\Library\bin'
    from pdf2image import convert_from_path
    for spk in proposed_spk_list:
        # images = convert_from_path(f"{base_path}/proposed_spk/{spk}.pdf")
        images = convert_from_path(f"{base_path}/proposed_spk/{spk}.pdf", poppler_path=poppler_path)
        for image in images:
            image.save(f'{base_path}/proposed_spk/{spk.split('.')[0]}.jpg', 'JPEG')

async def save_spk(df, leader, date, start_hour, end_hour, shift, proposed_spk_list):
    from spk_templater import create_pdf
    import pickle as pkl
    shift_id = shift.split(' ')[-1]
    spk_no = f"CMM-SPK-{date.strftime('%Y%m%d')}-{shift_id}"
    file_path = f"{base_path}/proposed_spk/{spk_no}.pdf"
    create_pdf(file_path, df=df, head=leader, date=date, start_hour=start_hour, end_hour=end_hour, shift=shift)
    convert_pdf_to_image()
    pkl.dump(df, open(f"{base_path}/proposed_spk/{spk_no}.pickle", 'wb'))
    gr.Info(f"SPK telah disimpan di {file_path}")
    if spk_no not in proposed_spk_list:
        proposed_spk_list.append(spk_no)
    return gr.Button("Lihat Pratinjau", interactive=True), proposed_spk_list, gr.Button("Tambah", interactive=True)

def switch_proposed_spk_preview(filename):
    return gr.Image(f'{base_path}/proposed_spk/{filename}.jpg', type='filepath')

def switch_approved_spk_preview(filename):
    return gr.Image(f'{base_path}/approved_spk/{filename}.jpg', type='filepath')

def approve_spk(filename, credential, proposed_spk_list, approved_spk_list):
    if credential == 'supervisor':
        os.replace(f"{base_path}/proposed_spk/{filename}.pdf", f"{base_path}/approved_spk/{filename}.pdf")
        os.replace(f"{base_path}/proposed_spk/{filename}.jpg", f"{base_path}/approved_spk/{filename}.jpg")
        os.remove(f"{base_path}/proposed_spk/{filename}.pickle")
        gr.Info(f"SPK telah disetujui, file disimpan di `approved_spk/{filename}.pdf`")
        proposed_spk_list.remove(filename)
        approved_spk_list.append(filename)
        return gr.Image(f'proposed_spk/placeholder.png', type='filepath'), proposed_spk_list, approved_spk_list
    else:
        gr.Warning("Hanya Supervisor yang dapat menyetujui pengajuan SPK")
        return gr.Image(f'proposed_spk/placeholder.png', type='filepath'), proposed_spk_list, approved_spk_list

def reject_spk(filename, credential, proposed_spk_list, rejected_spk_list):
    if credential == 'supervisor':
        os.replace(f"{base_path}/proposed_spk/{filename}.pdf", f"{base_path}/rejected_spk/{filename}.pdf")
        os.replace(f"{base_path}/proposed_spk/{filename}.pickle", f"{base_path}/rejected_spk/{filename}.pickle")
        os.remove(f"{base_path}/proposed_spk/{filename}.jpg")
        gr.Info(f"SPK telah disetujui, file disimpan di `rejected_spk/{filename}.pdf`")
        proposed_spk_list.remove(filename)
        rejected_spk_list.append(filename)
        return gr.Image(f'proposed_spk/placeholder.png', type='filepath'), proposed_spk_list, rejected_spk_list
    else:
        gr.Warning("Hanya Supervisor yang dapat menolak pengajuan SPK")