import gradio as gr
from gradio_modal import Modal
from constants import df_empty_tasks, tonnage2name
from part import (parts, materials, 
                formatted_part_names, process_names,
                update_stock, get_spk_dataframe_display,
                get_part_stock_dataframe_display,
                get_material_stock_dataframe_display,
                get_low_material_task_display)
from task_prioritization import get_prioritized_tasks, assign_task_to_machines
import os

parts, materials = update_stock(parts, materials, env='DEV') # change env to 'PROD' to update data based on DB, else use dummy data
parts = [part for part in parts if part.is_active] # filter out inactive parts
sorted_tasks, low_material_tasks = get_prioritized_tasks(parts, top_n=200)
machine_tasks, unassigned_tasks = assign_task_to_machines(sorted_tasks)
df_spk = get_spk_dataframe_display(machine_tasks)
df_second_spk = None

proposed_spk_initial_state = [f.split('.')[0] for f in os.listdir("outputs/proposed_spk") if f.endswith('.pdf')]
approved_spk_initial_state = [f.split('.')[0] for f in os.listdir("outputs/approved_spk") if f.endswith('.pdf')]
rejected_spk_initial_state = [f.split('.')[0] for f in os.listdir("outputs/rejected_spk") if f.endswith('.pdf')]

from event_listeners import *
def get_spk(credential):
    if credential == 'ppic':
        global df_spk
        return df_spk, gr.Button("Simpan SPK", interactive=True), gr.Button("Tambah", interactive=True)
    else:
        gr.Warning("Perlu login terlebih dahulu.")
        return df_empty_tasks, gr.Button("Simpan SPK", interactive=False), gr.Button("Tambah", interactive=False)

def get_second_spk():
    global df_second_spk, unassigned_tasks
    machine_tasks_second, _ = assign_task_to_machines(unassigned_tasks)
    df_second_spk = get_spk_dataframe_display(machine_tasks_second)
    return df_second_spk, gr.Button("Simpan SPK", interactive=True)

def spk_select_listener(evt: gr.SelectData):
    if evt.value == '`DELETE`':
        row_idx, _ = evt.index
        return row_idx, Modal(visible=True)
    else:
        return None, Modal(visible=False)

def delete_row(row_idx):
    global df_spk

    df_spk = df_spk.drop(row_idx)
    df_spk.reset_index(drop=True, inplace=True)
    return df_spk, Modal(visible=False)

def append_new_task(new_task_machine, new_task_part_name, new_task_process_name, new_task_quantity, new_task_material_spec_size, new_op):
    global df_spk
    new_row = {
        "No": df_spk.shape[0] + 1,
        "Mesin": new_task_machine,
        "Part Name": new_task_part_name,
        "Process Name": new_task_process_name,
        "OP": new_op,
        "Quantity": new_task_quantity,
        "Material Spec Size": new_task_material_spec_size,
        "Delete": '`DELETE`'
    }

    df_spk = df_spk._append(new_row, ignore_index=True)
    return df_spk, Modal(visible=True)

def delete_row_second(row_idx):
    global df_second_spk

    df_second_spk = df_second_spk.drop(row_idx)
    df_second_spk.reset_index(drop=True, inplace=True)
    return df_second_spk, Modal(visible=False)

def append_new_task_second(new_task_machine, new_task_part_name, new_task_process_name, new_task_quantity, new_task_material_spec_size, new_op):
    global df_second_spk
    new_row = {
        "No": df_second_spk.shape[0] + 1,
        "Mesin": new_task_machine,
        "Part Name": new_task_part_name,
        "Process Name": new_task_process_name,
        "OP": new_op,
        "Quantity": new_task_quantity,
        "Material Spec Size": new_task_material_spec_size,
        "Delete": '`DELETE`'
    }

    df_second_spk = df_second_spk._append(new_row, ignore_index=True)
    return df_second_spk, Modal(visible=True)


