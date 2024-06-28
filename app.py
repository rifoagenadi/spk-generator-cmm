import gradio as gr
from constants import df_empty_tasks
from part import (parts, materials,
                update_stock, get_spk_dataframe_display,
                get_part_stock_dataframe_display,
                get_material_stock_dataframe_display,
                get_low_material_task_display)
from task_prioritization import get_prioritized_tasks, assign_task_to_machines

parts, materials = update_stock(parts, materials, env='DEV') # change env to 'PROD' to update data based on DB, else use dummy data
parts = [part for part in parts if part.is_active] # filter out inactive parts
sorted_tasks, low_material_tasks = get_prioritized_tasks(parts, top_n=200)
machine_tasks, unassigned_tasks = assign_task_to_machines(sorted_tasks)
df_spk = get_spk_dataframe_display(machine_tasks)
df_second_spk = None

from event_listeners import *
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

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    proposed_spk_list = gr.State(value=[])
    with gr.Row():
        credential = gr.State(value=None)
        username = gr.Text(label="Username")
        password = gr.Text(label='Password', type='password')
        login_button = gr.Button("Login")
        login_button.click(get_credential, inputs=[username, password], outputs=credential)
    with gr.Tab("SPK"):
        with gr.Tab("Shift II (Today)"):
            preview_button = gr.Button("Lihat Pratinjau", interactive=False, render=False)
            update_stock_button = gr.Button("Update Stok")
            update_stock_button.click(update_stock_listener, inputs=credential, outputs=[preview_button])
            submit_button = gr.Button("Simpan SPK", interactive=False, render=False)            
            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        year = gr.Number(label="Tahun", minimum=2000, maximum=2100)
                        month = gr.Dropdown(label="Bulan", choices=['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'])
                        day = gr.Dropdown(label="Bulan", choices=[i+1 for i in range(31)])
                    leader = gr.Dropdown(["Ahmad", "Bambang", "Junaedi"], label="PIC Line/Leader")
                with gr.Column():
                    with gr.Row():
                        shift = gr.Dropdown(value="Shift II", choices=["Shift I", "Shift II"], label="Shift", interactive=False)
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
            submit_button.click(save_spk, inputs=[spk, leader, year, month, day, start_hour, end_hour, shift, proposed_spk_list], outputs=[preview_button_second, proposed_spk_list])
        
        with gr.Tab(f"Shift I (Tomorrow)"):
            submit_button_second = gr.Button("Simpan SPK", interactive=False, render=False)            
            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        year_second = gr.Number(label="Tahun", minimum=2000, maximum=2100)
                        month_second = gr.Dropdown(label="Bulan", choices=['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'])
                        day_second = gr.Dropdown(label="Tanggal", choices=[i+1 for i in range(31)])
                    leader_second = gr.Dropdown(["Ahmad", "Bambang", "Junaedi"], label="PIC Line/Leader")
                with gr.Column():
                    with gr.Row():
                        shift_second = gr.Dropdown(value="Shift I", choices=["Shift I", "Shift II"], label="Shift", interactive=False)
                    with gr.Row():
                        start_hour_second = gr.Dropdown([f"0{i}.00" if i <= 9 else f"{i}.00" for i in range(24)], label="Jam Mulai Kerja")
                        end_hour_second = gr.Dropdown([f"0{i}.00" if i <= 9 else f"{i}.00" for i in range(24)], label="Jam Mulai Kerja")
            with gr.Row():
                preview_button_second.render()
                spk_second = gr.DataFrame(df_empty_tasks, interactive=True, col_count=(7, 'static'),  render=False)
                preview_button_second.click(get_second_spk, outputs=[spk_second, submit_button_second])
            spk_second.render()

            submit_button_second.render()
            submit_button_second.click(save_spk, inputs=[spk_second, leader_second, year_second, month_second, day_second, start_hour_second, end_hour_second, shift_second, proposed_spk_list], outputs=[preview_button_second, proposed_spk_list])
        
        with gr.Tab("Approve Pengajuan SPK"):
            proposal_preview = gr.Image(interactive=False, render=False)
            @gr.render(inputs=proposed_spk_list)
            def render_spk_proposal(proposed_spk_list):
                proposed_spk_names_display = []
                proposed_spk_view_buttons = []
                proposed_spk_approve_buttons = []
                proposed_spk_reject_buttons = []
                proposed_spk_status = []
                for i in range(len(proposed_spk_list)):
                    proposed_spk_names_display.append(gr.Text(proposed_spk_list[i], render=False, label="No. SPK"))
                    proposed_spk_view_buttons.append(gr.Button("Lihat Pengajuan SPK", render=False)) #TODO edit
                    proposed_spk_approve_buttons.append(gr.Button("Approve", render=False))
                    proposed_spk_reject_buttons.append(gr.Button("Reject", render=False))
                    proposed_spk_status.append(gr.Radio(value='Pending', choices=["Approved", "Pending"], label="Status", render=False))
                for i in range(len(proposed_spk_names_display)):
                    with gr.Row():
                        proposed_spk_names_display[i].render()
                        proposed_spk_view_buttons[i].render()
                        proposed_spk_view_buttons[i].click(switch_proposed_spk_preview, inputs=proposed_spk_names_display[i], outputs=[proposal_preview])
                        with gr.Column():
                            proposed_spk_approve_buttons[i].render()
                            proposed_spk_reject_buttons[i].render()
                            proposed_spk_approve_buttons[i].click(approve_spk, inputs=[proposed_spk_names_display[i]], outputs=[proposal_preview, proposed_spk_status[i]])
                        proposed_spk_status[i].render()
            gr.Markdown("# Preview SPK")
            proposal_preview.render()
        with gr.Tab(f"Kekurangan Material"):
            df_low_material_task = gr.DataFrame(get_low_material_task_display(low_material_tasks))
            part_stocks_export_button = gr.Button("Export to Excel")
            part_stocks_export_button.click(export_material_necessity_to_excel, inputs=[df_low_material_task])
            
    with gr.Tab("Stok"):
        with gr.Tab("Part"):
            part_stocks_display = gr.DataFrame(get_part_stock_dataframe_display(parts))
            material_stocks_display = gr.DataFrame(get_material_stock_dataframe_display(materials), render=False)
            part_stocks_export_button = gr.Button("Export to Excel")
            part_stocks_export_button.click(export_stock_to_excel, inputs=[part_stocks_display, material_stocks_display])
        with gr.Tab("Material"):
            material_stocks_display.render()

demo.launch()