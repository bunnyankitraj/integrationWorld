from mappingUtility.strategy.ComponentGenerator import FileProcessor

class FileProcessingContext:
    def __init__(self, strategy: FileProcessor):
        self._strategy = strategy

    def set_strategy(self, strategy: FileProcessor):
        self._strategy = strategy

    def execute(self, file_content):
        result = self._strategy.process(file_content)
        return result
