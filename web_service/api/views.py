from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import os
import sys
import json 

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from src.component.paper_register import PaperRegister
import env as paper_env

# Create your views here.

register = PaperRegister()

@csrf_exempt
def FindPaperByFolder(request):
    if request.method == "POST":
        data = json.loads(request.body)
        source_folder = data.get('source_folder', None)
        if not source_folder:
            return JsonResponse({"action":"invalid input"}, status=422)
        target_folder = paper_env.ASSET_FOLDER
        res = register.RegisterWithPapersFolder(source_folder, target_folder)
        return JsonResponse({"action":"executed", "result":res})

@csrf_exempt
def FindPaperByDoi(request):
    if request.method == "POST":
        data = json.loads(request.body)
        doi = data.get('doi', None)
        paper_path = data.get("file_path", None)
        if not paper_path or not doi:
            return JsonResponse({"action":"invalid input"}, status=422)
        target_folder = target_folder = paper_env.ASSET_FOLDER
        res = register.RegisterWithDoi(paper_path, target_folder, doi)
        if not res:
            return JsonResponse({"action":"not found"}, status=204)
        return JsonResponse({"action":"found"}, status=200)
    

@csrf_exempt
def FindPaperByTitle(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get('title', None)
        paper_path = data.get("file_path", None)
        if not paper_path or not title:
            return JsonResponse({"action":"invalid input"}, status=422)
        target_folder = target_folder = paper_env.ASSET_FOLDER
        res = register.RegisterWithTitle(paper_path, target_folder, title)
        if not res:
            return JsonResponse({"action":"not found"}, status=204)
        return JsonResponse({"action":"found"}, status=200)

@csrf_exempt
def FindPaperByArxivId(request):
    if request.method == "POST":
        data = json.loads(request.body)
        paper_id = data.get('paper_id', None)
        paper_path = data.get("file_path", None)
        if not paper_path or not paper_id:
            return JsonResponse({"action":"invalid input"}, status=422)
        target_folder = target_folder = paper_env.ASSET_FOLDER
        res = register.RegisterWithPaperId(paper_path, target_folder, paper_id)
        if not res:
            return JsonResponse({"action":"not found"}, status=204)
        return JsonResponse({"action":"found"}, status=200)



