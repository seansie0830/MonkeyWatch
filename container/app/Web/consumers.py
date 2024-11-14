import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from rich.console import Console
import asyncio
import os
from channels.generic.websocket import AsyncWebsocketConsumer


console = Console()


class LiveStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        
        # 取得 HLS 檔案路徑
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        hls_file = os.path.join(BASE_DIR, 'hls', '19203683-uhd_3840_2160_60fps.m3u8')  

        # 讀取 m3u8 檔案
        with open(hls_file, 'r') as f:
            lines = f.readlines()

        # 提取 .ts 檔案列表
        ts_files = [line.strip() for line in lines if line.strip().endswith('.ts')]

        # 模擬直播：循環發送 ts 檔案內容
        while True:
            for ts_file in ts_files:
                ts_path = os.path.join(BASE_DIR, 'hls', ts_file)
                with open(ts_path, 'rb') as f:
                    while True:
                        chunk = f.read(4096)  # 調整每次發送的 chunk 大小
                        if not chunk:
                            break
                        await self.send(bytes_data=chunk)
                        await asyncio.sleep(0.1)  # 調整發送頻率
            await asyncio.sleep(1)  # 等待一段时间，模擬直播延遲

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        """
        當 WebSocket 連接建立時調用的方法。初始化聊天室並將當前通道添加到群組中。
        """
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        """
        當 WebSocket 連接關閉時調用的方法。將當前通道從群組中移除。
        """
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None, *args, **kwargs):
        """
        當從 WebSocket 接收到訊息時調用的方法。將訊息處理後廣播給群組中的所有人。
        """
        try:
            if text_data:
                # 解析接收到的 JSON 訊息
                text_data_json = json.loads(text_data)
                user = text_data_json.get('user', 'unknown')
                message = text_data_json.get('message', 'No message provided')
                action_code = text_data_json.get('action_code', '0000')

                # 打印接收到的訊息到控制台
                console.print(f"Received message from {user}: {message} with action code: {action_code}", style="bold green")

                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'broadcast_message',
                        'user': user,
                        'message': message,
                        'action_code': action_code,
                    }
                    )
                
                
            if bytes_data:
                text_message = bytes_data.decode('utf-8')
                text_data_json = json.loads(text_message)
                user = text_data_json.get('user', 'unknown')
                message = text_data_json.get('message', 'No message provided')
                action_code = text_data_json.get('action_code', '0000')

                # 打印接收到的訊息到控制台
                console.print(f"Received message from {user}: {message} with action code: {action_code}", style="bold green")

                # 廣播訊息到群組
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'broadcast_message',
                        'user': user,
                        'message': message,
                        'action_code': action_code,
                    }
                    )

        except Exception as e:
            console.print(f"Error processing message: {str(e)}", style="bold red")

    def broadcast_message(self, event):
        """
        將訊息廣播給所有 WebSocket 客戶端。
        """
        user = event['user']
        message = event['message']
        action_code = event['action_code']

        # 發送廣播訊息
        self.send(text_data=json.dumps({
            'user': user,
            'message': message,
            'action_code': action_code
        }))
