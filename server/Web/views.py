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

@csrf_exempt
@api_view(['POST'])
def post(request, format=None):
    if request.method == 'POST':
        serializer = MonkeyDetectionEventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 



@csrf_exempt
def imageupload(request):
    image_file = request.FILES.get('image')
    instance =Image(image=image_file )
    instance.save()
    return HttpResponse()

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
