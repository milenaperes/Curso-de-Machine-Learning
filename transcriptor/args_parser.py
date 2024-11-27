import argparse

class args_parser:
  def __init__(self):
    parser = argparse.ArgumentParser(description='transcriptor')
    parser.add_argument('-mode', default="app", type=str)
    parser.add_argument('--path_unprocessed', default=None, type=str)
    parser.add_argument('--path_processed', default=None, type=str)
    parser.add_argument('--prompt', default='Você é um transcritor especializado em capturar conteúdos de áudio com máxima precisão.', type=str)
    parser.add_argument('--model_size', default='medium', type=str)
    self.opts = parser.parse_args()

  def get_params(self):
    return self.opts
