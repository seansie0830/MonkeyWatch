import time  # 加入這一行
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, UpdateAPIView
from .models import *
from .serializers import GroupedWeeklyTaskSerializer, WeeklyTaskSerializer, CompletionStatusSerializer
from django.shortcuts import get_object_or_404
from django.http import JsonResponse , HttpResponse
import datetime  # 引入 datetime 模組
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import MonkeyDetectionEventSerializer

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os

@api_view(['POST'])
@csrf_exempt
def upload_hls_segment(request):
  if request.method == 'POST':
    # 從請求中取得 HLS 片段資料
    segment_data = request.body

    # 建立儲存 HLS 片段的目錄 (如果不存在)
    media_root = 'media/hls'  # 替換成你的媒體檔案根目錄
    os.makedirs(media_root, exist_ok=True)

    # 產生唯一的檔案名稱
    segment_filename = f'{os.path.join(media_root, "segment_" + str(int(time.time())))}.ts'  

    # 將 HLS 片段儲存到檔案
    with open(segment_filename, 'wb') as f:
      f.write(segment_data)

    return HttpResponse('HLS segment uploaded successfully.')
  else:
    return HttpResponse('Invalid request method.', status=405)

@csrf_exempt
@api_view(['POST'])
def post(request, format=None):
    if request.method == 'POST':
        serializer = MonkeyDetectionEventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 



import json
import random
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

def  get_detection_result_json(result, monkey_amount=None):  # 使用預設參數
    """產生 JSON 格式的 detection result。"""
    data = {
        "detection_result": result
    }
    if monkey_amount is not None:  # 只在 monkey_amount 有值時才加入
        data["monkey_amount"] = monkey_amount
    return json.dumps(data)

@csrf_exempt
def imageupload(request):
    image_file = request.FILES.get('image')
    
    # 檢查是否有上傳圖片
    if not image_file:
        json_response = get_detection_result_json("image not upload")  # monkey_amount 使用預設值 None
        return HttpResponse(json_response, content_type='application/json', status=400)  # Bad Request: 表示客户端请求有误

    try:
        instance = Image(image=image_file)
        instance.save()

        # 產生隨機的 monkey_amount 值
        monkey_amount = random.randint(0, 10) 

        # 產生 JSON 格式的 detection result
        json_response = get_detection_result_json("結果", monkey_amount)

        return HttpResponse(json_response, content_type='application/json') 

    except Exception as e:  # 捕捉所有錯誤
        error_response = json.dumps({"error": f"儲存圖片或產生 JSON 時發生錯誤：{str(e)}"})
        return HttpResponse(error_response, content_type='application/json', status=500)  # Internal Server Error: 表示服务器端发生错误

def imageshow(request,imageid):
    obj = get_object_or_404(Image, pk=imageid)
    image_file = obj.image.open()  # 開啟 ImageField 檔案
    response = HttpResponse(image_file.read(), content_type="image/jpeg")  # 或其他圖片類型
    return response
def serialize_events(events):
    event_list = []
    for event in events:
            event_data = {
                'id': event.id,
                'image_id': event.image.id,  # Include the related image ID
                'timestamp': event.timestamp.isoformat(),  # Format timestamp for JSON serialization
                'location': event.location,
                'monkey_count': event.monkey_count,
                'verdict': event.verdict,
                'mark': event.mark,
            }
            event_list.append(event_data)
    return event_list

def monkeyEventShow(request):
    if(request.GET.get("date") == None) :
        events= MonkeyDetectionEvent.objects.all()
        event_list=serialize_events(events)
        return JsonResponse(event_list, safe=False)
    else:
        try:
            date_str = request.GET.get("date")
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            events = MonkeyDetectionEvent.objects.filter(timestamp__date=date_obj)
            event_list=serialize_events(events)
            return JsonResponse(event_list, safe=False)
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=400)
        

from django.shortcuts import render
from django.http import JsonResponse
from .models import MonkeyDetectionEvent
from django.db.models import Q

def history(request):
    """
    API endpoint for filtering MonkeyDetectionEvent objects based on query parameters.
    """
    try:
        # Get all query parameters
        query_params = request.GET.dict()

        # Build filter conditions
        filter_kwargs = {}
        for key, value in query_params.items():
            # Add __icontains for string fields for partial matching
            if isinstance(getattr(MonkeyDetectionEvent, key.split('__')[0], None), str):
                key += '__icontains'  
            filter_kwargs[key] = value

        # Filter events
        events = MonkeyDetectionEvent.objects.filter(**filter_kwargs)

        # Serialize the events
        event_list = serialize_events(events) 

        return JsonResponse(event_list, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
# List all WeeklyTasks
class WeeklyTaskView(APIView):
    def get(self, request):
        # Get all weekly tasks
        weekly_tasks = WeeklyTask.objects.all()

        # Pass queryset to the serializer
        serializer = GroupedWeeklyTaskSerializer(weekly_tasks)

        # Return serialized data
        return Response(serializer.data)
    
# Patch API to update task completion status
class TaskCompletionUpdateView(UpdateAPIView):
    serializer_class = CompletionStatusSerializer

    def patch(self, request, pk, *args, **kwargs):
        task = get_object_or_404(DailyTask, pk=pk)
        completion_status_data = request.data.get('completion_status')

        # Either create a new CompletionStatus or update the existing one
        if task.completion_status:
            completion_status = task.completion_status
            serializer = CompletionStatusSerializer(completion_status, data=completion_status_data, partial=True)
        else:
            serializer = CompletionStatusSerializer(data=completion_status_data)

        if serializer.is_valid():
            # If no existing completion status, assign the newly created one
            if not task.completion_status:
                completion_status = serializer.save()
                task.completion_status = completion_status
                task.save()
            else:
                serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
