
def record_error(error_message, error_file):
  """
    Logs an error message to a specified file.

    This function appends an error message to the end of a specified log file. It's typically used to record errors
    encountered during processing.

    Parameters
    ----------
    error_message : str
        The message of the error to log.
    error_file : str
        The path to the error log file where the message should be appended.

    Returns
    -------
    None
  """
  with open(error_file, 'a') as f:
    f.write(error_message + '\n')

