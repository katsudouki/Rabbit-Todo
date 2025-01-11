import tkinter as tk
from tkinter import messagebox, colorchooser
from tkinter.simpledialog import askstring
from tkcalendar import Calendar
import json
import os

# INFO: Variáveis globais para cores
default_bg_color = "#ffffff"
default_text_color = "#000000"
bg_color = default_bg_color
text_color = default_text_color
coins = 0

# INFO: Dicionário de valores de prioridade
PRIORITY_VALUES = {
    "irrelevante": 1,
    "baixa": 5,
    "média": 7,
    "alta": 10,
    "urgente": 20,
}

CONFIG_FILE = "config.json"
TODO_PATH = "saves"

#INFO:  Garantir que a pasta existe
def folder_check(path):
    if not os.path.exists(path):
        os.makedirs(path)

folder_check(TODO_PATH)

# INFO: Função para salvar as configurações
def save_config():
    config = {"bg_color": bg_color, "text_color": text_color, "coins": coins}
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file)

# INFO: Função para carregar as configurações
def load_config():
    global bg_color, text_color, coins
    try:
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
            bg_color = config.get("bg_color", default_bg_color)
            text_color = config.get("text_color", default_text_color)
            coins = config.get("coins", 0)
    except FileNotFoundError:
        save_config()

# INFO: Função para salvar as tarefas
def save_tasks():
    tasks_data = [
        {
            "task": task,
            "date": date,
            "notify": notify.get(),
            "priority": priority,
            "completed": completed.get(),
        }
        for task, date, notify, priority, completed in tasks_list
    ]
    with open(os.path.join(TODO_PATH, "tasks.json"), "w") as file:
        json.dump(tasks_data, file)

# INFO: Função para carregar as tarefas salvas
def load_saved_tasks():
    tasks_file = os.path.join(TODO_PATH, "tasks.json")
    if os.path.exists(tasks_file):
        with open(tasks_file, "r") as file:
            loaded_tasks = json.load(file)
            for task_data in loaded_tasks:
                # INFO: Reconstrói as variáveis de estado para cada tarefa
                task = task_data.get("task", "Tarefa sem nome")
                date = task_data.get("date", "")
                notify = tk.BooleanVar(value=task_data.get("notify", False))
                priority = task_data.get("priority", "média")
                completed = tk.BooleanVar(value=task_data.get("completed", False))
                tasks_list.append((task, date, notify, priority, completed))

#INFO:  Atualiza o valor de RabbitCoins com base no status da tarefa
def update_coins(task_var, priority):
    global coins
    value = PRIORITY_VALUES.get(priority, 0)
    if task_var.get():
        coins += value
    else:
        coins -= value
    save_config()
    update_coin_label()

# INFO: Função para abrir o popup de seleção de hora
def select_time():
    def set_time():
        hour = hour_var.get()
        minute = minute_var.get()
        selected_time.set(f"{hour:02}:{minute:02}")
        time_popup.destroy()

    time_popup = tk.Toplevel(root)
    time_popup.title("Selecionar Hora")
    time_popup.configure(bg=bg_color)

    hour_var = tk.IntVar(value=12)
    minute_var = tk.IntVar(value=0)

    tk.Label(time_popup, text="Hora:", bg=bg_color, fg=text_color).pack(pady=5)
    tk.Spinbox(time_popup, from_=0, to=23, textvariable=hour_var, width=5).pack()

    tk.Label(time_popup, text="Minuto:", bg=bg_color, fg=text_color).pack(pady=5)
    tk.Spinbox(time_popup, from_=0, to=59, textvariable=minute_var, width=5).pack()

    tk.Button(time_popup, text="Definir", command=set_time).pack(pady=10)

# INFO: Popup para adicionar tarefa
def open_add_task_popup():
    popup = tk.Toplevel(root)
    popup.title("Adicionar Tarefa")

    tk.Label(popup, text="Nome da Tarefa:").pack(pady=5)
    task_entry = tk.Entry(popup, width=30)
    task_entry.pack(pady=5)

    tk.Label(popup, text="Prioridade:").pack(pady=5)
    priority_var = tk.StringVar(value="irrelevante")
    priority_menu = tk.OptionMenu(popup, priority_var, "irrelevante", "baixa", "média", "alta")
    priority_menu.pack(pady=5)

    tk.Label(popup, text="Data e Hora:").pack(pady=5)

    def select_date():
        date_popup = tk.Toplevel(popup)
        date_popup.title("Selecionar Data")
        calendar = Calendar(date_popup, selectmode="day")
        calendar.pack(pady=10)

        def confirm_date():
            selected_date.set(calendar.get_date())
            date_popup.destroy()

        tk.Button(date_popup, text="Confirmar", command=confirm_date).pack(pady=10)

    selected_date = tk.StringVar()
    tk.Button(popup, text="Selecionar Data", command=select_date).pack(pady=5)
    tk.Label(popup, textvariable=selected_date).pack(pady=5)

    notify_var = tk.BooleanVar(value=False)
    tk.Checkbutton(popup, text="Notificar", variable=notify_var).pack(pady=5)

    def add_task():
        task = task_entry.get()
        priority = priority_var.get()
        date = selected_date.get()

        if task:
            completed_var = tk.BooleanVar()
            tasks_list.append((task, date, notify_var, priority, completed_var))
            save_tasks()
            update_tasks()
            popup.destroy()
        else:
            messagebox.showwarning("Aviso", "Por favor, insira uma tarefa.")

    tk.Button(popup, text="Adicionar", command=add_task).pack(pady=10)

