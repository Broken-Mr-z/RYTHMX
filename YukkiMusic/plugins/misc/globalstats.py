import platform
from sys import version as pyver
from typing import Union

import psutil
from pyrogram import __version__ as pyrover
from pyrogram import filters, types
from pyrogram.types import (InlineKeyboardButton,
                            InlineKeyboardMarkup, InputMediaPhoto)

import config
from config import BANNED_USERS, MUSIC_BOT_NAME
from strings import get_command, get_string
from YukkiMusic import YouTube, app
from YukkiMusic.core.userbot import assistants
from YukkiMusic.misc import SUDOERS, pymongodb
from YukkiMusic.utils.database import (get_global_tops, get_lang,
                                       get_particulars, get_queries,
                                       get_served_chats,
                                       get_served_users, get_sudoers,
                                       get_top_chats, get_topp_users,
                                       is_commanddelete_on)
from YukkiMusic.utils.decorators.language import languageCB
from YukkiMusic.utils.inline.stats import (back_stats_markup,
                                           overallback_stats_markup,
                                           top_ten_stats_markup)

# Commands
STATS_COMMAND = get_command("STATS_COMMAND")


@app.on_message(
    filters.command(STATS_COMMAND) & filters.group & ~BANNED_USERS
)
@app.on_callback_query(filters.regex("GlobalStats") & ~BANNED_USERS)
async def stats_global(
    client: app, update: Union[types.Message, types.CallbackQuery]
):
    is_callback = isinstance(update, types.CallbackQuery)
    if is_callback:
        try:
            await update.answer()
        except:
            pass
        chat_id = update.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        mystic = await update.edit_message_text(_["set_cb_8"])
    else:
        chat_id = update.chat.id
        if await is_commanddelete_on(update.chat.id):
            try:
                await update.delete()
            except:
                pass
        language = await get_lang(chat_id)
        _ = get_string(language)
        mystic = await update.reply_text(_["gstats_1"])
    stats = await get_global_tops()
    if not stats:
        return await mystic.edit(_["gstats_2"])
    results = {}
    for i in stats:
        top_list = stats[i]["spot"]
        results[str(i)] = top_list
        list_arranged = dict(
            sorted(
                results.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )
    if not results:
        return await mystic.edit(_["gstats_2"])
    videoid = None
    co = None
    for vidid, count in list_arranged.items():
        if vidid == "telegram":
            continue
        else:
            videoid = vidid
            co = count
        break
    (
        title,
        duration_min,
        duration_sec,
        thumbnail,
        vidid,
    ) = await YouTube.details(videoid, True)
    title = title.title()
    final = f"??????s??? ???????????????? ?????????????? ???????? {MUSIC_BOT_NAME}\n\n**?????????????:** {title}\n\n???????????????????** {co} **???????????s???"
    not_sudo = [
        InlineKeyboardButton(
            text=_["CLOSEMENU_BUTTON"],
            callback_data="close",
        )
    ]
    sudo = [
        InlineKeyboardButton(
            text=_["SA_B_8"],
            callback_data="bot_stats_sudo",
        ),
        InlineKeyboardButton(
            text=_["CLOSEMENU_BUTTON"],
            callback_data="close",
        ),
    ]
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["SA_B_7"],
                    callback_data="TOPMARKUPGET",
                )
            ],
            [
                InlineKeyboardButton(
                    text=_["SA_B_6"],
                    url=f"https://t.me/{app.username}?start=stats",
                ),
                InlineKeyboardButton(
                    text=_["SA_B_5"],
                    callback_data="TopOverall",
                ),
            ],
            sudo if update.from_user.id in SUDOERS else not_sudo,
        ]
    )
    if is_callback:
        med = InputMediaPhoto(media=thumbnail, caption=final)
        await update.edit_message_media(media=med, reply_markup=upl)
    else:
        await mystic.delete()
        await app.send_photo(
            chat_id, photo=thumbnail, caption=final, reply_markup=upl
        )


