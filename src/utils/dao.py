import requests
import datetime
import os, json, re
from src.utils.sqliteconnector import SqliteHelper
from src.component.paper_info import SemanticScholarInfo, OpenAlexToolInfo

class OpenAlexTool:
    def __init__(self, fields:list=['title','authors','publicationDate','externalIds','citationCount','url','fieldsOfStudy','citations','references']):
        self.fields = fields

    def GetPaperFromArXiv(self, arXiv_id:str)->SemanticScholarInfo:
        req = requests.get(f"https://api.openalex.org/works?filter=primary_location.landing_page_url:https://arxiv.org/abs/{arXiv_id}&select={','.join(self.fields)}")
        if req.status_code == 200:
            return OpenAlexToolInfo(req.json())
        else:
            raise None

    def GetPaperFromDoi(self, doi:str)->SemanticScholarInfo:
        req = requests.get(f"https://api.openalex.org/works?filter=doi:{doi}&select={','.join(self.fields)}")
        if req.status_code == 200:
            return OpenAlexToolInfo(req.json())
        else:
            return None

    def SearchPaperWithKeyword(self, keyword:str)->SemanticScholarInfo:
        req = requests.get(f"https://api.openalex.org/works?filter=abstract.search:{keyword}&select={','.join(self.fields)}&limit=1")
        if req.status_code == 200:
            if req.json()["total"]>0:
                return OpenAlexToolInfo(req.json()["data"][0])
            else:
                return None
        else:
            return None
    def GetPapersWithListPaperId(self, paper_id_list:list)->dict:
        paperDataPair = dict()
        paperIds = list()
        for paperId in paper_id_list:
            arxiv_valid = re.match("\d{4}\.\d{5}", paperId)
            if arxiv_valid:
                paperIds.append(f'ARXIV:{arxiv_valid.group()}')
            else:
                paperIds.append(paperId)
        req = requests.post(
            'https://api.semanticscholar.org/graph/v1/paper/batch',
            params = {'fields': ','.join(self.fields)},
            json = {"ids": paperIds}
            )
        for i, paperInformation in enumerate(req.json()):
            if paperInformation:
                paperInformation['identifyId'] = paper_id_list[i]
                paperDataPair[paper_id_list[i]] = OpenAlexToolInfo(paperInformation)
        return paperDataPair


class SemanticScholarTool:
    """
    Due to an official announcement from the Semantic Scholar API:

    ----------------------------------------------------
    Request a Semantic Scholar API Key (Waitlist)
    Our API key issuance is currently on pause due to high demand.
    Please complete this form to join the waitlist,
    and we'll resume the process as soon as keys become available again.
    Thank you for your patience!
    ----------------------------------------------------

    We are unable to request or obtain a new API key at this time,
    making the Semantic Scholar API inaccessible for metadata retrieval.

    [Impacts]
    - Any functionality that relies on the Semantic Scholar API for academic paper metadata or citation data is currently disabled.
    - Automated processes that reference the Semantic Scholar endpoint may fail or be incomplete.

    [Alternative Solutions]
    1. OpenAlex
    - API:  https://api.openalex.org/works
    - Docs: https://docs.openalex.org/api
    """
    def __init__(self, fields:list=['title','authors','publicationDate','externalIds','citationCount','url','fieldsOfStudy','citations','references']):
        self.fields = fields

    def GetPaperFromArXiv(self, arXiv_id:str)->SemanticScholarInfo:
        req = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/arXiv:{arXiv_id.split('v')[0]}?&fields={','.join(self.fields)}")
        if req.status_code == 200:
            return SemanticScholarInfo(req.json())
        else:
            raise None
        
    def GetPapersWithListPaperId(self, paper_id_list:list)->dict:
        paperDataPair = dict()
        paperIds = list()
        for paperId in paper_id_list:
            arxiv_valid = re.match("\d{4}\.\d{5}", paperId)
            if arxiv_valid:
                paperIds.append(f'ARXIV:{arxiv_valid.group()}')
            else:
                paperIds.append(paperId)
        req = requests.post(
            'https://api.semanticscholar.org/graph/v1/paper/batch',
            params = {'fields': ','.join(self.fields)},
            json = {"ids": paperIds}
            )
        print(req.json())
        for i, paperInformation in enumerate(req.json()):
            if paperInformation:
                paperInformation['identifyId'] = paper_id_list[i]
                paperDataPair[paper_id_list[i]] = SemanticScholarInfo(paperInformation)
        return paperDataPair

    def GetPaperFromPaperId(self, paperId:str)->SemanticScholarInfo:
        req = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/{paperId}?&fields={','.join(self.fields)}")
        if req.status_code == 200:
            return SemanticScholarInfo(req.json())
        else:
            return None

    def SearchPaperWithKeyword(self, keyword:str)->SemanticScholarInfo:
        req = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/search?query={keyword}&fields={','.join(self.fields)}&limit=1")
        if req.status_code == 200:
            if req.json()["total"]>0:
                return SemanticScholarInfo(req.json()["data"][0])
            else:
                raise None
        else:
            return None
        

      

