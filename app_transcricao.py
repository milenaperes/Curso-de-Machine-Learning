import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import whisper
from tqdm import tqdm
import threading


# Função para selecionar arquivos e iniciar a transcrição
def selecionar_arquivos():
    filenames = filedialog.askopenfilenames(filetypes=[("Arquivos de vídeo", "*.mp4")])
    if filenames:
        iniciar_transcricao(filenames)


# Função que realiza a transcrição e mostra a barra de progresso
def iniciar_transcricao(filenames):
    try:
        modelo_selecionado = combo_modelo.get()
        prompt_usuario = entry_prompt.get("1.0", "end-1c")

        threading.Thread(target=processar_arquivos, args=(filenames, modelo_selecionado, prompt_usuario)).start()
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")


# Função que processa a transcrição com tqdm e salva o resultado em um arquivo
def processar_arquivos(filenames, modelo_selecionado, prompt_usuario):
    # Carrega o modelo selecionado pelo usuário
    model = whisper.load_model(modelo_selecionado)

    for fn in tqdm(filenames, desc="Transcrevendo arquivos"):
        audio = whisper.load_audio(fn)

        # Transcrevendo com o prompt personalizado e idioma definido
        result = model.transcribe(
            audio,
            temperature=0.1,
            initial_prompt=prompt_usuario,
            language="pt"  # Especifica que o áudio está em Português
        )
        texto_transcrito = result["text"]

        # Salva o arquivo transcrito em um local escolhido pelo usuário
        caminho_arquivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo de Texto", "*.txt")],
            title="Salvar Transcrição"
        )

        if caminho_arquivo:
            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                f.write(texto_transcrito)
            messagebox.showinfo("Sucesso", f"Arquivo salvo em: {caminho_arquivo}")
        else:
            messagebox.showwarning("Cancelado", "Salvamento cancelado pelo usuário.")


# Configuração da interface principal
app = tk.Tk()
app.title("Transcritor de Áudio com Whisper")
app.geometry("600x400")

# Label para o campo de seleção de modelo
label_modelo = tk.Label(app, text="Selecione o modelo de transcrição:")
label_modelo.pack(pady=5)

# ComboBox para seleção do modelo
combo_modelo = ttk.Combobox(app, values=["medium", "large"], state="readonly")
combo_modelo.set("medium")  # Define o valor padrão como "medium"
combo_modelo.pack(pady=5)

# Mensagem explicativa sobre os modelos
label_info_modelo = tk.Label(app, text="Dica: O modelo 'large' é mais preciso, mas consome mais recursos.")
label_info_modelo.pack(pady=5)

# Label e campo de entrada para o prompt personalizado
label_prompt = tk.Label(app, text="Insira o prompt personalizado:")
label_prompt.pack(pady=5)

entry_prompt = tk.Text(app, height=5, width=50)
entry_prompt.insert("1.0", "Você é um transcritor especializado em capturar conteúdos de áudio com máxima precisão.")
entry_prompt.pack(pady=5)

# Botão para iniciar a seleção de arquivos
btn_selecionar = tk.Button(app, text="Selecionar Arquivos", command=selecionar_arquivos)
btn_selecionar.pack(pady=20)

# Roda a aplicação
app.mainloop()
