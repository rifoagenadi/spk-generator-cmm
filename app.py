import gradio as gr
from constants import df_empty_tasks
from part import parts, materials, update_stock, get_spk_dataframe_display, get_part_stock_dataframe_display, get_material_stock_dataframe_display, get_low_material_task_display
from task_prioritization import get_prioritized_tasks, assign_task_to_machines
import os

proposed_spk_list = [f.split('.')[0] for f in os.listdir("./proposed_spk") if f.endswith('.pdf')]
poppler_path = r'C:\PROJECT CMM\poppler-24.02.0\Library\bin'
from pdf2image import convert_from_path
for spk in proposed_spk_list:
    images = convert_from_path(f"./proposed_spk/{spk}.pdf", poppler_path=poppler_path)
    for image in images:
        image.save(f'./proposed_spk/{spk.split('.')[0]}.jpg', 'JPEG')


parts, materials = update_stock(parts, materials, env='PROD') # change env to 'PROD' to update data based on DB, else use dummy data
parts = [part for part in parts if part.is_active] # filter out inactive parts
sorted_tasks, low_material_tasks = get_prioritized_tasks(parts, top_n=200)
machine_tasks, unassigned_tasks = assign_task_to_machines(sorted_tasks)
df_spk = get_spk_dataframe_display(machine_tasks)
df_second_spk = None


def update_stock_listener():
    return gr.Button("Lihat Pratinjau", interactive=True)

def get_spk():
    global df_spk
    return df_spk, gr.Button("Simpan SPK", interactive=True)

def get_second_spk():
    global df_second_spk, unassigned_tasks
    machine_tasks_second, _ = assign_task_to_machines(unassigned_tasks)
    df_second_spk = get_spk_dataframe_display(machine_tasks_second)
    return df_second_spk, gr.Button("Simpan SPK", interactive=True)

def delete_row(evt: gr.SelectData):
    global df_spk
    if evt.value == '`DELETE`':
        row_idx, _ = evt.index
        df_spk = df_spk.drop(row_idx)
        df_spk.reset_index(drop=True, inplace=True)
    return df_spk

def delete_row_second(row_idx):
    global df_spk_second
    df_spk_second = df_spk_second.drop(row_idx-1)
    return df_spk_second

def save_spk(df, leader, year, month, day, start_hour, end_hour, shift):
    from spk_templater import create_pdf
    from datetime import datetime
    shift_id = shift.split(' ')[-1]
    file_path = f"proposed_spk/CMM-SPK-{datetime(year, month, day).strftime('%Y%m%d')}-{shift_id}.pdf"
    create_pdf(file_path, df=df, head=leader, yy=year, mm=month, dd=day, start_hour=start_hour, end_hour=end_hour, shift=shift)
    gr.Info(f"SPK telah disimpan di {file_path}")
    return gr.Button("Lihat Pratinjau", interactive=True)

def switch_proposed_spk_preview(filename):
    return gr.Image(f'proposed_spk/{filename}.jpg', type='filepath')

def approve_spk(filename):
    os.replace(f"proposed_spk/{filename}.pdf", f"approved_spk/{filename}.pdf")
    os.remove(f"proposed_spk/{filename}.jpg")
    gr.Info(f"SPK telah disetujui, file disimpan di `approved_spk/{filename}.pdf`")
    return gr.Image(f'proposed_spk/placeholder.png', type='filepath'), 'Approved'

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    with gr.Tab("SPK"):
        with gr.Tab("SPK Shift Sore"):
            preview_button = gr.Button("Lihat Pratinjau", interactive=False, render=False)
            update_stock_button = gr.Button("Update Stok")
            update_stock_button.click(update_stock_listener, outputs=[preview_button])
            submit_button = gr.Button("Simpan SPK", interactive=False, render=False)            
            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        year = gr.Number(label="Tahun", minimum=2000, maximum=2100)
                        month = gr.Number(label="Bulan", minimum=1, maximum=12)
                        day = gr.Number(label='Tanggal', minimum=1, maximum=31)
                    leader = gr.Dropdown(["Ahmad", "Bambang", "Junaedi"], label="PIC Line/Leader")
                with gr.Column():
                    with gr.Row():
                        shift = gr.Dropdown(["Shift I", "Shift II"], label="Shift")
                    with gr.Row():
                        start_hour = gr.Dropdown([f"0{i}.00" if i <= 9 else f"{i}.00" for i in range(24)], label="Jam Mulai Kerja")
                        end_hour = gr.Dropdown([f"0{i}.00" if i <= 9 else f"{i}.00" for i in range(24)], label="Jam Mulai Kerja")
            with gr.Row():
                preview_button.render()
                spk = gr.DataFrame(df_empty_tasks, interactive=True, row_count=(1, 'static'), col_count=(7, 'static'), render=False, datatype=["number", "str", "str", "str", "str", "number", "str", "markdown"])
                preview_button.click(get_spk, outputs=[spk, submit_button])
            spk.render()
            spk.select(delete_row, outputs=spk)

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
                        day_second = gr.Number(label='Tanggal', minimum=1, maximum=31)
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

            submit_button_second.render()
            submit_button_second.click(save_spk, inputs=[spk_second, leader_second, year, month, day, start_hour, end_hour, shift], outputs=preview_button_second)
        
        with gr.Tab("Approve Pengajuan SPK"):
            proposal_preview = gr.Image(interactive=False, render=False)
            proposed_spk_names_display = []
            proposed_spk_view_buttons = []
            proposed_spk_approve_buttons = []
            proposed_spk_status = []
            for i in range(len(proposed_spk_list)):
                proposed_spk_names_display.append(gr.Text(proposed_spk_list[i], render=False))
                proposed_spk_view_buttons.append(gr.Button("Lihat Pengajuan", render=False)) #TODO edit
                proposed_spk_approve_buttons.append(gr.Button("Approve", render=False))
                proposed_spk_status.append(gr.Radio(value='Pending', choices=["Approved", "Pending"], label="Status", render=False))
            for i in range(len(proposed_spk_names_display)):
                with gr.Row():
                    proposed_spk_names_display[i].render()
                    proposed_spk_view_buttons[i].render()
                    proposed_spk_view_buttons[i].click(switch_proposed_spk_preview, inputs=proposed_spk_names_display[i], outputs=[proposal_preview])
                    proposed_spk_approve_buttons[i].render()
                    proposed_spk_approve_buttons[i].click(approve_spk, inputs=[proposed_spk_names_display[i]], outputs=[proposal_preview, proposed_spk_status[i]])
                    proposed_spk_status[i].render()
            gr.Markdown("# Preview SPK")
            proposal_preview.render()
        with gr.Tab(f"Kekurangan Material"):
            gr.DataFrame(get_low_material_task_display(low_material_tasks))
            
    with gr.Tab("Stok"):
        with gr.Tab("Part"):
            part_stocks_display = gr.DataFrame(get_part_stock_dataframe_display(parts))
        with gr.Tab("Material"):
            material_stocks_display = gr.DataFrame(get_material_stock_dataframe_display(materials))

demo.launch()