with gr.Blocks(theme=gr.themes.Soft()) as demo:
    proposed_spk_list = gr.State(value=proposed_spk_initial_state)
    approved_spk_list = gr.State(value=approved_spk_initial_state)
    rejected_spk_list = gr.State(value=rejected_spk_initial_state)
    with gr.Row():
        credential = gr.State(value=None)
        username = gr.Text(label="Username")
        password = gr.Text(label='Password', type='password')
        login_button = gr.Button("Login")
        login_button.click(get_credential, inputs=[username, password], outputs=credential)

    with gr.Tab("SPK"):
        with gr.Tabs("SPK_Tab_Items") as spk_tabs:
            with gr.TabItem("Shift II (Today)", id=0):
                preview_button = gr.Button("Lihat Pratinjau", render=False)
                submit_button = gr.Button("Simpan SPK", interactive=False, render=False)  
                add_task_button = gr.Button("Tambah", interactive=False, render=False)          
                with gr.Row():
                    with gr.Column():
                        with gr.Row():
                            year = gr.Number(label="Tahun", minimum=2000, maximum=2100)
                            month = gr.Dropdown(label="Bulan",value='Januari', choices=['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'])
                            day = gr.Dropdown(value=1, label="Tanggal", choices=[i+1 for i in range(31)])
                        leader = gr.Dropdown(value="Ahmad", choices=["Ahmad", "Bambang", "Junaedi"], label="PIC Line/Leader")
                    with gr.Column():
                        with gr.Row():
                            shift = gr.Dropdown(value="Shift II", choices=["Shift I", "Shift II"], label="Shift", interactive=False)
                        with gr.Row():
                            start_hour = gr.Dropdown([f"0{i}.00" if i <= 9 else f"{i}.00" for i in range(24)], label="Jam Mulai Kerja", value="20.00")
                            end_hour = gr.Dropdown([f"0{i}.00" if i <= 9 else f"{i}.00" for i in range(24)], label="Jam Selesai Kerja", value="05.00")
                with gr.Row():
                    preview_button.render()
                    spk = gr.DataFrame(df_empty_tasks, interactive=True, row_count=(1, 'static'), col_count=(7, 'static'), render=False, datatype=["number", "str", "str", "str", "str", "number", "str", "markdown"])
                    preview_button.click(get_spk, inputs=[credential], outputs=[spk, submit_button, add_task_button])
                spk.render()

                row_to_be_deleted = gr.State()
                with Modal(visible=False) as delete_confirmation_modal:
                    gr.Markdown(
                        f"""
                        # Konfirmasi Penghapusan
                        Hapus baris tersebut?
                        """)
                    with gr.Row():
                        cancel_deletion_button = gr.Button("Batal")
                        cancel_deletion_button.click(lambda: Modal(visible=False), None, delete_confirmation_modal)
                        confirm_deletion_button = gr.Button("Ya, Hapus")
                        confirm_deletion_button.click(delete_row, inputs=row_to_be_deleted, outputs=[spk, delete_confirmation_modal])

                spk.select(spk_select_listener, outputs=[row_to_be_deleted, delete_confirmation_modal])

                with Modal(visible=False) as new_task_modal:
                    gr.Markdown(
                        """
                        # Penambahan Task Produksi
                        Isi data di bawah untuk menambahkan task produksi.
                        """)
                    with gr.Row():
                        with gr.Column():
                            new_task_part_name = gr.Dropdown(choices=formatted_part_names, label='Nama Part')
                            new_task_process_name = gr.Dropdown(choices=process_names, label='Nama Proses')
                            new_task_op = gr.Dropdown(choices=[f"OP{i+1}0" for i in range(6)], label='Nama Proses')
                            new_task_material_spec_size = gr.Dropdown(label='Material Spec Size', choices=['']+sorted(materials))
                        with gr.Column():
                            new_task_machine = gr.Dropdown(choices=tonnage2name, label='Mesin')
                            new_task_quantity = gr.Number(label='Quantity', minimum=0)
                    append_new_task_button = gr.Button("Tambahkan")
                    append_new_task_button.click(append_new_task, inputs=[new_task_machine, new_task_part_name, new_task_process_name, new_task_quantity, new_task_material_spec_size, new_task_op], outputs=[spk, new_task_modal])
                with gr.Row():
                    with gr.Column(scale=8):
                        gr.Markdown()
                    with gr.Column(scale=2):
                        add_task_button.render()
                add_task_button.click(lambda: Modal(visible=True), None, new_task_modal)

                submit_button.render()
                preview_button_second = gr.Button("Lihat Pratinjau", interactive=False, render=False)
                add_task_button_second = gr.Button("Tambah", interactive=False, render=False)
                submit_button.click(save_spk, inputs=[spk, leader, year, month, day, start_hour, end_hour, shift, proposed_spk_list], outputs=[preview_button_second, proposed_spk_list, add_task_button_second])
            
            with gr.TabItem(f"Shift I (Tomorrow)", id=1):
                submit_button_second = gr.Button("Simpan SPK", interactive=False, render=False)
                with gr.Row():
                    with gr.Column():
                        with gr.Row():
                            year_second = gr.Number(label="Tahun", minimum=2000, maximum=2100)
                            month_second = gr.Dropdown(label="Bulan", choices=['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'], value="Januari")
                            day_second = gr.Dropdown(label="Tanggal", choices=[i+1 for i in range(31)], value=1)
                        leader_second = gr.Dropdown(choices=["Ahmad", "Bambang", "Junaedi"], value="Ahmad", label="PIC Line/Leader")
                    with gr.Column():
                        with gr.Row():
                            shift_second = gr.Dropdown(value="Shift I", choices=["Shift I", "Shift II"], label="Shift", interactive=False)
                        with gr.Row():
                            start_hour_second = gr.Dropdown([f"0{i}.00" if i <= 9 else f"{i}.00" for i in range(24)], label="Jam Mulai Kerja", value="08.00")
                            end_hour_second = gr.Dropdown([f"0{i}.00" if i <= 9 else f"{i}.00" for i in range(24)], label="Jam Selesai Kerja", value="17.00")
                with gr.Row():
                    preview_button_second.render()
                    spk_second = gr.DataFrame(df_empty_tasks, interactive=True, col_count=(7, 'static'),  render=False)
                    preview_button_second.click(get_second_spk, outputs=[spk_second, submit_button_second])
                spk_second.render()

                row_to_be_deleted_second = gr.State()
                with Modal(visible=False) as delete_confirmation_modal_second:
                    gr.Markdown(
                        f"""
                        # Konfirmasi Penghapusan
                        Hapus baris tersebut?
                        """)
                    with gr.Row():
                        cancel_deletion_button_second = gr.Button("Batal")
                        cancel_deletion_button_second.click(lambda: Modal(visible=False), None, delete_confirmation_modal_second)
                        confirm_deletion_button_second = gr.Button("Ya, Hapus")
                        confirm_deletion_button_second.click(delete_row_second, inputs=row_to_be_deleted_second, outputs=[spk_second, delete_confirmation_modal_second])


                with Modal(visible=False) as new_task_modal_second:
                    gr.Markdown(
                        """
                        # Penambahan Task Produksi
                        Isi data di bawah untuk menambahkan task produksi.
                        """)
                    with gr.Row():
                        with gr.Column():
                            new_task_part_name_second = gr.Dropdown(choices=formatted_part_names, label='Nama Part')
                            new_task_process_name_second = gr.Dropdown(choices=process_names, label='Nama Proses')
                            new_task_op_second = gr.Dropdown(choices=[f"OP{i+1}0" for i in range(6)], label='Nama Proses')
                            new_task_material_spec_size_second = gr.Dropdown(label='Material Spec Size', choices=['']+sorted(materials))
                        with gr.Column():
                            new_task_machine_second = gr.Dropdown(choices=tonnage2name, label='Mesin')
                            new_task_quantity_second = gr.Number(label='Quantity', minimum=0)
                    append_new_task_button_second = gr.Button("Tambahkan")
                    append_new_task_button_second.click(append_new_task_second, inputs=[new_task_machine_second, new_task_part_name_second, new_task_process_name_second, new_task_quantity_second, new_task_material_spec_size_second, new_task_op_second], outputs=[spk_second, new_task_modal_second])
                with gr.Row():
                    with gr.Column(scale=8):
                        gr.Markdown()
                    with gr.Column(scale=2):
                        add_task_button_second.render()
                add_task_button.click(lambda: Modal(visible=True), None, new_task_modal_second)

                submit_button_second.render()
                submit_button_second.click(save_spk, inputs=[spk_second, leader_second, year_second, month_second, day_second, start_hour_second, end_hour_second, shift_second, proposed_spk_list], outputs=[preview_button_second, proposed_spk_list])

            with gr.TabItem("Pengajuan SPK"):
                selected_spk_proposal = gr.State()
                proposal_preview = gr.Image(interactive=False, render=False)
                def spk_cta_modal_open(filename, credential):
                    if credential == 'supervisor':
                        return Modal(visible=True), filename
                    else:
                        gr.Warning("Hanya Supervisor yang dapat menyetujui/menolak pengajuan SPK")

                with Modal(visible=False) as spk_approve_modal:
                    gr.Markdown(f"# Apakah Anda menyetujui pengajuan SPK tersebut?")
                    spk_approve_button = gr.Button("Ya, setujui")
                    spk_approve_button.click(approve_spk, inputs=[selected_spk_proposal, credential, proposed_spk_list, approved_spk_list], outputs=[proposal_preview, proposed_spk_list, approved_spk_list])

                with Modal(visible=False) as spk_reject_modal:
                    gr.Markdown(f"# Apakah Anda menolak pengajuan SPK tersebut?")
                    spk_reject_button = gr.Button("Ya, tolak")
                    spk_reject_button.click(reject_spk, inputs=[selected_spk_proposal, credential, proposed_spk_list, rejected_spk_list], outputs=[proposal_preview, proposed_spk_list, rejected_spk_list])

                with gr.Tab("Daftar Pengajuan SPK"):
                    @gr.render(inputs=proposed_spk_list)
                    def render_spk_proposal(proposed_spk_list):
                        proposed_spk_names_display = []
                        proposed_spk_view_buttons = []
                        proposed_spk_approve_buttons = []
                        proposed_spk_reject_buttons = []
                        for i in range(len(proposed_spk_list)):
                            proposed_spk_names_display.append(gr.Text(proposed_spk_list[i], render=False, label="No. SPK", interactive=False))
                            proposed_spk_view_buttons.append(gr.Button("Lihat Pengajuan SPK", render=False))
                            proposed_spk_approve_buttons.append(gr.Button("Approve", render=False))
                            proposed_spk_reject_buttons.append(gr.Button("Reject", render=False))
                        for i in range(len(proposed_spk_names_display)):
                            with gr.Row():
                                with gr.Column(scale=4):
                                    proposed_spk_names_display[i].render()
                                with gr.Column(scale=2):
                                    gr.Markdown()
                                    gr.Markdown()
                                    proposed_spk_view_buttons[i].render()
                                    proposed_spk_view_buttons[i].click(switch_proposed_spk_preview, inputs=proposed_spk_names_display[i], outputs=[proposal_preview])
                                with gr.Column(scale=1):
                                    proposed_spk_approve_buttons[i].render()
                                    proposed_spk_reject_buttons[i].render()
                                    proposed_spk_approve_buttons[i].click(spk_cta_modal_open, inputs=[proposed_spk_names_display[i], credential], outputs=[spk_approve_modal, selected_spk_proposal])
                                    proposed_spk_reject_buttons[i].click(spk_cta_modal_open, inputs=[proposed_spk_names_display[i], credential], outputs=[spk_reject_modal, selected_spk_proposal])
                        
                    gr.Markdown("# Preview SPK")
                    proposal_preview.render()
            with gr.Tab("SPK Disetujui"):
                approved_proposal_preview = gr.Image(interactive=False, render=False)
                @gr.render(inputs=approved_spk_list)
                def render_approved_spk(approved_spk_list):
                    approved_spk_names_display = []
                    approved_spk_view_buttons = []
                    approved_spk_status = []
                    for i in range(len(approved_spk_list)):
                        approved_spk_names_display.append(gr.Text(approved_spk_list[i], render=False, label="No. SPK", interactive=False))
                        approved_spk_status.append(gr.Radio(value='Approved', choices=["Approved", "Pending", "Rejected"], label="Status", render=False, interactive=False))
                        approved_spk_view_buttons.append(gr.Button("Lihat SPK", render=False))
                    for i in range(len(approved_spk_names_display)):
                        with gr.Row():
                            with gr.Column(scale=4):
                                approved_spk_names_display[i].render()
                            with gr.Column(scale=4):
                                approved_spk_status[i].render()
                            with gr.Column(scale=2):
                                approved_spk_view_buttons[i].render()
                                approved_spk_view_buttons[i].click(switch_proposed_spk_preview, inputs=approved_spk_names_display[i], outputs=[approved_proposal_preview])
                approved_proposal_preview.render()
            with gr.Tab("SPK Ditolak"):
                def revise_spk(filename):
                    import pickle as pkl
                    df = pkl.load(open(f"outputs/rejected_spk/{filename}.pickle", 'rb'))
                    tab_idx = 0 if "II" in filename else 1
                    return df, gr.Tabs(selected=tab_idx)

                @gr.render(inputs=rejected_spk_list)
                def render_approved_spk(rejected_spk_list):
                    rejected_spk_names_display = []
                    rejected_spk_status = []
                    revise_spk_buttons = []
                    for i in range(len(rejected_spk_list)):
                        rejected_spk_names_display.append(gr.Text(rejected_spk_list[i], render=False, label="No. SPK", interactive=False))
                        rejected_spk_status.append(gr.Radio(value='Rejected', choices=["Approved", "Pending", "Rejected"], label="Status", render=False, interactive=False))
                        revise_spk_buttons.append(gr.Button("Buat Revisi", render=False))
                    for i in range(len(rejected_spk_names_display)):
                        with gr.Row():
                            with gr.Column(scale=4):
                                rejected_spk_names_display[i].render()
                            with gr.Column(scale=4):
                                rejected_spk_status[i].render()
                            with gr.Column(scale=2):
                                revise_spk_buttons[i].render()
                                if 'II' in rejected_spk_list[i]:
                                    revise_spk_buttons[i].click(revise_spk, inputs=[rejected_spk_names_display[i]], outputs=[spk, spk_tabs])
                                else:
                                    revise_spk_buttons[i].click(revise_spk, inputs=[rejected_spk_names_display[i]], outputs=[spk_second, spk_tabs])
            with gr.TabItem(f"Kekurangan Material"):
                df_low_material_task = gr.DataFrame(get_low_material_task_display(low_material_tasks), col_count=(0, 'static'), row_count=(0, 'static'))
                part_stocks_export_button = gr.Button("Export to Excel")
                part_stocks_export_button.click(export_material_necessity_to_excel, inputs=[df_low_material_task])
            
    with gr.Tab("Stok"):
        df_part_stock = get_part_stock_dataframe_display(parts)
        part_stocks_display = gr.DataFrame(df_part_stock, col_count=(4, 'static'), row_count=(df_part_stock.shape[0], 'static'), render=False)
        df_material_stock = get_material_stock_dataframe_display(materials)
        material_stocks_display = gr.DataFrame(df_material_stock, render=False, col_count=(2, 'static'), row_count=(df_material_stock.shape[0], 'static'))
        part_stocks_export_button = gr.Button("Export to Excel")
        part_stocks_export_button.click(export_stock_to_excel, inputs=[part_stocks_display, material_stocks_display])
        with gr.Tab("Part"):
            part_stocks_display.render()
        with gr.Tab("Material"):
            material_stocks_display.render()

demo.launch()