import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import (
    HighQualityAudio,
    HighQualityVideo,
    LowQualityVideo,
    MediumQualityVideo,
)
from youtubesearchpython import VideosSearch

from config import HNDLR, bot, call_py
from MusicAndVideo.helpers.queues import QUEUE, add_to_queue, get_queue


# music player
def ytsearch(query):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        duration = data["duration"]
        thumbnail = f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg"
        return [songname, url, duration, thumbnail]
    except Exception as e:
        print(e)
        return 0


async def ytdl(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        # CHANGE THIS BASED ON WHAT YOU WANT
        "bestaudio",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()


# video player
def ytsearch(query):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        duration = data["duration"]
        thumbnail = f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg"
        return [songname, url, duration, thumbnail]
    except Exception as e:
        print(e)
        return 0


async def ytdl(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        # CHANGE THIS BASED ON WHAT YOU WANT
        "best[height<=?720][width<=?1280]",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()


@Client.on_message(filters.command(["play", "پخش"], prefixes=f"{HNDLR}"))
async def play(client, m: Message):
    replied = m.reply_to_message
    chat_id = m.chat.id
    m.chat.title
    if replied:
        if replied.audio or replied.voice:
            await m.delete()
            huehue = await replied.reply("**درحال جستجو**")
            dl = await replied.download()
            link = replied.link
            if replied.audio:
                if replied.audio.title:
                    songname = replied.audio.title[:35] + "..."
                else:
                    songname = replied.audio.file_name[:35] + "..."
            elif replied.voice:
                songname = "Voice Note"
            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                await huehue.delete()
                # await m.reply_to_message.delete()
                await m.reply_photo(
                    photo="https://telegra.ph/file/f5abffb6b8d8ba8ba0e04.jpg",
                    caption=f"""
**#⃣ sᴏɴɢ ɪɴ ǫᴜᴇᴜᴇ {pos}
🏷️ تیتل: [{songname}]({link})
💬 چت ایدی: {chat_id}
🎧 درخواست کنندهᴛ: {m.from_user.mention}**
""",
                )
            else:
                await call_py.join_group_call(
                    chat_id,
                    AudioPiped(
                        dl,
                    ),
                    stream_type=StreamType().pulse_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                await huehue.delete()
                # await m.reply_to_message.delete()
                await m.reply_photo(
                    photo="https://telegra.ph/file/ac238261037cfd747b638.jpg",
                    caption=f"""
**▶ شروع پخش موزیک 
🏷️ توضیخات: [{songname}]({link})
💬 ایدی گپ: {chat_id}
🎧  درخواست کننده: {m.from_user.mention}**
""",
                )

    else:
        if len(m.command) < 2:
            await m.reply("ریپلی روی فایل برای پخش ")
        else:
            await m.delete()
            huehue = await m.reply("🔍 جستجو")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            if search == 0:
                await huehue.edit("`چیزی برای پلی دادن وجود ندارد`")
            else:
                songname = search[0]
                url = search[1]
                duration = search[2]
                thumbnail = search[3]
                hm, ytlink = await ytdl(url)
                if hm == 0:
                    await huehue.edit(f"**ارور یوتیوب ⚠️** \n\n`{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        pos = add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                        await huehue.delete()
                        # await m.reply_to_message.delete()
                        await m.reply_photo(
                            photo=f"{thumbnail}",
                            caption=f"""
**#⃣ پخش اهنگ  {pos}
🏷️ توضیحات : [{songname}]({url})
⏱️ مدت زمان : {duration}
💬 ایدی گروه : {chat_id}
🎧 درخواست کننده : {m.from_user.mention}**
""",
                        )
                    else:
                        try:
                            await call_py.join_group_call(
                                chat_id,
                                AudioPiped(
                                    ytlink,
                                ),
                                stream_type=StreamType().pulse_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                            await huehue.delete()
                            # await m.reply_to_message.delete()
                            await m.reply_photo(
                                photo=f"{thumbnail}",
                                caption=f"""
**▶ شروع پخش اهنگ 
🏷️ توضیحات: [{songname}]({url})
⏱️ مدت زمان : {duration}
💬 ایدی گروه : {chat_id}
🎧 درخواست کننده: {m.from_user.mention}**
""",
                            )
                        except Exception as ep:
                            await huehue.edit(f"`{ep}`")


@Client.on_message(filters.command(["vplay", "ویدیو پخش"], prefixes=f"{HNDLR}"))
async def vplay(client, m: Message):
    replied = m.reply_to_message
    chat_id = m.chat.id
    m.chat.title
    if replied:
        if replied.video or replied.document:
            await m.delete()
            huehue = await replied.reply("**🔍 درحال جستجو**")
            dl = await replied.download()
            link = replied.link
            if len(m.command) < 2:
                Q = 720
            else:
                pq = m.text.split(None, 1)[1]
                if pq == "720" or "480" or "360":
                    Q = int(pq)
                else:
                    Q = 720
                    await huehue.edit(
                        "`ᴏɴʟʏ 720,  480,  360 ᴀʟʟᴏᴡᴇᴅ` \n `ɴᴏᴡ sᴛʀᴇᴀᴍɪɴɢ ɪɴ 720ᴘ`"
                    )

            if replied.video:
                songname = replied.video.file_name[:35] + "..."
            elif replied.document:
                songname = replied.document.file_name[:35] + "..."

            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, dl, link, "Video", Q)
                await huehue.delete()
                # await m.reply_to_message.delete()
                await m.reply_photo(
                    photo="https://telegra.ph/file/f5abffb6b8d8ba8ba0e04.jpg",
                    caption=f"""
**#⃣ پخش ویدیو  {pos}
🏷️ توظیحات : [{songname}]({link})
💬 ایدی گپ: {chat_id}
🎧 درخواست کننده: {m.from_user.mention}**
""",
                )
            else:
                if Q == 720:
                    hmmm = HighQualityVideo()
                elif Q == 480:
                    hmmm = MediumQualityVideo()
                elif Q == 360:
                    hmmm = LowQualityVideo()
                await call_py.join_group_call(
                    chat_id,
                    AudioVideoPiped(dl, HighQualityAudio(), hmmm),
                    stream_type=StreamType().pulse_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Video", Q)
                await huehue.delete()
                # await m.reply_to_message.delete()
                await m.reply_photo(
                    photo="https://telegra.ph/file/ac238261037cfd747b638.jpg",
                    caption=f"""
**▶ شروع پخش ویدیو
🏷️ اطلاعات: [{songname}]({link})
💬 ᴄʜᴀᴛ ɪᴅ: {chat_id}
🎧 ᴜsᴇʀ ʀᴇǫᴜᴇsᴛ: {m.from_user.mention}**
""",
                )

    else:
        if len(m.command) < 2:
            await m.reply("**روی فایل ریپلی بزن**")
        else:
            await m.delete()
            huehue = await m.reply("**🔎جستجو")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            Q = 720
            hmmm = HighQualityVideo()
            if search == 0:
                await huehue.edit("**چیزی برای جستجو وجود ندارد**")
            else:
                songname = search[0]
                url = search[1]
                duration = search[2]
                thumbnail = search[3]
                hm, ytlink = await ytdl(url)
                if hm == 0:
                    await huehue.edit(f"**ارور یوتیوب⚠️** \n\n`{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        pos = add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                        await huehue.delete()
                        # await m.reply_to_message.delete()
                        await m.reply_photo(
                            photo=f"{thumbnail}",
                            caption=f"""
**#⃣ ویدیو {pos}
🏷️ اطلاعات: [{songname}]({url})
⏱️ مدت زمان : {duration}
💬 ایدی گروه : {chat_id}
🎧 درخواست کننده: {m.from_user.mention}**
""",
                        )
                    else:
                        try:
                            await call_py.join_group_call(
                                chat_id,
                                AudioVideoPiped(ytlink, HighQualityAudio(), hmmm),
                                stream_type=StreamType().pulse_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                            await huehue.delete()
                            # await m.reply_to_message.delete()
                            await m.reply_photo(
                                photo=f"{thumbnail}",
                                caption=f"""
**▶ویدیو پخش شد
🏷️ اطلاعات: [{songname}]({url})
⏱️ مدت زمان : {duration}
💬 ایدی گپ: {chat_id}
🎧 درخواست کننده: {m.from_user.mention}**
""",
                            )
                        except Exception as ep:
                            await huehue.edit(f"`{ep}`")


@Client.on_message(filters.command(["playfrom"], prefixes=f"{HNDLR}"))
async def playfrom(client, m: Message):
    chat_id = m.chat.id
    if len(m.command) < 2:
        await m.reply(
            f"**ᴜsᴇ:** \n\n`{HNDLR}ᴘʟᴀʏ ғʀᴏᴍ [ᴄʜᴀᴛ ɪᴅ /ᴜsᴇʀɴᴀᴍᴇ]` \n`{HNDLR}ᴘʟᴀʏ ғʀᴏᴍ [ᴄʜᴀᴛ ɪᴅ/ᴜsᴇʀɴᴀᴍᴇ]`"
        )
    else:
        args = m.text.split(maxsplit=1)[1]
        if ";" in args:
            chat = args.split(";")[0]
            limit = int(args.split(";")[1])
        else:
            chat = args
            limit = 10
            lmt = 9
        await m.delete()
        hmm = await m.reply(f"🔎جستجو {limit} ʀᴀɴᴅᴏᴍ sᴏɴɢ ғʀᴏᴍ {chat}**")
        try:
            async for x in bot.search_messages(chat, limit=limit, filter="audio"):
                location = await x.download()
                if x.audio.title:
                    songname = x.audio.title[:30] + "..."
                else:
                    songname = x.audio.file_name[:30] + "..."
                link = x.link
                if chat_id in QUEUE:
                    add_to_queue(chat_id, songname, location, link, "Audio", 0)
                else:
                    await call_py.join_group_call(
                        chat_id,
                        AudioPiped(location),
                        stream_type=StreamType().pulse_stream,
                    )
                    add_to_queue(chat_id, songname, location, link, "Audio", 0)
                    # await m.reply_to_message.delete()
                    await m.reply_photo(
                        photo="https://telegra.ph/file/ac238261037cfd747b638.jpg",
                        caption=f"""
**▶ موزیک {chat}
🏷️ توضیحات: [{songname}]({link})
💬 ایدی گپ: {chat_id}
🎧 درخواست کننده: {m.from_user.mention}**
""",
                    )
            await hmm.delete()
            await m.reply(
                f"➕ ᴀᴅᴅ {lmt} sᴏɴɢ ɪɴᴛᴏ ᴛʜᴇ ǫᴜᴇᴜᴇ \n• ᴄʟɪᴄᴋ {HNDLR}ᴘʟᴀʏʟɪsᴛ ᴛᴏ ᴠɪᴇᴡ ᴘʟᴀʏʟɪsᴛ**"
            )
        except Exception as e:
            await hmm.edit(f"**ᴇʀʀᴏʀ** \n`{e}`")


@Client.on_message(filters.command(["playlist", "لیست پخش"], prefixes=f"{HNDLR}"))
async def playlist(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if len(chat_queue) == 1:
            await m.delete()
            await m.reply(
                f"**🎧لیست پخش:** \n[{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][3]}`",
                disable_web_page_preview=True,
            )
        else:
            QUE = f"**🎧لیست پخش:** \n[{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][3]}` \n\n**⏯ QUEUE LIST:**"
            l = len(chat_queue)
            for x in range(1, l):
                hmm = chat_queue[x][0]
                hmmm = chat_queue[x][2]
                hmmmm = chat_queue[x][3]
                QUE = QUE + "\n" + f"**#{x}** - [{hmm}]({hmmm}) | `{hmmmm}`\n"
            await m.reply(QUE, disable_web_page_preview=True)
    else:
        await m.reply("**❌ لیست پخشی وجود ندارد**")
