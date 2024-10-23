import asyncio
import random
import secrets
import sys
from datetime import datetime
from time import time
from urllib.parse import unquote, quote
import aiohttp
import pytz
import traceback
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw import functions
from pyrogram.raw.functions.messages import RequestWebView
from bot.core.agents import generate_random_user_agent
from bot.config import settings
from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers
from random import randint, uniform
from bot.utils.version_updater import parser as ps


# api endpoint
api_profile = 'https://app.cexptap.com/api/v2/getUserInfo/'  # POST
api_convert = 'https://app.cexptap.com/api/v2/convert/'  # POST
api_claimBTC = 'https://app.cexptap.com/api/v2/claimCrypto/'  # POST
api_tap = 'https://app.cexptap.com/api/v2/claimMultiTaps'  # POST
api_data = 'https://app.cexptap.com/api/v2/getGameConfig'  # post
api_priceData = 'https://app.cexptap.com/api/v2/getConvertData'  # post
api_claimRef = 'https://app.cexptap.com/api/v2/claimFromChildren'  # post
api_checkref = 'https://app.cexptap.com/api/v2/getChildren'  # post
api_startTask = 'https://app.cexptap.com/api/v2/startTask'  # post
api_checkTask = 'https://app.cexptap.com/api/v2/checkTask'  # post
api_claimTask = 'https://app.cexptap.com/api/v2/claimTask'  # post
api_checkCompletedTask = 'https://app.cexptap.com/api/v2/getUserTasks' # post
api_getUserCard = 'https://app.cexptap.com/api/v2/getUserCards' #post
api_buyUpgrade = 'https://app.cexptap.com/api/v2/buyUpgrade' #post
api_getSpecialOffer = 'https://app.cexptap.com/api/v2/getUserSpecialOffer' # post
api_startSpecialOffer = 'https://app.cexptap.com/api/v2/startUserSpecialOffer' #post
api_checkSpecialOffer = 'https://app.cexptap.com/api/v2/checkUserSpecialOffer' #post
api_claimSpecialOffer = 'https://app.cexptap.com/api/v2/claimUserSpecialOffer' #post

