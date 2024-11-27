from transcriptor.args_parser import args_parser
from transcriptor.app.app_transcricao import AudioTranscriptorApp
from transcriptor.processamento_lotes.transcricao_lote import execute_transcription_folder
import tkinter as tk
import logging


logging.basicConfig()
logging.root.setLevel(logging.INFO)

if __name__ == "__main__":
  args = args_parser().get_params()
  if args.mode=='app':
    root = tk.Tk()
    app = AudioTranscriptorApp(root)
    root.mainloop()
  elif args.mode=='folder_processing':
    execute_transcription_folder(args)