@app.on_callback_query(filters.regex("TOPMARKUPGET") & ~BANNED_USERS)
@languageCB
async def too_ten_reply(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except:
        pass
    upl = top_ten_stats_markup(_)
    med = InputMediaPhoto(
        media=config.GLOBAL_IMG_URL,
        caption=_["tops_10"],
    )
    await CallbackQuery.edit_message_media(
        media=med, reply_markup=upl
    )


@app.on_callback_query(filters.regex("TopOverall") & ~BANNED_USERS)
@languageCB
async def overall_stats(client, CallbackQuery, _):
    upl = overallback_stats_markup(_)
    try:
        await CallbackQuery.answer()
    except:
        pass
    await CallbackQuery.edit_message_text(_["tops_9"])
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    total_queries = await get_queries()
    blocked = len(BANNED_USERS)
    sudoers = len(SUDOERS)
    assistant = len(assistants)
    playlist_limit = config.SERVER_PLAYLIST_LIMIT
    fetch_playlist = config.PLAYLIST_FETCH_LIMIT
    song = config.SONG_DOWNLOAD_DURATION
    play_duration = config.DURATION_LIMIT_MIN
    if config.AUTO_LEAVING_ASSISTANT == str(True):
        ass = "Yes"
    else:
        ass = "No"
    cm = config.CLEANMODE_DELETE_MINS
    text = f"""**???????? s?????????s ???????? ?????????????:**

**???????????s:** {served_chats} 
**???s?????s:** {served_users} 
**??????????????????? ???s?????s:** {blocked} 
**s??????????????s:** {sudoers} 
    
**???????????????s:** {total_queries} 
**???ss??s???????????s:** {assistant}
**???????????? ?????????????? ????????????:** {ass}
**??????????????????? ????????????????????:** {cm} ????????????????s

**????????????????????? ???????????????:** {play_duration} ????????????????s
**?????????????????????? ????????????:** {song} ????????????????s
**??????????????s??? ????????????:** {playlist_limit}
**??????????????s??? ???????????????? ????????????:** {fetch_playlist}"""
    med = InputMediaPhoto(media=config.STATS_IMG_URL, caption=text)
    await CallbackQuery.edit_message_media(
        media=med, reply_markup=upl
    )


@app.on_callback_query(filters.regex("TopUsers") & ~BANNED_USERS)
@languageCB
async def top_users_ten(client, CallbackQuery, _):
    upl = back_stats_markup(_)
    try:
        await CallbackQuery.answer()
    except:
        pass
    mystic = await CallbackQuery.edit_message_text(_["tops_4"])
    stats = await get_topp_users()
    if not stats:
        return await mystic.edit(_["tops_2"], reply_markup=upl)
    msg = ""
    limit = 0
    results = {}
    for i in stats:
        top_list = stats[i]
        results[str(i)] = top_list
        list_arranged = dict(
            sorted(
                results.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )
    if not results:
        return await mystic.edit(_["tops_2"], reply_markup=upl)
    for user, count in list_arranged.items():
        if limit > 9:
            limit += 1
            break
        try:
            user = (await app.get_users(user)).first_name
            if user is None:
                continue
        except:
            continue
        limit += 1
        msg += f"????`{user}` ???????????????? {count} ???????????s ????? ???????????.\n\n"
    if limit == 0:
        return await mystic.edit(_["tops_2"], reply_markup=upl)
    msg = _["tops_5"].format(limit, MUSIC_BOT_NAME) + msg
    med = InputMediaPhoto(media=config.GLOBAL_IMG_URL, caption=msg)
    await CallbackQuery.edit_message_media(
        media=med, reply_markup=upl
    )


@app.on_callback_query(filters.regex("TopChats") & ~BANNED_USERS)
@languageCB
async def top_ten_chats(client, CallbackQuery, _):
    upl = back_stats_markup(_)
    try:
        await CallbackQuery.answer()
    except:
        pass
    mystic = await CallbackQuery.edit_message_text(_["tops_1"])
    stats = await get_top_chats()
    if not stats:
        return await mystic.edit(_["tops_2"], reply_markup=upl)
    msg = ""
    limit = 0
    results = {}
    for i in stats:
        top_list = stats[i]
        results[str(i)] = top_list
        list_arranged = dict(
            sorted(
                results.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )
    if not results:
        return await mystic.edit(_["tops_2"], reply_markup=upl)
    for chat, count in list_arranged.items():
        if limit > 9:
            limit += 1
            break
        try:
            title = (await app.get_chat(chat)).title
            if title is None:
                continue
        except:
            continue
        limit += 1
        msg += f"????`{title}` ???????????????? {count} ???????????s ????? ???????????.\n\n"
    if limit == 0:
        return await mystic.edit(_["tops_2"], reply_markup=upl)
    if limit <= 10:
        limit = 10
    msg = _["tops_3"].format(limit, MUSIC_BOT_NAME) + msg
    med = InputMediaPhoto(media=config.GLOBAL_IMG_URL, caption=msg)
    await CallbackQuery.edit_message_media(
        media=med, reply_markup=upl
    )


@app.on_callback_query(filters.regex("TopStats") & ~BANNED_USERS)
@languageCB
async def top_fif_stats(client, CallbackQuery, _):
    upl = back_stats_markup(_)
    try:
        await CallbackQuery.answer()
    except:
        pass
    mystic = await CallbackQuery.edit_message_text(_["tops_7"])
    stats = await get_global_tops()
    tot = len(stats)
    if tot > 10:
        tracks = 10
    else:
        tracks = tot
    queries = await get_queries()
    if not stats:
        return await mystic.edit(_["tops_2"], reply_markup=upl)
    msg = ""
    limit = 0
    results = {}
    for i in stats:
        top_list = stats[i]["spot"]
        results[str(i)] = top_list
        list_arranged = dict(
            sorted(
                results.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )
    if not results:
        return await mystic.edit(_["tops_2"], reply_markup=upl)
    total_count = 0
    for vidid, count in list_arranged.items():
        total_count += count
        if limit > 9:
            continue
        limit += 1
        details = stats.get(vidid)
        title = (details["title"][:35]).title()
        if vidid == "telegram":
            msg += f"????[????????????????????? ??????????s & ??????????????s???](https://t.me/telegram) ** ???????????????? {count} ???????????s ????? ???????????**\n\n"
        else:
            msg += f"???? [{title}](https://www.youtube.com/watch?v={vidid}) ** ???????????????? {count} ???????????s ????? ???????????**\n\n"
    final = (
        _["gstats_3"].format(
            queries, config.MUSIC_BOT_NAME, tot, total_count, tracks
        )
        + msg
    )
    med = InputMediaPhoto(media=config.GLOBAL_IMG_URL, caption=final)

    await CallbackQuery.edit_message_media(
        media=med, reply_markup=upl
    )


@app.on_callback_query(filters.regex("TopHere") & ~BANNED_USERS)
@languageCB
async def top_here(client, CallbackQuery, _):
    chat_id = CallbackQuery.message.chat.id
    upl = back_stats_markup(_)
    try:
        await CallbackQuery.answer()
    except:
        pass
    mystic = await CallbackQuery.edit_message_text(_["tops_6"])
    stats = await get_particulars(chat_id)
    tot = len(stats)
    if tot > 10:
        tracks = 10
    else:
        tracks = tot
    if not stats:
        return await mystic.edit(_["tops_2"], reply_markup=upl)
    msg = ""
    limit = 0
    results = {}
    for i in stats:
        top_list = stats[i]["spot"]
        results[str(i)] = top_list
        list_arranged = dict(
            sorted(
                results.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )
    if not results:
        return await mystic.edit(_["tops_2"], reply_markup=upl)
    total_count = 0
    for vidid, count in list_arranged.items():
        total_count += count
        if limit > 9:
            continue
        limit += 1
        details = stats.get(vidid)
        title = (details["title"][:35]).title()
        if vidid == "telegram":
            msg += f"????[????????????????????? ??????????s & ??????????????s???](https://t.me/telegram) ** ???????????????? {count} ???????????s ????? ???????????**\n\n"
        else:
            msg += f"???? [{title}](https://www.youtube.com/watch?v={vidid}) ** ???????????????? {count} ???????????s ????? ???????????**\n\n"
    msg = _["tops_8"].format(tot, total_count, tracks) + msg
    med = InputMediaPhoto(media=config.GLOBAL_IMG_URL, caption=msg)
    await CallbackQuery.edit_message_media(
        media=med, reply_markup=upl
    )


@app.on_callback_query(filters.regex("bot_stats_sudo") & SUDOERS)
@languageCB
async def overall_stats(client, CallbackQuery, _):
    upl = overallback_stats_markup(_)
    try:
        await CallbackQuery.answer(
            "????????????????? s?????????s ??????????? s????????????????...!"
        )
    except:
        pass
    await CallbackQuery.edit_message_text(_["tops_9"])
    sc = platform.system()
    p_core = psutil.cpu_count(logical=False)
    t_core = psutil.cpu_count(logical=True)
    ram = (
        str(round(psutil.virtual_memory().total / (1024.0**3)))
        + " GB"
    )
    try:
        cpu_freq = psutil.cpu_freq().current
        if cpu_freq >= 1000:
            cpu_freq = f"{round(cpu_freq / 1000, 2)}GHz"
        else:
            cpu_freq = f"{round(cpu_freq, 2)}MHz"
    except:
        cpu_freq = "Unable to Fetch"
    hdd = psutil.disk_usage("/")
    total = hdd.total / (1024.0**3)
    total = str(total)
    used = hdd.used / (1024.0**3)
    used = str(used)
    free = hdd.free / (1024.0**3)
    free = str(free)
    db = pymongodb
    call = db.command("dbstats")
    datasize = call["dataSize"] / 1024
    datasize = str(datasize)
    storage = call["storageSize"] / 1024
    objects = call["objects"]
    collections = call["collections"]
    status = db.command("serverStatus")
    query = status["opcounters"]["query"]
    mongouptime = status["uptime"] / 86400
    mongouptime = str(mongouptime)
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    total_queries = await get_queries()
    blocked = len(BANNED_USERS)
    sudoers = len(await get_sudoers())
    text = f""" **???? s?????????s ???????? ????????????? ????**

               ??? ????????????????????? ???

**??????????????????????:** {sc}
**????????:** {ram}
**???????s?????????? ???????????s:** {p_core}
**?????????????? ???????????s:** {t_core}
**????????? ???????????????????????:** {cpu_freq}
   
               ??? s???????????????????? ???

**??????????????? ????????s???????:** {pyver.split()[0]}
**???????????????????? ????????s???????:** {pyrover}

                ??? s???????????????? ???

**???????????????????????:** {total[:4]} ?????????
**???s??????:** {used[:4]} ?????????
**???????????:** {free[:4]} ?????????

                ??? ???s?????s ???

**???????????s:** {served_chats} 
**???s?????s:** {served_users} 
**???????????????????:** {blocked} 
**s??????????????s:** {sudoers} 

               ??? ?????????????????s?????? ???

**?????????????????:** {mongouptime[:4]} ????????s???
**s????????:** {datasize[:6]} ????????
**s????????????????:** {storage} ????????
**??????????????????????????s:** {collections}
**????????s:** {objects}
**???????????????s:** `{query}`
**???????? ???????????????s:** `{total_queries} `
    """
    med = InputMediaPhoto(media=config.STATS_IMG_URL, caption=text)
    await CallbackQuery.edit_message_media(
        media=med, reply_markup=upl
    )
