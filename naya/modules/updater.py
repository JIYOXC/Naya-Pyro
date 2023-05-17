# Copas Teriak Copas MONYET
# Gay Teriak Gay Anjeng
# @Rizzvbss | @Kenapanan
# Kok Bacot
# © @KynanSupport
# FULL MONGO NIH JING FIX MULTI CLIENT


import asyncio
import os
import socket
import sys
from datetime import datetime
from os import environ, execle, path, remove

import aiohttp
import urllib3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from pyrogram import *
from pyrogram import filters
from pyrogram.types import *
from pyrogram.types import Message

from naya.config import *

from . import *

HAPP = None

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


XCB = [
    "/",
    "@",
    ".",
    "com",
    ":",
    "git",
    "heroku",
    "push",
    str(HEROKU_API_KEY),
    "https",
    str(HEROKU_APP_NAME),
    "HEAD",
    "main",
]

BASE = "https://batbin.me/"


def get_arg(message: Message):
    msg = message.text
    msg = msg.replace(" ", "", 1) if msg[1] == " " else msg
    split = msg[1:].replace("\n", " \n").split(" ")
    if " ".join(split[1:]).strip() == "":
        return ""
    return " ".join(split[1:])


async def post(url: str, *args, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, *args, **kwargs) as resp:
            try:
                data = await resp.json()
            except Exception:
                data = await resp.text()
        return data


async def PasteBin(text):
    resp = await post(f"{BASE}api/v2/paste", data=text)
    if not resp["success"]:
        return
    link = BASE + resp["message"]
    return link


if GIT_TOKEN:
    GIT_USERNAME = REPO_URL.split("com/")[1].split("/")[0]
    TEMP_REPO = REPO_URL.split("https://")[1]
    UPSTREAM_REPO = f"https://{GIT_USERNAME}:{GIT_TOKEN}@{TEMP_REPO}"
    UPSTREAM_REPO_URL = UPSTREAM_REPO
else:
    UPSTREAM_REPO_URL = REPO_URL

requirements_path = path.join(
    path.dirname(path.dirname(path.dirname(__file__))), "requirements.txt"
)


def restart():
    os.execvp(sys.executable, [sys.executable, "-m", "naya"])


async def is_heroku():
    return "heroku" in socket.getfqdn()


