import os


class MarkdownReader:
    def __init__(self, directory):
        self.directory = directory

    def read_files(self):
        files = [f for f in os.listdir(self.directory) if f.endswith('.md')]
        return files

    def parse_file(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return content
