from mappingUtility.strategy.ComponentGenerator import FileProcessor

class FileProcessingContext:
    def __init__(self, strategy: FileProcessor):
        self._strategy = strategy

    def set_strategy(self, strategy: FileProcessor):
        self._strategy = strategy

    # def before_process(self, file_content: str):
    #     """Hook for pre-processing logic."""
    #     print("Before processing: Adding pre-processing logic.")
    #     # You can add validation, logging, etc. here

    # def after_process(self, result: dict):
    #     """Hook for post-processing logic."""
    #     print("After processing: Adding post-processing logic.")
    #     # You can add logging, result transformation, etc. here

    def execute(self, file_content):
        # Call before process hook
        # self.before_process(file_content)

        # Call the strategy's process method
        result = self._strategy.process(file_content)

        # Call after process hook
        # self.after_process(result)

        return result
