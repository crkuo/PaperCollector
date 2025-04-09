import os

class OpenAlexToolInfo:
    def __init__(self, apiData:dict):
        self.requestJsonData = apiData

    def __dict__(self):
        return self.requestJsonData

    def get_data(self) -> dict:
        return self.preprocessing()
    
    def preprocessing(self) -> dict:
        requestData = dict()
        requestData.update(self.requestJsonData)
        if 'authorships' in requestData:
            requestData['authorships'] = ','.join([author['author']['display_name'] for author in requestData['authorships']])
        if 'fieldsOfStudy' in requestData:
            requestData['fieldsOfStudy'] = ','.join([field for field in requestData['fieldsOfStudy'] ]) if requestData['fieldsOfStudy'] else ""
        return requestData
    

class SemanticScholarInfo:
    def __init__(self, apiData:dict):
        self.requestJsonData = apiData

    def __dict__(self):
        return self.requestJsonData

    def get_data(self) -> dict:
        return self.preprocessing()
    
    def preprocessing(self) -> dict:
        requestData = dict()
        requestData.update(self.requestJsonData)
        if 'authors' in requestData:
            requestData['authors'] = ','.join([author['name'] for author in requestData['authors']])
        if 'fieldsOfStudy' in requestData:
            requestData['fieldsOfStudy'] = ','.join([field for field in requestData['fieldsOfStudy'] ]) if requestData['fieldsOfStudy'] else ""
        return requestData