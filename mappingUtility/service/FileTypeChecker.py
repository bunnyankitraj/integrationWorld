class FileTypeChecker:
    
    
    def get_file_type(self, file):
        if not file:
            return None
        
        file_extension = file.name.split('.')[-1].lower()
        if file_extension == 'json':
            return 'json'
        elif file_extension == 'xml':
            return 'xml'
        
        content_type = file.content_type.lower()
        if 'json' in content_type:
            return 'json'
        elif 'xml' in content_type:
            return 'xml'
        
        return None
