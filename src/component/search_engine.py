import os , sys, datetime, shutil, json, re
from src.utils.dao import SemanticScholarTool, PaperProcessor, OpenAlexTool
from src.component.paper_info import SemanticScholarInfo, OpenAlexToolInfo

import env as paper_env

class SearchEngine:
    def __init__(self, engine='SemanticScholar'):
        if engine == 'SemanticScholar':
            self.search_tool = SemanticScholarTool()
        elif engine == "OpenAlex":
            self.search_tool = OpenAlexTool()
        else:
            raise
    def SearchWithPaperIds(self, paper_ids):
        paper_infos = self.search_tool.GetPapersWithListPaperId(paper_ids)
        res = {'success':{}, 'failed':{}}
        for paper_id in paper_ids:
            if paper_id in paper_infos:
                paper_info = paper_infos[paper_id]
                res['success'].update(self.__dealWithPaperInfo(paper_id, paper_info))
            else:
                res['failed'][paper_id] = {}
        return res

    def SearchWithPapersFolder(self, source_dir):
        file_names:list[str] = [file for file in os.listdir(source_dir) if file.endswith('.pdf')]
        identity_ids:list[str] = [file_name.rsplit('.pdf', 1)[0] for file_name in file_names]
        paper_infos = self.search_tool.GetPapersWithListPaperId(identity_ids)
        res = {'success':{}, 'failed':{}}
        for file_name in file_names:
            identity_id = file_name.rsplit('.pdf', 1)[0]
            if identity_id in paper_infos:
                paper_info = paper_infos[identity_id]
                res['success'].update(self.__dealWithPaperInfo(identity_id, paper_info))
            else:
                res['failed'][identity_id] = {}
        return res
    
    def SearchWithTitle(self, paper_path:str, title:str):
        file_name = paper_path.rsplit('\\', 1)[-1].rsplit('/', 1)[-1]
        if not file_name.endswith('.pdf'):
            return None
        identity_id = file_name.rsplit('.pdf', 1)[0]
        paper_info = self.search_tool.SearchPaperWithKeyword(title)
        return self.__dealWithPaperInfo(identity_id, paper_info)
    
    
    def SearchWithDoi(self, paper_path:str, doi:str):
        def AssignPaperId(doi):
            return f"DOI:{doi}"
        file_name = paper_path.rsplit('\\', 1)[-1].rsplit('/', 1)[-1]
        if not file_name.endswith('.pdf'):
            return None
        paper_id = AssignPaperId(doi)
        identity_id = file_name.rsplit('.pdf', 1)[0]
        paper_info = self.search_tool.GetPaperFromPaperId(paper_id)
        return self.__dealWithPaperInfo(identity_id, paper_info)
        
    def SearchWithPaperId(self, paper_path:str, identity_id = None):
        def AssignPaperId(identity_id):
            if len(identity_id)<11:
                paper_id = f"ArXiv:{identity_id}"
            else:
                paper_id = identity_id
            return paper_id 
        file_name = paper_path.rsplit('\\', 1)[-1].rsplit('/', 1)[-1]
        if not file_name.endswith('.pdf'):
            return None
        paper_id = AssignPaperId(identity_id)
        paper_info = self.search_tool.GetPaperFromPaperId(paper_id)
        return self.__dealWithPaperInfo(identity_id, paper_info)

    def __dealWithPaperInfo(self, file_name, paper_info):
        if not paper_info:
            return None
        paper_data = paper_info.get_data()
        return {file_name:paper_data}
    
