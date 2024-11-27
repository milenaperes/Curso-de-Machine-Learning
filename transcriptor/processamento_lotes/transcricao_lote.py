from transcriptor.app.app_transcricao import AudioTranscriptorApp
from transcriptor.processamento_lotes.error_logs import record_error
import logging
import time
import os
import whisper

logger = logging.getLogger('processamento_lotes')
def execute_transcription_folder(args):
    logger.info(f"Started at {time.strftime('%H:%M:%S')}")
    start_time = time.time()

    folder_path = os.path.normpath(args.path_unprocessed)
    path_processed = os.path.normpath(args.path_processed)
    os.makedirs(path_processed, exist_ok=True)

    # Initialize the transcription class (without UI)
    transcriptor_app = AudioTranscriptorApp()
    model = transcriptor_app.initialize_model(args.model_size)
    prompt_usuario = args.prompt

    # Error logging
    error_file = os.path.join(path_processed, f'{os.path.basename(folder_path)}_errors.txt')
    error_encountered = False
    try:
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if
                 f.endswith(".mp4") or f.endswith(".MP4")]
        transcriptor_app.processar_arquivos(filenames=files, model=model, prompt_usuario=prompt_usuario)
    except Exception as e:
            error_encountered = True
            error_message = f"Error processing file {files}): {str(e)}"
            logger.error(error_message)
            with open(error_file, 'a', encoding='utf-8') as ef:
                ef.write(error_message + '\n')

    # Log completion
    if error_encountered:
        logger.error("Errors occurred during processing. Please check the error log.")
    else:
        end_time = time.time()
        elapsed_time = (end_time - start_time) / 3600.0
        logger.info(f"Data processing completed without errors. Time elapsed: {elapsed_time:.2f} hours")
