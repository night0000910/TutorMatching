from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from django.utils import timezone

import json
import math

from . import models

User = get_user_model()


# --- DB操作用関数 ---

@database_sync_to_async
def update_class_start_datetime(user):
    user.class_start_datetime = timezone.now()
    user.save(update_fields=["class_start_datetime"])


@database_sync_to_async
def update_class_ending_datetime_and_rank(user):
    now = timezone.now()
    user.class_ending_datetime = now

    # 開始時間が存在する場合のみ時間を計算（Noneエラー防止）
    if user.class_start_datetime:
        spent_delta = user.class_ending_datetime - user.class_start_datetime
        added_minutes = math.floor(spent_delta.total_seconds() / 60)

        # 負の値にならないよう安全対策
        if added_minutes > 0:
            user.spent_time += added_minutes

        # ランク更新
        spent_time = user.spent_time
        if spent_time < 1500:
            user.rank = "bronze"
        elif 1500 <= spent_time < 3000:
            user.rank = "silver"
        elif 3000 <= spent_time < 4500:
            user.rank = "gold"
        else:
            user.rank = "diamond"

    user.save()


# --- Consumer ---

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # 1. 本人確認（AuthMiddlewareStack経由のログインユーザー情報を使う）
        self.user = self.scope.get("user")
        url_user_id = self.scope["url_route"]["kwargs"]["user_id"]

        # 未ログイン、またはURLのIDとログインIDが一致しない場合は拒否
        if not self.user or not self.user.is_authenticated or str(self.user.id) != str(url_user_id):
            await self.close()
            return

        class_id = self.scope["url_route"]["kwargs"]["class_id"]
        self.room_group_name = f"class_{class_id}"  # 数字だけのグループ名回避

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # 授業開始時刻を更新
        await update_class_start_datetime(self.user)

    async def disconnect(self, close_code):
        # 正常に接続できていた場合のみ離脱・更新処理を行う
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        print("通信が切断されました")

        # 認証済みユーザーの場合のみDB更新
        if hasattr(self, "user") and self.user.is_authenticated:
            try:
                await update_class_ending_datetime_and_rank(self.user)
            except Exception as e:
                print(f"切断時のデータ更新中にエラーが発生しました: {e}")

    async def receive(self, text_data):
        try:
            receive_dict = json.loads(text_data)
            action = receive_dict.get("action")

            if (action == "new-offer") or (action == "new-answer"):
                receiver_channel_name = receive_dict["message"]["receiver_channel_name"]
                receive_dict["message"]["receiver_channel_name"] = self.channel_name

                await self.channel_layer.send(
                    receiver_channel_name,
                    {
                        "type": "send.sdp",
                        "receive_dict": receive_dict,
                    }
                )
                return

            receive_dict["message"]["receiver_channel_name"] = self.channel_name

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send.sdp",
                    "receive_dict": receive_dict,
                }
            )
        except Exception as e:
            print(f"受信処理中のエラー: {e}")

    async def send_sdp(self, event):
        receive_dict = event["receive_dict"]
        await self.send(text_data=json.dumps(receive_dict))