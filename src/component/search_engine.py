import os , sys, datetime, shutil, json, re
from utils.dao import SemanticScholarTool, PaperProcessor
from component.paper_info import PaperInfo


class SearchEngine:
    semantic_tool = SemanticScholarTool()

    def SearchWithPapersFolder(self, source_dir):
        file_names:list[str] = [file for file in os.listdir(source_dir) if file.endswith('.pdf')]
        identity_ids:list[str] = [file_name.rsplit('.pdf', 1)[0] for file_name in file_names]
        paper_infos = self.semantic_tool.GetPapersWithListPaperId(identity_ids)
        res = {'success':{}, 'failed':{}}
        for file_name in file_names:
            identity_id = file_name.rsplit('.pdf', 1)[0]
            if identity_id in paper_infos:
                paper_info:PaperInfo = paper_infos[identity_id]
                res['success'].update(self.__dealWithPaperInfo(os.path.join(source_dir, file_name), paper_info))
            else:
                res['failed'][os.path.join(source_dir, file_name)] = {}
        return res
    
    def SearchWithTitle(self, paper_path:str, title:str):
        file_name = paper_path.rsplit('\\', 1)[-1].rsplit('/', 1)[-1]
        if not file_name.endswith('.pdf'):
            return None
        paper_info = self.semantic_tool.SearchPaperWithKeyword(title)
        return self.__dealWithPaperInfo(paper_path, paper_info)
    
    
    def SearchWithDoi(self, paper_path:str, doi:str):
        def AssignPaperId(doi):
            return f"DOI:{doi}"
        file_name = paper_path.rsplit('\\', 1)[-1].rsplit('/', 1)[-1]
        if not file_name.endswith('.pdf'):
            return None
        paper_id = AssignPaperId(doi)
        paper_info = self.semantic_tool.GetPaperFromPaperId(paper_id)
        return self.__dealWithPaperInfo(paper_path, paper_info)
        
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
        paper_info = self.semantic_tool.GetPaperFromPaperId(paper_id)
        return self.__dealWithPaperInfo(paper_path, paper_info)

    def __dealWithPaperInfo(paper_path, paper_info:PaperInfo):
        if not paper_info:
            return None
        paper_data = paper_info.get_data()
        return {paper_path:paper_data}
    