# INFO: Atualiza a lista de tarefas
def update_tasks():
    for widget in tasks_frame.winfo_children():
        widget.destroy()

    for task, date, notify, priority, completed in tasks_list:
        # INFO: Frame para a tarefa e o botão de apagar
        frame = tk.Frame(tasks_frame, bg=bg_color)
        frame.pack(fill="x", pady=5)

        # INFO: Checkbox da tarefa
        task_text = f"{task} ({priority.capitalize()})"
        if date:
            task_text += f" - {date}"
        task_checkbox = tk.Checkbutton(
            frame,
            text=task_text,
            variable=completed,
            bg=bg_color,
            fg=text_color,
            command=lambda var=completed, pri=priority: update_coins(var, pri),
        )
        task_checkbox.pack(side=tk.LEFT, padx=5, pady=2)

        #INFO:  Botão de apagar
        delete_button = tk.Button(
            frame,
            text="Apagar",
            command=lambda t=task: delete_task(t),
            bg="#ff6464",
            fg="white",
        )
        delete_button.pack(side=tk.RIGHT, padx=5)

        #INFO:  Linha horizontal separando as tarefas
        separator = tk.Frame(tasks_frame, height=1, bg="gray")
        separator.pack(fill="x", pady=2)

# INFO: Função para deletar tarefas
def delete_task(task_name):
    global tasks_list
    tasks_list = [t for t in tasks_list if t[0] != task_name]
    save_tasks()
    update_tasks()

# INFO:  Atualiza o rótulo de moedas
def update_coin_label():
    coin_label.config(text=f"RabbitCoins: {coins}")

#INFO:  Função para abrir o menu de configurações
def open_settings():
    def apply_colors():
        global bg_color, text_color
        bg_color = bg_color_var.get()
        text_color = text_color_var.get()
        save_config()
        root.configure(bg=bg_color)
        update_tasks()
        settings_popup.destroy()

    settings_popup = tk.Toplevel(root)
    settings_popup.title("Configurações")
    settings_popup.configure(bg=bg_color)

    tk.Label(settings_popup, text="Cor de Fundo:", bg=bg_color, fg=text_color).pack(pady=5)
    bg_color_var = tk.StringVar(value=bg_color)
    tk.Entry(settings_popup, textvariable=bg_color_var).pack(pady=5)
    tk.Button(
        settings_popup,
        text="Escolher Cor",
        command=lambda: bg_color_var.set(colorchooser.askcolor()[1]),
    ).pack(pady=5)

    tk.Label(settings_popup, text="Cor do Texto:", bg=bg_color, fg=text_color).pack(pady=5)
    text_color_var = tk.StringVar(value=text_color)
    tk.Entry(settings_popup, textvariable=text_color_var).pack(pady=5)
    tk.Button(
        settings_popup,
        text="Escolher Cor",
        command=lambda: text_color_var.set(colorchooser.askcolor()[1]),
    ).pack(pady=5)

    tk.Button(settings_popup, text="Aplicar", command=apply_colors).pack(pady=10)

# INFO:  Configuração inicial
root = tk.Tk()
root.title("Rabbit Todo")
root.geometry("800x600")
load_config()
root.configure(bg=bg_color)

# INFO:  Variáveis globais
tasks_list = []

# INFO: Frame superior
top_frame = tk.Frame(root, bg=bg_color)
top_frame.pack(pady=10, fill="x")

coin_label = tk.Label(
    top_frame, text=f"RabbitCoins: {coins}", font=("Arial", 14), fg=text_color, bg=bg_color
)
coin_label.pack(side=tk.LEFT, padx=10)

add_button = tk.Button(top_frame, text="+", font=("Arial", 16), command=open_add_task_popup)
add_button.pack(side=tk.RIGHT, padx=10)

settings_button = tk.Button(top_frame, text="Cores", command=open_settings)
settings_button.pack(side=tk.RIGHT, padx=10)

#INFO:  Linha horizontal
separator = tk.Frame(root, height=1, bg="gray")
separator.pack(fill="x", pady=5)

# INFO: Frame para a lista de tarefas
tasks_frame = tk.Frame(root, bg=bg_color)
tasks_frame.pack(pady=10, fill="both", expand=True)

# INFO: Inicializar tarefas
load_saved_tasks()
update_tasks()

# INFO: Iniciar o loop do Tkinter
root.mainloop()
