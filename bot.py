from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class HahaWallet:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "chrome-extension://andhndehpcjpmneneealacgnmealilal",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Storage-Access": "active",
            "User-Agent": FakeUserAgent().random,
            "X-Request-Source-Extra": "chrome"
        }
        self.BASE_API = "https://prod.haha.me"
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Claim Karma {Fore.BLUE + Style.BRIGHT}Haha Wallet - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        try:
            if not os.path.exists('accounts.json'):
                self.log(f"{Fore.RED}File 'accounts.json' tidak ditemukan.{Style.RESET_ALL}")
                return

            with open('accounts.json', 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
        
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"
        
    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Monosans Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return choose, rotate
    
    async def users_login(self, email: str, password: str, proxy=None):
        url = f"{self.BASE_API}/users/login"
        data = json.dumps({"email":email, "password":password})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Content-Type": "application/json"
        }
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                async with session.post(url=url, headers=headers, data=data) as response:
                    response.raise_for_status()
                    return await response.json()
        except (Exception, ClientResponseError) as e:
            return None
                
    async def user_balance(self, token: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/wallet-api/graphql"
        data = json.dumps({
            "operationName": None,
            "variables": {},
            "query": "{\n  getKarmaPoints\n}"
        })
        headers = {
            **self.headers,
            "Authorization": token,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.log(str(e))
                
    async def daily_checkin(self, token: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/wallet-api/graphql"
        data = json.dumps({
            "operationName": None,
            "variables":{
                "timezone":"Asia/Jakarta"
            },
            "query": "query ($timezone: String) {\n  getDailyCheckIn(timezone: $timezone)\n}"
        })
        headers = {
            **self.headers,
            "Authorization": token,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
                
    async def claim_checkin(self, token: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/wallet-api/graphql"
        data = json.dumps({
            "operationName": None,
            "variables":{
                "timezone": "Asia/Jakarta"
            },
            "query": "mutation ($timezone: String) {\n  setDailyCheckIn(timezone: $timezone)\n}"
        })
        headers = {
            **self.headers,
            "Authorization": token,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def basic_task_lists(self, token: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/wallet-api/graphql"
        data = json.dumps({
            "operationName": None,
            "variables": {},
            "query": "{\n  getOnboarding {\n    show\n    expired\n    user_id\n    completed_all\n    completed_at\n    karma_available\n    karma_paid\n    karma_multiplier\n    max_transaction_perday\n    total_streaks_karma\n    redeemed_karma\n    tasks {\n      task_id\n      type\n      name\n      description\n      content\n      link\n      deeplink\n      completed\n      completed_at\n      karma_available\n      karma_paid\n      today_transactions\n      hide_after_completion\n      __typename\n    }\n    __typename\n  }\n}"
        })
        headers = {
            **self.headers,
            "Authorization": token,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
                
    async def claim_basic_tasks(self, token: str, task_id: int, proxy=None, retries=5):
        url = f"{self.BASE_API}/wallet-api/graphql"
        data = json.dumps({
            "operationName": None,
            "variables": {
                "task_id": task_id
            },
            "query": "mutation ($task_id: Int) {\n  setOnboarding(task_id: $task_id) {\n    task_id\n    success\n    completed_all\n    current_karma\n    __typename\n  }\n}"
        })
        
        headers = {
            **self.headers,
            "Authorization": token,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def social_task_lists(self, token: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/wallet-api/graphql"
        data = json.dumps({
            "operationName": None,
            "variables": {},
            "query": "{\n  getQuests {\n    name\n    title\n    description\n    haha_wallet_created\n    swap_count\n    swap_amount\n    app_open_count\n    status\n    disabled\n    karma_cost\n    karma_multiplier\n    karma_reward\n    tasks {\n      title\n      description\n      deeplink\n      completed\n      progress\n      progress_text\n      progress_total\n      amount\n      amount_total\n      task_id\n      task_type\n      content\n      __typename\n    }\n    __typename\n  }\n}"
        })
        headers = {
            **self.headers,
            "Authorization": token,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
                
    async def claim_social_tasks(self, token: str, task_name: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/wallet-api/graphql"
        data = json.dumps({
            "operationName": "claimQuestEx",
            "variables": {
                "questName": task_name
            },
            "query": "mutation claimQuestEx($questName: String!) {\n  claimQuestEx(questName: $questName) {\n    success\n    message\n    __typename\n  }\n}"
        })
        
        headers = {
            **self.headers,
            "Authorization": token,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
        
    async def process_users_login(self, email: str, password: str, use_proxy: bool, rotate_proxy: bool):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.YELLOW + Style.BRIGHT}Trying to Login, Wait...{Style.RESET_ALL}",
            end="\r",
            flush=True
        )

        proxy = self.get_next_proxy_for_account(email) if use_proxy else None

        if rotate_proxy:
            token = None
            while token is None:
                token = await self.users_login(email, password, proxy)
                if not token:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Login Failed With Proxy {Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT}{proxy},{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Rotating Proxy... {Style.RESET_ALL}"
                    )
                    proxy = self.rotate_proxy_for_account(email) if use_proxy else None
                    await asyncio.sleep(5)
                    continue

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Login Success {Style.RESET_ALL}"
                )

                return token["id_token"]

        token = await self.users_login(email, password, proxy)
        if not token:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Login Failed With Proxy {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            )
            return None
        
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} Login Success {Style.RESET_ALL}"
        )

        return token["id_token"]
        
    async def process_accounts(self, email: str, password: str, use_proxy: bool, rotate_proxy: bool):
        token = await self.process_users_login(email, password, use_proxy, rotate_proxy)
        if token:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            karma = "N/A"
            user = await self.user_balance(token, proxy)
            if user:
                karma = user.get("data", {}).get("getKarmaPoints", 0)
                
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Balance   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {karma} Karma {Style.RESET_ALL}"
            )
            
            daily_checkin = await self.daily_checkin(token, proxy)
            if daily_checkin:
                is_claimable = daily_checkin.get("data", {}).get("getDailyCheckIn", False)

                if is_claimable:
                    claim = await self.claim_checkin(token, proxy)
                    if claim:
                        is_claimed = claim.get("data", {}).get("setDailyCheckIn", False)

                        if is_claimed:
                            karma = "N/A"
                            user = await self.user_balance(token, proxy)
                            if user:
                                karma = user.get("data", {}).get("getKarmaPoints", 0)

                            self.log(
                                f"{Fore.CYAN+Style.BRIGHT}Check-In  :{Style.RESET_ALL}"
                                f"{Fore.GREEN+Style.BRIGHT} Claimed Successfully {Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.CYAN+Style.BRIGHT} Balance {Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT}{karma} Karma{Style.RESET_ALL}"
                            )
                        else:
                            self.log(
                                f"{Fore.CYAN+Style.BRIGHT}Check-In  :{Style.RESET_ALL}"
                                f"{Fore.YELLOW+Style.BRIGHT} Not Claimed {Style.RESET_ALL}"
                            )
                    else:
                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}Check-In  :{Style.RESET_ALL}"
                            f"{Fore.RED+Style.BRIGHT} Not Claimed {Style.RESET_ALL}"
                        )
                else:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Check-In  :{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} Already Claimed {Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Check-In  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} GET Status Failed {Style.RESET_ALL}"
                )
            
            self.log(f"{Fore.CYAN+Style.BRIGHT}Task Lists:{Style.RESET_ALL}")

            basic_task_lists = await self.basic_task_lists(token, proxy)
            if basic_task_lists:
                basic_tasks = basic_task_lists.get("data", {}).get("getOnboarding", {}).get("tasks", [])

                if basic_tasks:
                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   ● {Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT}Basic Tasks{Style.RESET_ALL}"
                    )

                    for basic_task in basic_tasks:
                        if basic_task:
                            task_id = basic_task["task_id"]
                            title = basic_task["name"]
                            reward = basic_task["karma_available"]
                            is_completed = basic_task["completed"]
                            is_paid = basic_task["karma_paid"]
                            today_tx = basic_task["today_transactions"]

                            if is_completed and is_paid:
                                self.log(
                                    f"{Fore.MAGENTA+Style.BRIGHT}      > {Style.RESET_ALL}"
                                    f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                                    f"{Fore.YELLOW+Style.BRIGHT} Already Completed {Style.RESET_ALL}"
                                )
                                continue

                            if task_id == 14:
                                count = 10
                                if today_tx is None:
                                    today_tx = 0
                                    count = 10 - today_tx
                                else:
                                    count = 10 - today_tx

                                for _ in range(count):
                                    claim = await self.claim_basic_tasks(token, task_id, proxy)
                                    if claim and claim.get("data", {}):
                                        self.log(
                                            f"{Fore.CYAN+Style.BRIGHT}      > {Style.RESET_ALL}"
                                            f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                                            f"{Fore.GREEN+Style.BRIGHT} Claimed Successfully {Style.RESET_ALL}"
                                            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                                            f"{Fore.CYAN+Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                            f"{Fore.WHITE+Style.BRIGHT}{reward} Karma{Style.RESET_ALL}"
                                        )
                                    else:
                                        self.log(
                                            f"{Fore.CYAN+Style.BRIGHT}      > {Style.RESET_ALL}"
                                            f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                                            f"{Fore.RED+Style.BRIGHT} Not Claimed {Style.RESET_ALL}"
                                        )
                                        break

                                    await asyncio.sleep(1)

                            else:
                                claim = await self.claim_basic_tasks(token, task_id, proxy)
                                if claim and claim.get("data", {}):
                                    self.log(
                                        f"{Fore.CYAN+Style.BRIGHT}      > {Style.RESET_ALL}"
                                        f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                                        f"{Fore.GREEN+Style.BRIGHT} Claimed Successfully {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                                        f"{Fore.CYAN+Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                        f"{Fore.WHITE+Style.BRIGHT}{reward} Karma{Style.RESET_ALL}"
                                    )
                                else:
                                    self.log(
                                        f"{Fore.CYAN+Style.BRIGHT}      > {Style.RESET_ALL}"
                                        f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                                        f"{Fore.RED+Style.BRIGHT} Not Claimed {Style.RESET_ALL}"
                                    )

                            await asyncio.sleep(1)
                else:
                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   ● {Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT}Basic Tasks:{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} No Available Tasks {Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   ● {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Basic Tasks:{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} GET Lists Data Failed {Style.RESET_ALL}"
                )

            social_task_lists = await self.social_task_lists(token, proxy)
            if social_task_lists:
                social_tasks = social_task_lists.get("data", {}).get("getQuests", [])

                if social_tasks:
                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   ● {Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT}Social Tasks{Style.RESET_ALL}"
                    )

                    for social_task in social_tasks:
                        if social_task:
                            task_name = social_task["name"]
                            title = social_task["description"]
                            reward = social_task["karma_reward"]
                            status = social_task["status"]

                            if status == reward:
                                self.log(
                                    f"{Fore.CYAN+Style.BRIGHT}      > {Style.RESET_ALL}"
                                    f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                                    f"{Fore.YELLOW+Style.BRIGHT} Already Completed {Style.RESET_ALL}"
                                )
                                continue
                            
                            claim = await self.claim_social_tasks(token, task_name, proxy)
                            if claim and claim.get("data", {}):
                                self.log(
                                    f"{Fore.CYAN+Style.BRIGHT}      > {Style.RESET_ALL}"
                                    f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                                    f"{Fore.GREEN+Style.BRIGHT} Claimed Successfully {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.CYAN+Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                    f"{Fore.WHITE+Style.BRIGHT}{reward} Karma{Style.RESET_ALL}"
                                )
                            else:
                                self.log(
                                    f"{Fore.CYAN+Style.BRIGHT}      > {Style.RESET_ALL}"
                                    f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                                    f"{Fore.RED+Style.BRIGHT} Not Claimed {Style.RESET_ALL}"
                                )

                            await asyncio.sleep(1)
                else:
                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   ● {Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT}Social Tasks:{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} No Available Tasks {Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   ● {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Social Tasks:{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} GET Lists Data Failed {Style.RESET_ALL}"
                )
    
    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED}No Accounts Loaded.{Style.RESET_ALL}")
                return

            use_proxy_choice, rotate_proxy = self.print_question()

            while True:
                use_proxy = False
                if use_proxy_choice in [1, 2]:
                    use_proxy = True

                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies(use_proxy_choice)
        
                separator = "=" * 15
                for account in accounts:
                    if account:
                        email = account.get('Email')
                        password = account.get('Password')

                        if "@" in email and password:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(email)} {Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                            )
                            await self.process_accounts(email, password, use_proxy, rotate_proxy)
                            await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*53)
                seconds = 12 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed...{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = HahaWallet()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Haha Wallet - BOT{Style.RESET_ALL}                                       "                              
        )