class Tapper:
    def __init__(self, tg_client: Client, app_version):
        self.tg_client = tg_client
        self.session_name = tg_client.name
        self.version = app_version
        self.first_name = ''
        self.last_name = ''
        self.user_id = ''
        self.Total_Point_Earned = 0
        self.Total_Game_Played = 0
        self.btc_balance = 0
        self.coin_balance = 0
        self.task = None
        self.card = None
        self.startedTask = []
        self.skip = ['register_on_cex_io', 'boost_telegram', 'play_piggypiggy_tap_game', 'join_btc_garden_twitter', 'subscribe_crypto_garden_telegram', 'subscribe_telegram', 'join_cedex_tap_game', 'join_wigwam_drum_game', 'WatchPowerTapGuidevideo', 'joinПро100Крипта', 'joinCryptoCab', 'joinEarningSikka']
        self.card1 = None
        self.potential_card = {}
        self.multi = 1000000
        self.energy = 1000
        self.cexp_balance = 0
        self.multi_tap = 1
        self.energy_limit = 1000
        self.special_task = []
        self.hash = None
        self.my_ref = "1729165832653351"
        self.ready_to_check_special_task = []


    async def get_tg_web_data(self, proxy: str | None) -> str:
        logger.info(f"Getting data for {self.session_name}")
        if settings.REF_LINK != "":
            ref_param = settings.REF_LINK.split('=')[1]
        else:
            ref_param = "1729165832653351"
        ref_param = random.choices([self.my_ref, ref_param], weights=[30, 70])
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()
                    start_command_found = False
                    async for message in self.tg_client.get_chat_history('cexio_tap_bot'):
                        if (message.text and message.text.startswith('/start')) or (
                                message.caption and message.caption.startswith('/start')):
                            start_command_found = True
                            break
                    if not start_command_found:
                        peer = await self.tg_client.resolve_peer('cexio_tap_bot')
                        await self.tg_client.invoke(
                            functions.messages.StartBot(
                                bot=peer,
                                peer=peer,
                                start_param=ref_param[0],
                                random_id=randint(1, 9999999),
                            )
                        )

                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            while True:
                try:
                    peer = await self.tg_client.resolve_peer('cexio_tap_bot')
                    break
                except FloodWait as fl:
                    fls = fl.value

                    logger.warning(f"<light-yellow>{self.session_name}</light-yellow> | FloodWait {fl}")
                    logger.info(f"<light-yellow>{self.session_name}</light-yellow> | Sleep {fls}s")

                    await asyncio.sleep(fls + 3)

            web_view = await self.tg_client.invoke(RequestWebView(
                peer=peer,
                bot=peer,
                platform='android',
                from_bot_menu=False,
                url="https://app.cexptap.com",
                start_param=ref_param[0]
            ))
            auth_url = web_view.url
            # print(unquote(auth_url))
            tg_web_data = unquote(
                string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
           # print(tg_web_data)
            self.user_id = tg_web_data.split('"id":')[1].split(',"first_name"')[0]
            self.first_name = tg_web_data.split('"first_name":"')[1].split('","last_name"')[0]
            self.last_name = tg_web_data.split('"last_name":"')[1].split('","username"')[0]
            self.hash = tg_web_data.split('&hash=')[1]
            # print(self.hash)
            # await asyncio.sleep(10000)
            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

            return unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Unknown error during Authorization: "
                         f"{error}")
            await asyncio.sleep(delay=3)

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

    async def get_user_info(self, http_client: aiohttp.ClientSession, authToken):
        data = {
            "devAuthData": int(self.user_id),
            "authData": str(authToken),
            "platform": "android",
            "data": {}
        }
        # print(http_client.headers)
        response = await http_client.post(api_profile, json=data)
        if response.status == 200:
            try:
                json_response = await response.json()
                data_response = json_response['data']
                self.coin_balance = int(float(data_response['balance_USD']))
                self.multi_tap = int(data_response['multiTapsPower'])
                self.energy = data_response['multiTapsEnergy']
                self.energy_limit = data_response['multiTapsEnergyLimit']
                # print(json_response)
                try:
                    self.multi = 10**data_response['precision_BTC']
                except:
                    self.multi = 10
                try:
                    cexp = data_response['balance_CEXP']
                    self.cexp_balance = int(cexp)
                except:
                    cexp = 0
                self.btc_balance = int(float(data_response['balance_BTC'])) / self.multi
                logger.info(
                    f"Account name: {data_response['first_name']} - Balance: <yellow>{data_response['balance_USD']}</yellow> - Btc balance: <yellow>{self.btc_balance}</yellow> - Power: <yellow>{cexp}</yellow> CEXP")
            except Exception as e:
                logger.error(f"Error while getting user data: {e} .Try again after 30s")
                await asyncio.sleep(30)
                return
        else:
            logger.error(f"Error while getting user data. Response {response.status}. Try again after 30s")
            await asyncio.sleep(30)


    async def get_user_special_task(self, http_client: aiohttp.ClientSession, authToken):
        data = {
            "devAuthData": int(self.user_id),
            "authData": authToken,
            "platform": "android",
            "data": {}
        }

        response = await http_client.post(api_getSpecialOffer, json=data)
        if response.status == 200:
            json_response = await response.json()
            for task in json_response['data']:
                if task['type'] != "social" and task['type'] != "learn_earn":
                    continue
                elif task['state'] == "NONE":
                    self.special_task.append(task)
                elif task['state'] == "ReadyToCheck":
                    logger.info(f"{self.session_name} | Task: {task['taskId']} ready for check...")
                    self.ready_to_check_special_task.append(task)
        else:
            logger.warning(f"{self.session_name} | Failed to get special tasks data. Response code: {response.status}")

    async def start_special_task(self, http_client: aiohttp.ClientSession, authToken, offerId, taskName):
        data = {
            "devAuthData": int(self.user_id),
            "authData": authToken,
            "platform": "android",
            "data": {
                "specialOfferId": str(offerId)
            }
        }

        response = await http_client.post(api_startSpecialOffer, json=data)
        if response.status == 200:
            logger.info(f"{self.session_name} | <green> Successfully started special offer: {taskName}.</green>")
            return True
        else:
            logger.warning(f"{self.session_name} | Failed to start special offer data. Response code: {response.status}")
            return False
    async def claim_special_task(self, http_client: aiohttp.ClientSession, authToken, offerId, taskName):
        data = {
            "devAuthData": int(self.user_id),
            "authData": authToken,
            "platform": "android",
            "data": {
                "specialOfferId": str(offerId)
            }
        }
        response = await http_client.post(api_claimSpecialOffer, json=data)
        if response.status == 200:
            logger.success(f"{self.session_name} | <green>Successfully claimed special offer: <cyan>{taskName}</cyan></green>")
        else:
            logger.warning(
                f"{self.session_name} | Failed to claim special offer. Response code: {response.status}")
            return False

    async def check_special_task(self, http_client: aiohttp.ClientSession, authToken, offerId, taskName):
        data = {
            "devAuthData": int(self.user_id),
            "authData": authToken,
            "platform": "android",
            "data": {
                "specialOfferId": str(offerId)
            }
        }

        response = await http_client.post(api_checkSpecialOffer, json=data)
        if response.status == 200:
            check = False
            json_response = await response.json()
            for task in json_response['data']:
                if task['specialOfferId'] == str(offerId):
                    if task['state'] == "ReadyToClaim":
                        check = await self.claim_special_task(http_client, authToken, offerId, taskName)
                        break
                    else:
                        logger.info(f"{self.session_name} | Task: {task['taskId']} wait for check...")
                        break
            if check:
                return True
            else:
                return False
        else:
            logger.warning(f"{self.session_name} | Failed to check special offer. Response code: {response.status}")
            return False
    async def tap(self, http_client: aiohttp.ClientSession, authToken, taps):
        time_unix = int((time()) * 1000)
        data = {
            "devAuthData": int(self.user_id),
            "authData": str(authToken),
            "platform": "android",
            "data": {
                "tapsEnergy": str(int(self.energy)-int(taps)),
                "tapsToClaim": str(taps),
                "tapsTs": time_unix
            }
        }
        # print(data)
        # print(int((time()) * 1000) - time_unix)
        response = await http_client.post(api_tap, json=data)
        if response.status == 200:
            self.energy -= int(taps)*self.multi_tap
            json_response = await response.json()
            data_response = json_response['data']
            self.coin_balance = int(float(data_response['balance_USD']))
            if int(taps) != 0:
                logger.info(f"{self.session_name} | Tapped <cyan>{taps}</cyan> times | Coin balance: <cyan>{data_response['balance_USD']}</cyan>")
        else:
            json_response = await response.json()
            if "too slow" in json_response['data']['reason']:
                logger.error(f'{self.session_name} | <red> Tap failed - please stop the code and open the bot in telegram then tap 1-2 times and run this code again. it should be worked!</red>')
            elif "fast taps" in json_response['data']['reason']:
                pass
            else:
                print(json_response)
                logger.error(f'{self.session_name} | <red> Tap failed - response code: {response.status}</red>')

    async def claim_crypto(self, http_client: aiohttp.ClientSession, authToken):
        data = {
            "devAuthData": int(self.user_id),
            "authData": str(authToken),
            "platform": "ios",
            "data": {}
        }
        response = await http_client.post(api_claimBTC, json=data)
        if response.status == 200:
            json_response = await response.json()
            data_response = json_response['data']["BTC"]
            try:
                self.multi = 10 ** int(data_response['precision_BTC'])
                self.btc_balance = int(data_response['balance_BTC']) / self.multi
            except:
                return None
            logger.info(
                f"{self.session_name} | Claimed <cyan>{int(data_response['claimedAmount']) / self.multi}</cyan> BTC | BTC Balance: <cyan>{int(data_response['balance_BTC']) / self.multi}</cyan>")
        else:
            logger.error(f"{self.session_name} | <red>Claim BTC failed - response code: {response.status}</red>")

    async def getConvertData(self, http_client: aiohttp.ClientSession, authToken):
        data = {
            "devAuthData": int(self.user_id),
            "authData": str(authToken),
            "platform": "ios",
            "data": {}
        }
        response = await http_client.post(api_priceData, json=data)
        if response.status == 200:
            json_response = await response.json()
            data_response = json_response['convertData']['lastPrices']
            return data_response[-1]
        else:
            logger.error(f"{self.session_name} | <red> Can convert !| Error code: {response.status}")
            return None

    async def convertBTC(self, http_client: aiohttp.ClientSession, authToken):
        price = await self.getConvertData(http_client, authToken)
        if price:
            data = {
                "devAuthData": int(self.user_id),
                "authData": str(authToken),
                "platform": "android",
                "data": {
                    "fromCcy": "BTC",
                    "toCcy": "USD",
                    "price": str(price),
                    "fromAmount": str(self.btc_balance)
                }
            }
            response = await http_client.post(api_convert, json=data)
            if response.status == 200:
                json_response = await response.json()
                data_response = json_response['convert']
                self.coin_balance = int(float(data_response['balance_USD']))
                logger.success(
                    f"{self.session_name} | <green> Successfully convert <yellow>{self.btc_balance}</yellow> to <yellow>{float(self.btc_balance)*float(price)}</yellow> coin - Coin balance: <yellow>{data_response['balance_USD']}</yellow></green>")
            else:
                logger.error(f"{self.session_name} | <red>Error code {response.status} While trying to convert...</red>")

    async def checkref(self, http_client: aiohttp.ClientSession, authToken):
        data = {
            "devAuthData": int(self.user_id),
            "authData": str(authToken),
            "platform": "android",
            "data": {}
        }
        response = await http_client.post(api_checkref, json=data)
        if response.status == 200:
            json_response = await response.json()
            return json_response['data']['totalRewardsToClaim']
        else:
            return 0

    async def claim_pool(self, http_client: aiohttp.ClientSession, authToken):
        data = {
            "devAuthData": int(self.user_id),
            "authData": str(authToken),
            "platform": "android",
            "data": {}
        }
        response = await http_client.post(api_claimRef, json=data)
        if response.status == 200:
            json_response = await response.json()
            logger.success(
                f"{self.session_name} | Successfully Claimed <yellow>{int(json_response['data']['claimed_BTC']) / self.multi}</yellow> | BTC balance: <yellow>{json_response['data']['balance_BTC']}</yellow>")
        else:
            logger.error(f"{self.session_name} | <red>Error code {response.status} While trying to claim from pool</red>")

    async def fetch_data(self, http_client: aiohttp.ClientSession, authToken):
        data = {
            "devAuthData": int(self.user_id),
            "authData": str(authToken),
            "platform": "android",
            "data": {}
        }
        response = await http_client.post(api_data, json=data)
        if response.status == 200:
            json_response = await response.json(content_type=None)
            # print(json_response)
            try:
                self.task = json_response['tasksConfig']
            except:
                self.task = []
            
            self.card = json_response['upgradeCardsConfig']
        else:
            logger.error(f"{self.session_name} | <red>Error code {response.status} While trying to get data</red>")

    async def getUserTask(self, http_client: aiohttp.ClientSession, authToken):
        data = {
            "devAuthData": int(self.user_id),
            "authData": str(authToken),
            "platform": "android",
            "data": {}
        }
        response = await http_client.post(api_checkCompletedTask, json=data)
        if response.status == 200:
            json_response = await response.json()
            # print(json_response)
            completed_task = []
            for task in json_response['tasks']:
                if json_response['tasks'][task]['state'] == "Claimed":
                    completed_task.append(task)
                elif json_response['tasks'][task]['state'] == "ReadyToCheck":
                    self.startedTask.append(task)
            return completed_task
        else:
            logger.error(f"{self.session_name} | <red>Error code {response.status} While trying to get completed task</red>")
            return None

    async def claimTask(self, http_client: aiohttp.ClientSession, authToken, taskId):
        data = {
            "devAuthData": int(self.user_id),
            "authData": str(authToken),
            "platform": "android",
            "data": {
                "taskId": taskId
            }
        }
        response = await http_client.post(api_claimTask, json=data)
        if response.status == 200:
            json_response = await response.json()
            logger.success(f"{self.session_name} | <green>Successfully claimed <yellow>{json_response['data']['claimedBalance']}</yellow> from {taskId}</green>")
        else:
            logger.error(f"{self.session_name} | <red>Failed to claim {taskId}. Response: {response.status}</red>")

    async def checkTask(self, http_client: aiohttp.ClientSession, authToken, taskId):
        data = {
            "devAuthData": int(self.user_id),
            "authData": str(authToken),
            "platform": "android",
            "data": {
                "taskId": taskId
            }
        }
        response = await http_client.post(api_checkTask, json=data)
        if response.status == 200:
            json_response = await response.json()
            if json_response['data']['state'] == "ReadyToClaim":
                await self.claimTask(http_client, authToken, taskId)
            else:
                logger.info(f"{self.session_name} | {taskId} wait for check")
        else:
            logger.error(f"{self.session_name} | <red>Failed to check task {taskId}. Response: {response.status}</red>")

    async def startTask(self, http_client: aiohttp.ClientSession, authToken, taskId):
        data = {
            "devAuthData": int(self.user_id),
            "authData": str(authToken),
            "platform": "android",
            "data": {
                "taskId": taskId
            }
        }
        response = await http_client.post(api_startTask, json=data)
        if response.status == 200:
            logger.info(f"{self.session_name} | Successfully started task {taskId}")
        else:
            if response.status == 500:
                self.skip.append(taskId)
            logger.error(f"{self.session_name} | <red>Failed to start task {taskId}. Response: {response.status}</red>")

    async def getUserCard(self, http_client: aiohttp.ClientSession, authToken):
        data = {
            "devAuthData": int(self.user_id),
            "authData": str(authToken),
            "platform": "android",
            "data": {}
        }
        response = await http_client.post(api_getUserCard, json=data)
        if response.status == 200:
            json_response = await response.json()
            return json_response['cards']
        else:
           return None

    async def find_potential(self):
        for category in self.card:
            for card in category['upgrades']:
                # print(card)
                if card['upgradeId'] in self.card1:
                    card_lvl = self.card1[card['upgradeId']]['lvl']
                    if len(card['levels']) <= card_lvl:
                        continue
                    if len(card['levels']) > 0:
                        potential = card['levels'][card_lvl][0]/card['levels'][card_lvl][2]
                        self.potential_card.update({
                            potential: {
                                "upgradeId": card['upgradeId'],
                                "cost": card['levels'][card_lvl][0],
                                "effect": card['levels'][card_lvl][2],
                                "categoryId": category['categoryId'],
                                "nextLevel": card_lvl + 1,
                                "effectCcy": "CEXP",
                                "ccy": "USD",
                                "dependency": card['dependency']
                            }
                        })
                else:
                    if len(card['levels']) > 0:
                        if card['levels'][0][2] != 0:
                            potential = card['levels'][0][0]/card['levels'][0][2]
                            self.potential_card.update({
                                potential: {
                                    "upgradeId":  card['upgradeId'],
                                    "cost": card['levels'][0][0],
                                    "effect": card['levels'][0][2],
                                    "categoryId": category['categoryId'],
                                    "nextLevel": 1,
                                    "effectCcy": "CEXP",
                                    "ccy": "USD",
                                    "dependency": card['dependency']
                                }
                            })

    def checkDependcy(self, dependency):
        if len(dependency) == 0:
            return True
        if dependency['upgradeId'] not in self.card1:
            return False
        if self.card1[dependency['upgradeId']]['lvl'] >= dependency['level']:
            return True
        return False

    async def buyUpgrade(self, http_client: aiohttp.ClientSession, authToken, Buydata):
        data = {
            "devAuthData": int(self.user_id),
            "authData": str(authToken),
            "platform": "android",
            "data": {
                "categoryId": Buydata['categoryId'],
                "ccy": Buydata['ccy'],
                "cost": Buydata['cost'],
                "effect": Buydata['effect'],
                "effectCcy": Buydata['effectCcy'],
                "nextLevel": Buydata['nextLevel'],
                "upgradeId": Buydata['upgradeId']
            }
        }
        response = await http_client.post(api_buyUpgrade, json=data)
        if response.status == 200:
            self.coin_balance -= int(Buydata['cost'])
            logger.success(f"{self.session_name} | <green>Successfully upgraded <blue>{Buydata['upgradeId']}</blue> to level <blue>{Buydata['nextLevel']}</blue></green>")
            return True
        else:
            logger.error(f"{self.session_name} | <red>Error while upgrade card {Buydata['upgradeId']} to lvl {Buydata['nextLevel']}. Response code: {response.status}</red>")
            return False


    async def run(self, proxy: str | None) -> None:
        access_token_created_time = 0
        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        headers["user-agent"] = generate_random_user_agent(device_type='android', browser_type='chrome')
        http_client = CloudflareScraper(headers=headers, connector=proxy_conn)

        if proxy:
            await self.check_proxy(http_client=http_client, proxy=proxy)
        authToken = ""
        token_live_time = randint(3500, 3600)
        while True:
            try:
                if time() - access_token_created_time >= token_live_time or authToken == "":
                    logger.info(f"{self.session_name} | Update auth token...")
                    tg_web_data = await self.get_tg_web_data(proxy=proxy)
                    with open("x-appl-version.txt", "r") as f:
                        version = f.read()

                    http_client.headers.update({'x-appl-version': str(version)})
                    # print(http_client.headers)
                    # print(self.user_id)
                    authToken = tg_web_data
                    access_token_created_time = time()
                    token_live_time = randint(3500, 3600)
                    await asyncio.sleep(delay=randint(10, 15))

                if ps.check_base_url() is False:
                    if settings.ADVANCED_ANTI_DETECTION:
                        sys.exit(
                            "Detected index js file change. Contact me to check if it's safe to continue: https://t.me/vanhbakaaa")
                    else:
                        sys.exit(
                            "Detected api change! Stoped the bot for safety. Contact me here to update the bot: https://t.me/vanhbakaaa")

                logger.info(f"Session {self.first_name} {self.last_name} logged in.")
                # print(authToken)
                user_hash = self.hash
                http_client.headers.update({"x-request-userhash": user_hash})
                await self.get_user_info(http_client, authToken)
                if self.card is None or self.task is None:
                    await self.fetch_data(http_client, authToken)
                    # print(self.task)
                if settings.AUTO_TASK:
                    await self.get_user_special_task(http_client, authToken)
                    if len(self.special_task) > 0:
                        for task in self.special_task:
                            check = await self.start_special_task(http_client,authToken,task['specialOfferId'],task['taskId'])
                            if check:
                                self.special_task.remove(task)
                        await asyncio.sleep(uniform(2, 3))
                    elif len(self.ready_to_check_special_task) > 0:
                        for task in self.ready_to_check_special_task:
                            check = await self.check_special_task(http_client, authToken,task['specialOfferId'], task['taskId'])
                            if check:
                                self.ready_to_check_special_task.remove(task)
                            await asyncio.sleep(uniform(2,3))
                    else:
                        logger.info(f"{self.session_name} | No special tasks now!")
                    completed_tasks = await self.getUserTask(http_client, authToken)
                    for task in self.task:
                        #print(task)
                        if task['taskId'] in self.skip:
                            continue
                        elif task['taskId'] in completed_tasks:
                            continue
                        elif task['type'] != "social" and task['type'] != "learn_earn":
                            continue
                        elif task['taskId'] in self.startedTask:
                            await self.checkTask(http_client, authToken, task['taskId'])
                            await asyncio.sleep(uniform(1, 2))
                        else:
                            await self.startTask(http_client, authToken, task['taskId'])
                            await asyncio.sleep(uniform(1,2))

                if settings.AUTO_CONVERT and self.btc_balance >= settings.MINIMUM_TO_CONVERT:
                    await self.convertBTC(http_client, authToken)

                if settings.AUTO_BUY_UPGRADE:
                    self.card1 = await self.getUserCard(http_client, authToken)
                    await self.find_potential()
                    sorted_potential_card = dict(sorted(self.potential_card.items()))
                        # print(sorted_potential_card)

                    for card in sorted_potential_card:
                        if self.checkDependcy(sorted_potential_card[card]['dependency']):
                            if int(sorted_potential_card[card]['cost']) <= int(round(float(self.coin_balance))):
                                logger.info(f"{self.session_name} | Attempt to upgrade {card}")
                                check = await self.buyUpgrade(http_client, authToken, sorted_potential_card[card])
                                if check:
                                    self.potential_card.pop(card)
                                await asyncio.sleep(uniform(3,5))
                            elif settings.WAIT_FOR_MOST_PROFITABLE_CARD:
                                break

                runtime = 10
                if settings.AUTO_TAP:
                    await asyncio.sleep(uniform(3, 5))
                    await self.tap(http_client, authToken, 0)
                    while runtime > 0:
                        taps = str(randint(settings.RANDOM_TAPS_COUNT[0], settings.RANDOM_TAPS_COUNT[1]))
                        if int(taps) >= 1000:
                            logger.warning(f"{self.session_name} | Invaild taps count...")
                        elif self.energy > settings.SLEEP_BY_MIN_ENERGY:
                            await self.tap(http_client, authToken, taps)
                        else:
                            logger.info(f"Minimum energy reached: {self.energy}")
                        runtime -= 1
                        sleep_ = randint(settings.SLEEP_BETWEEN_TAPS[0], settings.SLEEP_BETWEEN_TAPS[1])
                        self.energy += sleep_*3
                        if self.energy > self.energy_limit:
                            self.energy = self.energy_limit
                        await asyncio.sleep(sleep_)
                    await self.claim_crypto(http_client, authToken)
                    logger.info(f"{self.session_name} | resting and upgrade...")
                else:
                    if self.cexp_balance > 0:
                        await self.claim_crypto(http_client, authToken)
                        while runtime > 0:
                            runtime -= 1
                            await asyncio.sleep(uniform(15, 25))
                        logger.info(f"{self.session_name} | resting and upgrade...")

                if settings.AUTO_CLAIM_SQUAD_BONUS:
                    pool_balance = await self.checkref(http_client, authToken)
                    if float(pool_balance) > 0:
                        await self.claim_pool(http_client, authToken)

                delay_time = randint(60, 120)
                logger.info(f"{self.session_name} | waiting {delay_time} seconds...")
                await asyncio.sleep(delay=delay_time)
            except InvalidSession as error:
                raise error

            except Exception as error:
                traceback.print_exc()
                logger.error(f"{self.session_name} | Unknown error: {error}")
                await asyncio.sleep(delay=randint(60, 120))


async def run_tapper(tg_client: Client, proxy: str | None, app_version):
    try:
        sleep_ = randint(1, 15)
        logger.info(f"{tg_client.name} | Start after {sleep_}s...")
        await asyncio.sleep(sleep_)
        await Tapper(tg_client=tg_client, app_version=app_version).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
