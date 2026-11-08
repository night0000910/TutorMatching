from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from django.utils import timezone

import json
import datetime
import math
import asyncio

from . import models


# 授業開始時刻をデータベースに記録する
@database_sync_to_async
def update_class_start_datetime(user_id):
    now = timezone.now()
    user = get_user_model().objects.get(id=user_id)
    user.class_start_datetime = now
    user.save()

# 授業終了時刻をデータベースに記録する
@database_sync_to_async
def update_class_ending_datetime(user_id):
    now = timezone.now()
    user = get_user_model().objects.get(id=user_id)
    user.class_ending_datetime = now
    user.save()

# 授業に費やした時間をデータベースに記録する
@database_sync_to_async
def update_spent_time(user_id):
    user = get_user_model().objects.get(id=user_id)
    spent_time = user.class_ending_datetime - user.class_start_datetime
    user.spent_time += math.floor(spent_time.seconds/60)
    user.save()

# ランクを更新する
@database_sync_to_async
def update_rank(user_id):
    user = get_user_model().objects.get(id=user_id)
    spent_time = user.spent_time

    if spent_time < 1500:
        user.rank = "bronze"
    elif 1500 <= spent_time < 3000:
        user.rank = "silver"
    elif 3000 <= spent_time < 4500:
        user.rank = "gold"
    elif spent_time >= 4500:
        user.rank = "diamond"

    user.save()

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        class_id = self.scope["url_route"]["kwargs"]["class_id"]
        self.room_group_name = class_id
        print(f"グループ名 : {self.room_group_name}")

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        user_id = self.scope["url_route"]["kwargs"]["user_id"]
        await update_class_start_datetime(user_id)

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        print("通信が切断されました")

        user_id = self.scope["url_route"]["kwargs"]["user_id"]
        await update_class_ending_datetime(user_id)
        await update_spent_time(user_id)
        await update_rank(user_id)

    async def receive(self, text_data):

        receive_dict = json.loads(text_data)
        message = receive_dict["message"]
        action = receive_dict["action"]

        if (action == "new-offer") or (action == "new-answer"):
            receiver_channel_name = receive_dict["message"]["receiver_channel_name"]

            receive_dict["message"]["receiver_channel_name"] = self.channel_name

            await self.channel_layer.send(
                receiver_channel_name,
                {
                    "type" : "send.sdp",
                    "receive_dict" : receive_dict,
                }
            )

            return
        
        receive_dict["message"]["receiver_channel_name"] = self.channel_name

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type" : "send.sdp",
                "receive_dict" : receive_dict,
            }
        )

    async def send_sdp(self, event):
        receive_dict = event["receive_dict"]

        await self.send(text_data=json.dumps(receive_dict))