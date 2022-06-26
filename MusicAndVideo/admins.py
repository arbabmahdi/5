from pyrogram import Client, filters
from pyrogram.types import Message

from config import HNDLR, call_py
from MusicAndVideo.helpers.decorators import authorized_users_only
from MusicAndVideo.helpers.handlers import skip_current_song, skip_item
from MusicAndVideo.helpers.queues import QUEUE, clear_queue


@Client.on_message(filters.command(["skip", "بعدی"], prefixes=f"{HNDLR}"))
@authorized_users_only
async def skip(client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    if len(m.command) < 2:
        op = await skip_current_song(chat_id)
        if op == 0:
            await m.reply("**موزیکی برای پلی دادن وجود ندارد**")
        elif op == 1:
            await m.reply("Eᴍᴘᴛʏ ǫᴜᴇᴜᴇ  ʟᴇᴀᴠɪɴɢ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ**")
        else:
            await m.reply(
                f"**⏭ موزیک بعدی** \n**🎧 پخش جدید** - [{op[0]}]({op[1]}) | `{op[2]}`",
                disable_web_page_preview=True,
            )
    else:
        skip = m.text.split(None, 1)[1]
        OP = "**🗑️ Rᴇᴍᴏᴠᴇᴅ ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ sᴏɴɢs ғʀᴏᴍ ᴛʜᴇ ǫᴜᴇᴜᴇ: -**"
        if chat_id in QUEUE:
            items = [int(x) for x in skip.split(" ") if x.isdigit()]
            items.sort(reverse=True)
            for x in items:
                if x == 0:
                    pass
                else:
                    hm = await skip_item(chat_id, x)
                    if hm == 0:
                        pass
                    else:
                        OP = OP + "\n" + f"**#⃣{x}** - {hm}"
            await m.reply(OP)


@Client.on_message(filters.command(["end", "اتمام"], prefixes=f"{HNDLR}"))
@authorized_users_only
async def stop(client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.leave_group_call(chat_id)
            clear_queue(chat_id)
            await m.reply("**✅ پایان یافت **")
        except Exception as e:
            await m.reply(f"**ᴇʀʀᴏʀ** \n`{e}`")
    else:
        await m.reply("**❌ چیزی برای پخش وجود ندارد **")


@Client.on_message(filters.command(["paused", "توقف"], prefixes=f"{HNDLR}"))
@authorized_users_only
async def pause(client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.pause_stream(chat_id)
            await m.reply(
                f"**⏸ موزیک متوقف شد**\n\n• برای ادامه دادن دستور . ادامه . را ارسال کنید » {HNDLR}ʀᴇsᴜᴍᴇ"
            )
        except Exception as e:
            await m.reply(f"**ᴇʀʀᴏʀ** \n`{e}`")
    else:
        await m.reply("** ❌ چیزی برای ادامه وجود ندارد**")


@Client.on_message(filters.command(["resumed", "ادامه"], prefixes=f"{HNDLR}"))
@authorized_users_only
async def resume(client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.resume_stream(chat_id)
            await m.reply(
                f"**▶ادامه یافت **\n\n• برای متوقف کردن دستور توقف را ارسال کنید » {HNDLR}ᴘᴀᴜsᴇ**"
            )
        except Exception as e:
            await m.reply(f"**ارور** \n`{e}`")
    else:
        await m.reply("**❌ چیزی برای توقف وجود ندارد**")
