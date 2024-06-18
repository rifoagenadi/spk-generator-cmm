import gradio as gr
from constants import df_empty_tasks
from part import parts, materials, update_stock, get_spk_dataframe_display, get_part_stock_dataframe_display, get_material_stock_dataframe_display

parts, materials = update_stock(parts, materials, env='DEV') # change env to 'PROD' to update data based on DB, else use dummy data
df_spk = get_spk_dataframe_display(parts)

def get_spk():
    global parts
    global df_spk
    return df_spk, gr.Button("Simpan SPK", interactive=True)       

def delete_row(row_idx):
    global df_spk
    df_spk = df_spk.drop(row_idx-1)
    return df_spk

def save_spk(df, leader, year, month, day, hour, shift):
    from spk_templater import create_pdf
    file_path = 'data/spk.pdf'
    create_pdf(file_path, df=df, head=leader, yy=year, mm=month, dd=day, workhour=hour, shift=shift)
    gr.Info(f"SPK telah disimpan di {file_path}")
    
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    with gr.Tab("SPK"):
        submit_button = gr.Button("Simpan SPK", interactive=False, render=False)            
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    year = gr.Number(label="Tahun", minimum=2000, maximum=2100)
                    month = gr.Number(label="Bulan", minimum=1, maximum=12)
                    day = gr.Number(label='Hari', minimum=1, maximum=31)
                leader = gr.Dropdown(["Ahmad", "Bambang", "Junaedi"], label="PIC Line/Leader")
            with gr.Column():
                with gr.Row():
                    shift = gr.Dropdown(["Shift I", "Shift II"], label="Shift")
                hour = gr.Dropdown(["08.00 - 17.00", "20.00 - 05.00",], label="Jam Kerja")
        with gr.Row():
            preview_button = gr.Button("Lihat Pratinjau")
            spk = gr.DataFrame(df_empty_tasks, interactive=True, col_count=(7, 'static'),  render=False)
            preview_button.click(get_spk, outputs=[spk, submit_button])
        spk.render()
        with gr.Row():
            row_to_delete = gr.Number(minimum=1, label="No. Baris yang hendak dihapus")
            delete_button = gr.Button("Hapus")
            delete_button.click(delete_row, inputs=row_to_delete, outputs=spk)

        submit_button.render()
        submit_button.click(save_spk, inputs=[spk, leader, year, month, day, hour, shift])
        
    with gr.Tab("Stok"):
        with gr.Tab("Part"):
            part_stocks_display = gr.DataFrame(get_part_stock_dataframe_display(parts))
        with gr.Tab("Material"):
            material_stocks_display = gr.DataFrame(get_material_stock_dataframe_display(materials))

demo.launch()