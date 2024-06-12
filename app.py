import gradio as gr
from constants import parts, tonnage2name
from utils import get_prioritized_tasks, assign_task_to_machines
import pandas as pd

df_parts = pd.DataFrame({
    "No": [i+1 for i, _ in enumerate(parts)],
    "Part": [part.name for part in parts],
    "Customer": [part.customer for part in parts],
    "Stok WIP": [','.join([f"{process.process_name}: {process.stock}" for process in part.processes[:-1]]) for part in parts],
    "Stok FIN": [part.processes[-1].stock for part in parts],
    "3HK": [part.ideal_stock_3hk for part in parts],
    "Status": ["Stok OK" if part.processes[-1].stock >= part.ideal_stock_3hk else "Stok Kurang" for part in parts]
})

sorted_tasks = get_prioritized_tasks(parts, top_n=200)
df_prioritization = pd.DataFrame({
    "No": [i+1 for i in range(len(sorted_tasks))],
    "Part Name": [task.part_name for task in sorted_tasks],
    "Process Name": [task.process_name for task in sorted_tasks],
    "Quantity": [task.quantity for task in sorted_tasks],
    "Kekurangan": [task.necessity for task in sorted_tasks],
    "Material Spec Size": [task.material if task.process_name == 'Blank' else '' for task in sorted_tasks]
})
machine_tasks = assign_task_to_machines(sorted_tasks)
tasks = [(tonnage_idx, task) for tonnage_idx, tasks_ in enumerate(machine_tasks) for task in tasks_]

from datetime import datetime
current_date = datetime.now()
formatted_date = current_date.strftime("%m/%d/%Y")

df_tasks = pd.DataFrame({
    "No": [i+1 for i in range(len(tasks))],
    "Mesin": [tonnage2name[tonnage_idx] for tonnage_idx, _ in tasks],
    "Part Name": [task.part_name for _, task in tasks],
    "Process Name": [task.process_name for _, task in tasks],
    "OP": [task.op for _, task in tasks],
    "Quantity": [task.quantity for _, task in tasks],
    "Material Spec Size": [task.material if task.process_name == 'Blank' else '' for _, task in tasks]
})


def get_spk():
    return df_tasks

def update_stock():
    #TODO, update stok dari DB based on hasil produksi dan delivery hari ini
    #TODO, enable tombol download pdf spk
    return gr.Button("Unduh SPK", interactive=True)

def delete_row(row_idx):
    global df_tasks
    df_tasks = df_tasks.drop(row_idx-1)
    return df_tasks

def save_spk():
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    file_path = 'data/spk.pdf'
    c = canvas.Canvas(file_path, pagesize=letter)

    c.drawString(100, 750, "SPK PT CMM")

    c.save()
    gr.Info(f"SPK telah disimpan di {file_path}")
    
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    df_empty_tasks = pd.DataFrame({
        "No": [],
        "Mesin": [],
        "Part Name": [],
        "Process Name": [],
        "OP": [],
        "Quantity": [],
        "Material Spec Size": []
    })  
    with gr.Tab("SPK"):
        with gr.Tab("Buat SPK"):
            update_stock_button = gr.Button("Update Stok")
            submit_button = gr.Button("Simpan SPK", interactive=False, render=False)
            update_stock_button.click(update_stock, outputs=submit_button)
            with gr.Row():
                with gr.Column():
                    production_date = gr.Text(formatted_date, label="Tanggal Produksi", interactive=False)
                    leader = gr.Dropdown(["Ahmad", "Bambang", "Junaedi"], label="PIC Line/Leader")
                with gr.Column():
                    shift = gr.Dropdown(["Shift I", "Shift II"], label="Shift")
                    hour = gr.Dropdown(["08.00 - 17.00", "20.00 - 05.00",], label="Jam Kerja")
            with gr.Row():
                preview_button = gr.Button("Lihat Pratinjau")
                spk = gr.DataFrame(df_empty_tasks, interactive=True, col_count=(7, 'static'),  render=False)
                preview_button.click(get_spk, outputs=spk)
            spk.render()
            with gr.Row():
                row_to_delete = gr.Number(minimum=1, maximum=len(tasks), label="No. Baris yang hendak dihapus")
                delete_button = gr.Button("Hapus")
                delete_button.click(delete_row, inputs=row_to_delete, outputs=spk)

            submit_button.render()
            submit_button.click(save_spk)

        with gr.Tab("Prioritas Produksi"):
            gr.DataFrame(df_prioritization)
        
    with gr.Tab("Status Ketersediaan Part"):
        gr.DataFrame(df_parts, row_count=df_parts.shape[0], interactive=True)

demo.launch()