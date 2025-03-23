import logging

class GUILogHandler(logging.Handler):
    """
    A logging handler that appends log messages to a Tkinter Text widget.
    """
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        try:
            msg = self.format(record)
            # Schedule GUI update in the main thread
            self.text_widget.after(0, self.append_message, msg)
        except Exception:
            self.handleError(record)

    def append_message(self, msg):
        self.text_widget.configure(state='normal')
        self.text_widget.insert('end', msg + "\n")
        self.text_widget.configure(state='disabled')
        self.text_widget.see('end')
