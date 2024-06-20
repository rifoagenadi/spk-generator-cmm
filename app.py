import gradio as gr
from constants import df_empty_tasks
from part import parts, materials, update_stock, get_spk_dataframe_display, get_part_stock_dataframe_display, get_material_stock_dataframe_display
from task_prioritization import get_prioritized_tasks, assign_task_to_machines

parts, materials = update_stock(parts, materials, env='DEV') # change env to 'PROD' to update data based on DB, else use dummy data
sorted_tasks = get_prioritized_tasks(parts, top_n=200)
machine_tasks, unassigned_tasks = assign_task_to_machines(sorted_tasks)
df_spk = get_spk_dataframe_display(machine_tasks)
df_second_spk = None

def get_spk():
    global df_spk
    return df_spk, gr.Button("Simpan SPK", interactive=True)

def get_second_spk():
    global df_second_spk, unassigned_tasks
    machine_tasks_second, _ = assign_task_to_machines(unassigned_tasks)
    df_second_spk = get_spk_dataframe_display(machine_tasks_second)
    return df_second_spk, gr.Button("Simpan SPK", interactive=True)

def delete_row(row_idx):
    global df_spk
    df_spk = df_spk.drop(row_idx-1)
    return df_spk

def delete_row_second(row_idx):
    global df_spk_second
    df_spk_second = df_spk_second.drop(row_idx-1)
    return df_spk_second

def save_spk(df, leader, year, month, day, start_hour, end_hour, shift):
    from spk_templater import create_pdf
    from datetime import datetime
    shift_id = shift.split(' ')[-1]
    file_path = f"data/CMM-SPK-{datetime(year, month, day).strftime('%Y%m%d')}-{shift_id}.pdf"
    create_pdf(file_path, df=df, head=leader, yy=year, mm=month, dd=day, start_hour=start_hour, end_hour=end_hour, shift=shift)
    gr.Info(f"SPK telah disimpan di {file_path}")
    return gr.Button("Lihat Pratinjau", interactive=True)
    
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    with gr.Tab("SPK"):
        with gr.Tab("SPK Shift Sore"):
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
                    with gr.Row():
                        start_hour = gr.Dropdown([f"0{i}.00" if i <= 9 else f"{i}.00" for i in range(24)], label="Jam Mulai Kerja")
                        end_hour = gr.Dropdown([f"0{i}.00" if i <= 9 else f"{i}.00" for i in range(24)], label="Jam Mulai Kerja")
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
            preview_button_second = gr.Button("Lihat Pratinjau", interactive=False, render=False)
            submit_button.click(save_spk, inputs=[spk, leader, year, month, day, start_hour, end_hour, shift], outputs=[preview_button_second])
        
        with gr.Tab(f"SPK Shift Pagi"):
            submit_button_second = gr.Button("Simpan SPK", interactive=False, render=False)            
            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        year_second = gr.Number(label="Tahun", minimum=2000, maximum=2100)
                        month_second = gr.Number(label="Bulan", minimum=1, maximum=12)
                        day_second = gr.Number(label='Hari', minimum=1, maximum=31)
                    leader_second = gr.Dropdown(["Ahmad", "Bambang", "Junaedi"], label="PIC Line/Leader")
                with gr.Column():
                    with gr.Row():
                        shift_second = gr.Dropdown(["Shift I", "Shift II"], label="Shift")
                    with gr.Row():
                        start_hour_second = gr.Dropdown([f"0{i}.00" if i <= 9 else f"{i}.00" for i in range(24)], label="Jam Mulai Kerja")
                        end_hour_second = gr.Dropdown([f"0{i}.00" if i <= 9 else f"{i}.00" for i in range(24)], label="Jam Mulai Kerja")
            with gr.Row():
                preview_button_second.render()
                spk_second = gr.DataFrame(df_empty_tasks, interactive=True, col_count=(7, 'static'),  render=False)
                preview_button_second.click(get_second_spk, outputs=[spk_second, submit_button_second])
            spk_second.render()
            with gr.Row():
                row_to_delete_second = gr.Number(minimum=1, label="No. Baris yang hendak dihapus")
                delete_button_second = gr.Button("Hapus")
                delete_button_second.click(delete_row_second, inputs=row_to_delete_second, outputs=spk_second)

            submit_button_second.render()
            submit_button_second.click(save_spk, inputs=[spk_second, leader_second, year, month, day, start_hour, end_hour, shift], outputs=preview_button_second)
            
    with gr.Tab("Stok"):
        with gr.Tab("Part"):
            part_stocks_display = gr.DataFrame(get_part_stock_dataframe_display(parts))
        with gr.Tab("Material"):
            material_stocks_display = gr.DataFrame(get_material_stock_dataframe_display(materials))

demo.launch()