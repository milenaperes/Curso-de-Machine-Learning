import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import whisper
import threading
import os


def selecionar_arquivos():
    filenames = filedialog.askopenfilenames(filetypes=[("Arquivos de vídeo", "*.mp4")])
    if filenames:
        iniciar_transcricao(filenames)


def iniciar_transcricao(filenames):
    try:
        # Carregar o modelo de forma assíncrona para não travar a interface
        threading.Thread(target=processar_arquivos, args=(filenames,)).start()
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")


def processar_arquivos(filenames):
    model = whisper.load_model("base")

    # Configurar a barra de progresso
    progress_bar["maximum"] = len(filenames)
    progress_bar["value"] = 0
    text_resultado = ""

    for i, fn in enumerate(filenames):
        progress_bar["value"] = i + 1
        app.update_idletasks()  # Atualiza a interface para refletir a barra de progresso

        audio = whisper.load_audio(fn)
        result = model.transcribe(audio)

        # Mostrar o resultado em uma janela pop-up
        text_resultado += f"Arquivo: {os.path.basename(fn)}\n"
        text_resultado += result["text"] + "\n\n"
        messagebox.showinfo("Resultado da Transcrição", f"Arquivo {os.path.basename(fn)} transcrito com sucesso!")


    exportar_para_txt(text_resultado)

def exportar_para_txt(texto):
    try:
        output_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                   filetypes=[("Arquivo de texto", "*.txt")],
                                                   title="Salvar transcrição como")
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(texto)
            messagebox.showinfo("Exportação", f"Transcrição exportada com sucesso para {output_path}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao exportar a transcrição: {str(e)}")

# Configuração da interface principal
app = tk.Tk()
app.title("Transcritor de Áudio com Whisper")
app.geometry("400x250")

# Botão para iniciar a seleção de arquivos
btn_selecionar = tk.Button(app, text="Selecionar Arquivos", command=selecionar_arquivos)
btn_selecionar.pack(pady=20)

# Barra de progresso
progress_bar = ttk.Progressbar(app, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

# Roda a aplicação
app.mainloop()
