from django.urls import path
from . import views

app_name = "Web"

from django.urls import path
from . import views

urlpatterns = [
    path('weekly-tasks/', views.WeeklyTaskView.as_view(), name='weekly-task-list'),
    path('tasks/<int:pk>/complete/', views.TaskCompletionUpdateView.as_view(), name='task-complete-update'),
	path('api/detection_results/', views.monkeyEventShow ,name="monkeyEventShow"),
	path('api/detection_results/image/<int:imageid>' ,views.imageshow ,name= "imageshow"),
	path('api/upload_image',views.imageupload ,name='imageupload'),
	path('api/history/', views.history, name='history'),
	path('api/debugUpload', views.post ,name='post'),   # ! would be removed in productive enviroment
	path('upload_hls/', views.upload_hls_segment, name='upload_hls_segment'),
]