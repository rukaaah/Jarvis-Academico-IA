import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import streamlit as st

class DataFolderHandler(FileSystemEventHandler):
    def __init__(self, rag_engine):
        self.rag = rag_engine
        self.processing = False

    def on_created(self, event):
        if not event.is_directory and self._is_supported(event.src_path):
            self._sync_file(event.src_path, "added")

    def on_deleted(self, event):
        if not event.is_directory and self._is_supported(event.src_path):
            filename = os.path.basename(event.src_path)
            self.rag.remover_documento(filename)

    def on_modified(self, event):
        if not event.is_directory and self._is_supported(event.src_path):
            self._sync_file(event.src_path, "modified")

    def _is_supported(self, path):
        return path.endswith(('.pdf', '.txt'))

    def _sync_file(self, filepath, action):
        if self.processing:
            return
        self.processing = True
        try:
            if action == "modified":
                # Remove versão antiga, depois adiciona nova
                filename = os.path.basename(filepath)
                self.rag.remover_documento(filename)
                if os.path.exists(filepath):
                    self.rag.adicionar_documento(filepath)
            elif action == "added":
                self.rag.adicionar_documento(filepath)
        except Exception as e:
            print(f"Erro ao sincronizar {filepath}: {e}")
        finally:
            self.processing = False

def iniciar_monitoramento(rag_engine):
    event_handler = DataFolderHandler(rag_engine)
    observer = Observer()
    observer.schedule(event_handler, path="data", recursive=False)
    observer.start()
    return observer