async def bash(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    err = stderr.decode().strip()
    out = stdout.decode().strip()
    return out, err


async def gen_chlog(repo, diff):
    ch_log = ""
    d_form = "%d/%m/%y"
    for c in repo.iter_commits(diff):
        ch_log += (
            f"• [{c.committed_datetime.strftime(d_form)}]: {c.summary} <{c.author}>\n"
        )
    return ch_log


async def updateme_requirements():
    reqs = str(requirements_path)
    try:
        process = await asyncio.create_subprocess_shell(
            " ".join([sys.executable, "-m", "pip", "install", "-r", reqs]),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
        return process.returncode
    except Exception as e:
        return repr(e)


@bots.on_message(filters.command(["update", "cekupdate"], cmd) & filters.me)
async def _(client, message):
    status = await message.edit("`Sebentar sedang memeriksa pembaruan...`")
    conf = get_arg(message)
    off_repo = UPSTREAM_REPO_URL
    txt = None
    repo = None
    try:
        txt = (
            "**Update Could Not Continue Due "
            + "Several ERROR Occurred**\n\n**LOGTRACE:**\n"
        )
        repo = Repo()
    except NoSuchPathError as error:
        await status.edit(f"{txt}\n**Directory** `{error}` **Can not be found.**")
        repo.__del__()
        return
    except GitCommandError as error:
        await status.edit(f"{txt}\n**Early failure!** `{error}`")
        repo.__del__()
        return
    except InvalidGitRepositoryError:
        if conf != "gas":
            pass
        repo = Repo.init()
        origin = repo.create_remote("upstream", off_repo)
        origin.fetch()
        repo.create_head(
            BRANCH,
            origin.refs[BRANCH],
        )
        repo.heads[BRANCH].set_tracking_branch(origin.refs[BRANCH])
        repo.heads[BRANCH].checkout(True)
    ac_br = repo.active_branch.name
    if ac_br != BRANCH:
        await status.edit(
            f"**[UPDATER]:** `Looks like you are using your own custom branch ({ac_br}). in that case, Updater is unable to identify which branch is to be merged. please checkout to main branch`"
        )
        repo.__del__()
        return
    try:
        repo.create_remote("upstream", off_repo)
    except BaseException as a:
        print(a)
    ups_rem = repo.remote("upstream")
    ups_rem.fetch(ac_br)
    changelog = await gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    if "gas" not in conf:
        if changelog:
            changelog_str = f"**Terdapat pembaruan untuk [{ac_br}]:\n\nCHANGELOG:**\n\n`{changelog}`"
            if len(changelog_str) > 4096:
                await status.edit("**Changelog terlalu besar.**")
                file = open("output.txt", "w+")
                file.write(changelog_str)
                file.close()
                await client.send_document(
                    message.chat.id,
                    "output.txt",
                    caption=f"**Ketik** `{cmd}update gas` **Untuk melakukan pembaruan.**",
                    reply_to_message_id=status.id,
                )
                remove("output.txt")
            else:
                return await status.edit(
                    f"{changelog_str}\n**Ketik** `{cmd}update gas` **Untuk melakukan pembaruan.**",
                    disable_web_page_preview=True,
                )
        else:
            await status.edit(
                f"\n`Your BOT is`  **up-to-date**  `with branch`  **[{ac_br}]**\n",
                disable_web_page_preview=True,
            )
            repo.__del__()
            return
    if HEROKU_API_KEY is not None:
        import heroku3

        heroku = heroku3.from_key(HEROKU_API_KEY)
        heroku_app = None
        heroku_applications = heroku.apps()
        if not HEROKU_APP_NAME:
            await status.edit(
                "`Please set up the HEROKU_APP_NAME variable to be able to update userbot.`"
            )
            repo.__del__()
            return
        for app in heroku_applications:
            if app.name == HEROKU_APP_NAME:
                heroku_app = app
                break
        if heroku_app is None:
            await status.edit(
                f"{txt}\n`Invalid Heroku credentials for updating userbot dyno.`"
            )
            repo.__del__()
            return
        await status.edit(
            "`[HEROKU]: Naya-Pyro Premium Deploy Update is in Progress...`"
        )
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        heroku_git_url = heroku_app.git_url.replace(
            "https://", "https://api:" + HEROKU_API_KEY + "@"
        )
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(heroku_git_url)
        else:
            remote = repo.create_remote("heroku", heroku_git_url)
        try:
            remote.push(refspec="HEAD:refs/heads/main", force=True)
        except GitCommandError:
            pass
        await status.edit(
            "`Naya-Pyro Premium Successfully Updated! Userbot can be used again.`"
        )
    else:
        try:
            ups_rem.pull(ac_br)
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
        await updateme_requirements()
        await status.edit(
            "`Naya-Pyro Premium Successfully Updated! Userbot can be used again.`",
        )
        args = [sys.executable, "-m", "naya"]
        execle(sys.executable, *args, environ)
        return


@bots.on_message(filters.command("cekupdate", cmd) & filters.me)
async def _(client, message):
    response = await message.edit("`Memeriksa pembaruan...")
    try:
        repo = Repo()
    except GitCommandError:
        return await response.edit("Git Command Error")
    except InvalidGitRepositoryError:
        return await response.edit("Invalid Git Repsitory")
    to_exc = f"git fetch origin {BRANCH} &> /dev/null"
    await bash(to_exc)
    await asyncio.sleep(7)
    verification = ""
    REPO_ = repo.remotes.origin.url.split(".git")[0]  # main git repository
    for checks in repo.iter_commits(f"HEAD..origin/{BRANCH}"):
        verification = str(checks.count())
    if verification == "":
        return await response.edit("Bot is up-to-date!")
    updates = ""
    ordinal = lambda format: "%d%s" % (
        format,
        "tsnrhtdd"[(format // 10 % 10 != 1) * (format % 10 < 4) * format % 10 :: 4],
    )
    for info in repo.iter_commits(f"HEAD..origin/{BRANCH}"):
        updates += f"<b>➣ #{info.count()}: [{info.summary}]({REPO_}/commit/{info}) by -> {info.author}</b>\n\t\t\t\t<b>➥ Commited on:</b> {ordinal(int(datetime.fromtimestamp(info.committed_date).strftime('%d')))} {datetime.fromtimestamp(info.committed_date).strftime('%b')}, {datetime.fromtimestamp(info.committed_date).strftime('%Y')}\n\n"
    _update_response_ = "<b>A new update is available for the Bot!</b>\n\n➣ Pushing Updates Now</code>\n\n**<u>Updates:</u>**\n\n"
    _final_updates_ = _update_response_ + updates
    if len(_final_updates_) > 4096:
        url = await PasteBin(updates)
        nrs = await response.edit(
            f"<b>A new update is available for the Bot!</b>\n\n➣ Pushing Updates Now</code>\n\n**<u>Updates:</u>**\n\n[Click Here to checkout Updates]({url})"
        )
    else:
        nrs = await response.edit(_final_updates_, disable_web_page_preview=True)
    await bash("git stash &> /dev/null && git pull")
    if await is_heroku():
        try:
            await response.edit(
                f"{nrs.text}\n\nBot was updated successfully on! Now, wait for 2 - 3 mins until the bot restarts!"
            )
            await bash(
                f"{XCB[5]} {XCB[7]} {XCB[9]}{XCB[4]}{XCB[0]*2}{XCB[6]}{XCB[4]}{XCB[8]}{XCB[1]}{XCB[5]}{XCB[2]}{XCB[6]}{XCB[2]}{XCB[3]}{XCB[0]}{XCB[10]}{XCB[2]}{XCB[5]} {XCB[11]}{XCB[4]}{XCB[12]}"
            )
            return
        except Exception as err:
            return await response.edit(f"{nrs.text}\n\nERROR: <code>{err}</code>")
    else:
        await bash("pip3 install -U -r requirements.txt")
        restart()
        exit()


__MODULE__ = "updater"
__HELP__ = f"""
✘ Bantuan Untuk Updater

Perintah: <code>{cmd}cekupdate</code>
Penjelasan: Untuk mengetahui apa yang baru.

Perintah: <code>{cmd}update gas</code>
Penjelasan: Untuk melakukan update Naya-Pyro.
"""
