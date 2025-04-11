from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import datetime

import os
import sys
import json 

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import traceback
from src.component.search_engine import SearchEngine
from src.utils.dao import PaperProcessor
import env as paper_env

# Create your views here.

search_engine = SearchEngine()

@csrf_exempt
def FindPaperByPaperIds(request):
    if request.method == "POST":
        data = json.loads(request.body)
        paper_ids = data.get('paperIds', None)
        if not paper_ids:
            return JsonResponse({"action":"invalid input"}, status=422)
        target_folder = paper_env.ASSET_FOLDER
        res = search_engine.SearchWithPaperIds(paper_ids)
        return JsonResponse({"action":"executed", "result":res})
    else:
        return JsonResponse({"message":f"Invalid method {request.method}"}, status=502)

@csrf_exempt
def FindPaperByDoi(request):
    if request.method == "POST":
        data = json.loads(request.body)
        doi = data.get('doi', None)
        paper_path = data.get("file_path", None)
        if not paper_path or not doi:
            return JsonResponse({"action":"invalid input"}, status=422)
        target_folder = target_folder = paper_env.ASSET_FOLDER
        res = search_engine.SearchWithDoi(paper_path, target_folder, doi)
        if not res:
            return JsonResponse({"action":"not found"}, status=204)
        return JsonResponse({"action":"found", "data":res}, status=200)
    

@csrf_exempt
def FindPaperByTitle(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get('title', None)
        paper_path = data.get("file_path", None)
        if not paper_path or not title:
            return JsonResponse({"action":"invalid input"}, status=422)
        target_folder = target_folder = paper_env.ASSET_FOLDER
        res = search_engine.SearchWithTitle(paper_path, target_folder, title)
        if not res:
            return JsonResponse({"action":"not found"}, status=204)
        return JsonResponse({"action":"found", "data":res}, status=200)

@csrf_exempt
def FindPaperByArxivId(request):
    if request.method == "POST":
        data = json.loads(request.body)
        paper_id = data.get('paper_id', None)
        paper_path = data.get("file_path", None)
        if not paper_path or not paper_id:
            return JsonResponse({"action":"invalid input"}, status=422)
        target_folder = target_folder = paper_env.ASSET_FOLDER
        res = search_engine.SearchWithPaperId(paper_path, target_folder, paper_id)
        if not res:
            return JsonResponse({"action":"not found"}, status=204)
        return JsonResponse({"action":"found", "data":res}, status=200)

@csrf_exempt
def AcceptChange(paper_infos, target_dir = None):
    res = {"action":"Shift", "data":{'success':{}, 'failed':{}}}
    if target_dir is None:
        target_dir = paper_env.ASSET_FOLDER
    for paper_path in paper_infos:
        try:
            paper_info = paper_infos[paper_path]
            publication_date = datetime.datetime.strptime(paper_info['publicationDate'], "%Y-%m-%d").strftime('%Y%m%d') if paper_info['publicationDate'] else "Unknown"
            paper_title = paper_info['title'].replace("?", "").replace(":", "")
            folder_name = os.path.join(target_dir, f"{publication_date} {paper_title}")
            processor = PaperProcessor(paper_info)
            os.makedirs(folder_name, exist_ok=True)
            processor.CreateNewPaperFolder(paper_path, folder_name)
            res['data']['success'][paper_path] = folder_name
        except Exception:
            res['data']['failed'][paper_path] = traceback.format_exc()



