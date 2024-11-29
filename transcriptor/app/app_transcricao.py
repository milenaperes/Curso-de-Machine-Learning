import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import torch
import whisper
from tqdm import tqdm
import os
import threading

class AudioTranscriptorApp:
    def __init__(self, master=None):
        """
        Initialize the application. If `master` is None, skip UI setup.
        """
        self.master = master
        if self.master:
            self.master.title("Transcritor de Áudio com Whisper")
            self.master.geometry("600x400")
            self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        label_modelo = tk.Label(self.master, text="Selecione o modelo de transcrição:")
        label_modelo.pack(pady=5)

        self.combo_modelo = ttk.Combobox(self.master, values=["medium", "large"], state="readonly")
        self.combo_modelo.set("medium")
        self.combo_modelo.pack(pady=5)

        label_info_modelo = tk.Label(self.master,
                                     text="Dica: O modelo 'large' é mais preciso, mas consome mais recursos.")
        label_info_modelo.pack(pady=5)

        label_prompt = tk.Label(self.master, text="Insira o prompt personalizado:")
        label_prompt.pack(pady=5)

        self.entry_prompt = tk.Text(self.master, height=5, width=50)
        self.entry_prompt.insert("1.0",
                                 "Você é um transcritor especializado em capturar conteúdos de áudio com máxima precisão.")
        self.entry_prompt.pack(pady=5)

        btn_selecionar = tk.Button(self.master, text="Selecionar Arquivos", command=self.selecionar_arquivos)
        btn_selecionar.pack(pady=20)

    def selecionar_arquivos(self):
        """Open file dialog to select files for transcription."""
        filenames = filedialog.askopenfilenames(filetypes=[("Arquivos de vídeo", "*.mp4")])
        if filenames:
            self.iniciar_transcricao(filenames)

    def initialize_model(self, modelo_selecionado):
        """Initialize and return the Whisper model."""
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        model = whisper.load_model(modelo_selecionado, device=device)
        return model

    # Função para selecionar arquivos e iniciar a transcrição
    def processar_arquivos(self, filenames, model, prompt_usuario):
        """Process and transcribe the selected files."""
        ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg")
        os.environ["PATH"] += os.pathsep + ffmpeg_path
        full_transcription = ""
        for fn in tqdm(filenames, desc="Transcrevendo arquivos"):
            audio = whisper.load_audio(fn)
            result = model.transcribe(
                audio,
                temperature=0.1,
                initial_prompt=prompt_usuario,
                language="pt"
            )
            full_transcription += result["text"] + " "
        return full_transcription

    def iniciar_transcricao(self, filenames):
        """Start transcription in a separate thread."""
        try:
            modelo_selecionado = self.combo_modelo.get()
            prompt_usuario = self.entry_prompt.get("1.0", "end-1c")

            # Initialize the Whisper model
            model = self.initialize_model(modelo_selecionado)

            # Start the transcription in a separate thread
            threading.Thread(
                target=self._transcription_thread, args=(filenames, model, prompt_usuario)
            ).start()
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

    def save_txt_filebox(self, texto_transcrito):
        """Save the transcribed text to a file."""
        caminho_arquivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo de Texto", "*.txt")],
            title="Salvar Transcrição"
        )
        if caminho_arquivo:
            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                f.write(texto_transcrito.strip())
            messagebox.showinfo("Sucesso", f"Arquivo salvo em: {caminho_arquivo}")
        else:
            messagebox.showwarning("Cancelado", "Salvamento cancelado pelo usuário.")

    def _transcription_thread(self, filenames, model, prompt_usuario):
        """Thread worker for transcription."""
        try:
            transcription = self.processar_arquivos(filenames, model, prompt_usuario)
            self.save_txt_filebox(transcription)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante a transcrição: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioTranscriptorApp(root)
    root.mainloop()
