__version__ = (1, 0, 0)

#       █████  ██████   ██████ ███████  ██████  ██████   ██████ 
#       ██   ██ ██   ██ ██      ██      ██      ██    ██ ██      
#       ███████ ██████  ██      █████   ██      ██    ██ ██      
#       ██   ██ ██      ██      ██      ██      ██    ██ ██      
#       ██   ██ ██       ██████ ███████  ██████  ██████   ██████

#              © Copyright 2025
#           https://t.me/apcecoc
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @apcecoc
# scope: hikka_only
# scope: hikka_min 1.2.10

from .. import loader, utils
import io
import logging
from requests import get, post
import os
import tempfile
from telethon.tl.functions.users import GetFullUserRequest

logger = logging.getLogger(__name__)

@loader.tds
class UserInfoMod(loader.Module):
    """UserInfo in web interface"""
    strings = {
        "name": "UserInfo",
        "processing": "⏳ Обработка...",
        "no_user": "❌ Не указан пользователь или нет ответа на сообщение!",
        "screenshot_error": "❌ Ошибка получения информации о пользователе в веб-интерфейсе!",
        "processing_en": "⏳ Processing...",
        "no_user_en": "❌ No user specified or replied to!",
        "screenshot_error_en": "❌ Error retrieving user information in web interface!"
    }

    @loader.command(
        ru_doc="<@username/id/reply> Получить информацию о пользователе в веб-интерфейсе",
        es_doc="<@username/id/reply> Obtener información del usuario en la interfaz web",
        de_doc="<@username/id/reply> Benutzerinformationen in der Weboberfläche abrufen",
        en_doc="<@username/id/reply> Retrieve user information in the web interface"
    )
    async def usercmd(self, message):
        await utils.answer(message, self.strings["processing"])

        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)
        full_user = None

        try:
            if reply:
                full_user = await message.client(GetFullUserRequest(reply.sender_id))
            elif args:
                entity = await message.client.get_entity(args)
                full_user = await message.client(GetFullUserRequest(entity.id))
            else:
                await utils.answer(message, self.strings["no_user"])
                return
        except Exception:
            await utils.answer(message, self.strings["no_user"])
            return

        user = full_user.users[0]
        bio = full_user.full_user.about or "No bio available."

        photo = user.photo
        photo_url = await self.upload_user_photo(user, message) if photo else "https://via.placeholder.com/300x200"

        user_data = {
            "id": user.id,
            "username": user.username or "",
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "bio": bio,
            "photo": photo_url,
        }

        page_url = (
            f"https://apcecoc.github.io/apcecocuserinfo?"
            f"id={user_data['id']}"
            f"&username={user_data['username']}"
            f"&first_name={user_data['first_name']}"
            f"&last_name={user_data['last_name']}"
            f"&bio={utils.escape_html(user_data['bio'])}"
            f"&photo={user_data['photo']}"
        )

        screenshot_path = await self.take_screenshot(page_url)
        if not screenshot_path:
            await utils.answer(message, self.strings["screenshot_error"])
            return

        await message.client.send_file(message.chat_id, screenshot_path)

        if screenshot_path and os.path.exists(screenshot_path):
            os.remove(screenshot_path)

        await message.delete()

    async def take_screenshot(self, url):
        try:
            api_url = f"https://qnext.app/bin/webhooks/12921/666/rf5QV8tixrswFl3h?url={url}"
            response1 = get(api_url)

            if response1.status_code != 200:
                return None

            screenshot_url = response1.text.strip()
            response2 = get(screenshot_url)

            if response2.status_code != 200:
                return None

            screenshot_path = tempfile.mktemp(suffix=".jpg")
            with open(screenshot_path, "wb") as file:
                file.write(response2.content)

            return screenshot_path
        except Exception as e:
            logger.error(f"Ошибка получения информации о пользователе: {e}")
            return None

    async def upload_user_photo(self, user, message):
        try:
            photo = await message.client.download_profile_photo(user, file=bytes)
            if photo:
                photo_path = tempfile.mktemp(suffix=".jpg")
                with open(photo_path, "wb") as file:
                    file.write(photo)
                with open(photo_path, "rb") as file:
                    response = post("https://0x0.st", files={"file": file})
                if response.ok:
                    os.remove(photo_path)
                    return response.text.strip()
        except Exception as e:
            logger.error(f"Ошибка загрузки фотографии: {e}")
        return "https://via.placeholder.com/300x200"