class PaperProcessor:
    def __init__(self, paperData:SemanticScholarInfo):
        self.paperData = paperData.get_data()
        self.PaperInfo = paperData
        self.CreateOrIgnorePaperTable()
        
    def WritePaperInfo(self, target_path:str , paperData=None):

        def attachCurrentDate():
            return f"<span style='font-size:11;float:right;'>Information Update:{datetime.datetime.now().strftime('%b %d, %Y')}</span>"
        if paperData is None:
            paperData = self.paperData
        paper_id = paperData['paperId']
        title = paperData['title']
        url = paperData['url']
        publication_date = paperData['publicationDate']
        external_id = paperData['externalIds']
        citationCount = paperData['citationCount']
        fields_of_study = paperData['fieldsOfStudy']
        author = paperData['authors']
        paper_summary = f"""## Information 
- Title: {title}
- Author: {author}
- Publication Date: {publication_date}
- Citation: {citationCount}
- Url: {url}
- Paper ID:{paper_id}
"""
        paper_relationship = self.CreateLinkString()
        with open(target_path, 'w', encoding='utf8') as fp:
            fp.write(
                paper_summary
            )
            fp.write(paper_relationship)
            fp.write(attachCurrentDate())

    def GeneratePaperNote(self, paperId, target_dir):
        note_path = os.path.join(target_dir, f"{paperId}-note.md")
        if not os.path.exists(note_path):
            with open(note_path, 'w') as fp:
                fp.write(f"![[{paperId}-intro]]")
            
    def CreateOrIgnorePaperTable(self):
        sql = """
CREATE TABLE IF NOT EXISTS paper_information
(
id INTEGER PRIMARY KEY AUTOINCREMENT,
identifyId VARCHAR(128) NOT NULL,
paperId VARCHAR(128) NOT NULL,
title VARCHAR(256) NOT NULL,
authors TEXT NOT NULL,
citationCount INT NOT NULL DEFAULT 0,
publicationDate DATE NOT NULL,
fieldsOfStudy VARCHAR(128) NOT NULL,
url TEXT NOT NULL,
location TEXT NOT NULL,
paperPath TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS paperId_index ON paper_information(paperId);


CREATE TABLE IF NOT EXISTS paper_link
(
id INTEGER PRIMARY KEY AUTOINCREMENT,
source_id INT NOT NULL,
citation_id INT NOT NULL
);

CREATE INDEX IF NOT EXISTS paper_source_query ON paper_link(source_id);
CREATE INDEX IF NOT EXISTS paper_citation_query ON paper_link(citation_id);
CREATE UNIQUE INDEX IF NOT EXISTS paper_link_pair ON paper_link(source_id, citation_id);
"""
        return SqliteHelper('paper_db').ExecuteUpdate(sql)

        
    def GeneratePaperSetting(self, target_dir:str):
        data = dict()
        data.update(self.paperData)
        data.pop('citations')
        data.pop('references')
        paper_id = self.getPaperId()
        data['paperPath'] = os.path.join(target_dir, f"{paper_id}.pdf")
        data['mdPath'] = os.path.join(target_dir, f"{paper_id}-intro.md")
        data['location'] = target_dir
        data['identifyId'] = paper_id
        with open(os.path.join(target_dir, 'config.json'), 'w') as fp:
            json.dump(data, fp, indent=4)
        
        
    def getPaperId(self):
        if 'ArXiv' in self.paperData['externalIds']:
            paper_id = self.paperData['externalIds']['ArXiv']
        else:
            paper_id = self.paperData['paperId']
        return paper_id
    
    def UpdatePaperInfo(self, target_dir:str):
        data = dict()
        data.update(self.paperData)
        paper_id = self.getPaperId()
        data['paperPath'] = os.path.join(target_dir, f"{paper_id}.pdf")
        data['mdPath'] = os.path.join(target_dir, f"{paper_id}-intro.md")
        data['location'] = target_dir
        data['identifyId'] = paper_id
        sql = f"""
        INSERT OR IGNORE INTO paper_information('paperId','url','title','citationCount','fieldsOfStudy','publicationDate','authors','paperPath', 'location', 'identifyId')
        VALUES (:paperId,:url,:title,:citationCount,:fieldsOfStudy,:publicationDate,:authors,:paperPath, :location, :identifyId);
        """
        SqliteHelper('paper_db').ExecuteUpdate(sql, data)
        sql = f"""
        UPDATE paper_information SET paperPath=:paperPath, location=:location, citationCount=:citationCount WHERE paperId=:paperId;
        """
        SqliteHelper('paper_db').ExecuteUpdate(sql, data)

    def UpdatePaperLink(self):
        sql = """
        SELECT paperId FROM paper_information;
        """
        paper_link_list = []
        db_paper_id = [paper_id for paper_arr in SqliteHelper('paper_db').ExecuteSelect(sql) for paper_id in paper_arr]
        paper_id = self.paperData['paperId']
        cite_paper_ids = [ item['paperId'] for item in self.paperData['citations']]
        paper_ids_need_to_rewrite = []
        for cite_paper_id in cite_paper_ids:
            if cite_paper_id in db_paper_id:
                paper_link  = dict()
                paper_link['source_id'] = paper_id
                paper_link['citation_id'] = cite_paper_id
                paper_ids_need_to_rewrite.append(cite_paper_id)
                paper_link_list.append(paper_link)
        refer_paper_ids = [ item['paperId'] for item in self.paperData['references']]
        for refer_paper_id in refer_paper_ids:
            if refer_paper_id in db_paper_id:
                paper_link = dict()
                paper_link['source_id'] = refer_paper_id
                paper_link['citation_id'] = paper_id
                paper_ids_need_to_rewrite.append(refer_paper_id)
                paper_link_list.append(paper_link)
        sql = f"""
        INSERT OR IGNORE INTO paper_link (source_id, citation_id)
        VALUES (:source_id, :citation_id)
        """
        if len(paper_link_list) >0:
            SqliteHelper('paper_db').ExecuteUpdate(sql, paper_link_list)
        self.RewritePaperInformation(paper_ids_need_to_rewrite)
    
    def RewritePaperInformation(self, paper_ids):
        if len(paper_ids)>0:
            sql = f"""SELECT paperId, location FROM paper_information WHERE paperId IN ('{"','".join(paper_ids)}')"""
            paper_locs = {paper_info["paperId"]:paper_info['location'] for paper_info in SqliteHelper('paper_db').ExecuteSelect(sql)}
            for paper_id in paper_ids:
                if os.path.exists(os.path.join(paper_locs[paper_id], 'config.json')):
                    with open(os.path.join(paper_locs[paper_id], 'config.json'), 'r') as fp:
                        paper_data = json.load(fp)
                        self.WritePaperInfo(os.path.join(paper_data['location'], f"{paper_data['identifyId']}-intro.md"), paperData=paper_data)

    def CreateLinkString(self):
        def createPaperInternalLink(paper_infos:list[dict]):
            return_string = ""
            for paper_info in paper_infos:
                paper_file_name:str = paper_info['identifyId']
                return_string += f"[[{paper_file_name}-intro|{paper_info['title']}]] <br>"
            return return_string

        def createPaperLinkString(source_info, citation_info):
            return_string = f"{citation_info['paperId']}-->{source_info['paperId']}"
            return return_string 
        paper_id = self.paperData['paperId']
        reference_ids = self.GetReferences(paper_id)
        citation_ids = self.GetCitations(paper_id)
        current_paper_info = self.GetPapersInformation([paper_id])[0]
        reference_infos = self.GetPapersInformation((reference_ids))
        reference_link = [[ reference_info, current_paper_info] for reference_info in reference_infos]
        citation_infos = self.GetPapersInformation(citation_ids)
        citation_link = [[ current_paper_info, citation_info] for citation_info in citation_infos]
        paper_link = reference_link + citation_link
        paper_infos = reference_infos + citation_infos
        paper_infos.append(current_paper_info)
        newline_sign = '\n'
        if len(reference_ids)+len(citation_ids)>0:
            mermaid_string = f"""## Relationship
```mermaid
graph TD;
{newline_sign.join([f"{paper_info['paperId']}[{paper_info['title']}]" for paper_info in paper_infos])}
\n
{newline_sign.join([f"{createPaperLinkString(link[0], link[1])}" for link in paper_link])}
```
{createPaperInternalLink(paper_infos=paper_infos)}
"""
        else:
            mermaid_string = ""
        return mermaid_string
    
    def GetPapersInformation(self, paper_ids:list):
        sql = f"""
            SELECT * FROM paper_information WHERE paperId IN ('{"','".join(paper_ids)}')
        """
        result = SqliteHelper('paper_db').ExecuteDictSelect(sql)
        return result

    def GetReferences(self, paperId):
        sql = f"""
            SELECT source_id FROM paper_link WHERE citation_id = '{paperId}'
        """
        result = SqliteHelper('paper_db').ExecuteSelect(sql)
        return [sub_result[0] for sub_result in result]
        
    def GetCitations(self, paperId):
        sql = f"""
            SELECT citation_id FROM paper_link WHERE source_id = '{paperId}'
        """
        result = SqliteHelper('paper_db').ExecuteSelect(sql)
        return [sub_result[0] for sub_result in result]
    
    def GeneratePaperFolderByData(self, pdf_file_data, target_folder):
        paper_id = self.getPaperId()
        paper_path = os.path.join(target_folder, f"{paper_id}.pdf")
        with open(paper_path, 'wb') as fp:
            fp.write(pdf_file_data)
        md_path = os.path.join(os.path.join(target_folder, f"{paper_id}-intro.md"))
        self.GeneratePaperSetting(target_folder)
        self.UpdatePaperInfo(target_folder)
        self.WritePaperInfo(md_path)
        self.GeneratePaperNote(paper_id, target_folder)
        self.UpdatePaperLink()

    def CreateNewPaperFolder(self, pdf_file_path, target_folder):
        paper_id = self.getPaperId()
        paperPath = os.path.join(target_folder, f"{paper_id}.pdf")
        if not os.path.exists(paperPath):
            os.rename(pdf_file_path, paperPath)
        mdPath = os.path.join(os.path.join(target_folder, f"{paper_id}-intro.md"))
        self.GeneratePaperSetting(target_folder)
        self.UpdatePaperInfo(target_folder)
        self.WritePaperInfo(mdPath)
        self.GeneratePaperNote(paper_id, target_folder)
        self.UpdatePaperLink()

class PaperDataChecker:
    def __init__(self):
        pass
    def checkPaperInDb(self):
        sql = "SELECT paperId, paperPath FROM paper_information;"
        paper_infos = SqliteHelper('paper_db').ExecuteDictSelect(sql)
        paper_not_exist = [paper_info for paper_info in paper_infos if not os.path.exists(paper_info['paperPath'])]
        sql = "DELETE FROM paper_information WHERE paperId = :paperId"
        affect_rows = SqliteHelper('paper_db').ExecuteUpdate(sql, paper_not_exist)
        print(f"Delete {affect_rows} rows which paper path is invalid.")
        sql = "DELETE FROM paepr_link WHERE source_id = :paperId"
        SqliteHelper('paper_db').ExecuteUpdate(sql, paper_not_exist)
        sql = "DELETE FROM paper_link WHERE citation_id = :paperId"
        SqliteHelper('paper_db').ExecuteUpdate(sql, paper_not_exist)
