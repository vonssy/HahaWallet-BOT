from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
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
            "Content-Type": "application/json",
            "Origin": "chrome-extension://andhndehpcjpmneneealacgnmealilal",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none",
            "User-Agent": FakeUserAgent().random,
            "X-Request-Source-Extra": "chrome"
        }

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
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"
        
    async def user_login(self, email: str, password: str, retries=5):
        url = "https://prod.haha.me/users/login"
        data = json.dumps({"email":email, "password":password})
        headers = {
            **self.headers,
            "Content-Length": str(len(data))

        }
        for attempt in range(retries):
            try:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
                
    async def user_login(self, email: str, password: str, retries=5):
        url = "https://prod.haha.me/users/login"
        data = json.dumps({"email":email, "password":password})
        headers = {
            **self.headers,
            "Content-Length": str(len(data))

        }
        for attempt in range(retries):
            try:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['id_token']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return None
                
    async def user_balance(self, token: str, retries=5):
        url = "https://prod.haha.me/wallet-api/graphql"
        data = json.dumps({"operationName":None,"variables":{},"query":"{\n  getKarmaPoints\n}"})
        headers = {
            **self.headers,
            "Authorization": token,
            "Content-Length": str(len(data))
        }
        for attempt in range(retries):
            try:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return None
                
    async def daily_checkin(self, token: str, retries=5):
        url = "https://prod.haha.me/wallet-api/graphql"
        data = json.dumps({"operationName":None,"variables":{"timezone":"Asia/Jakarta"},"query":"query ($timezone: String) {\n  getDailyCheckIn(timezone: $timezone)\n}"})
        headers = {
            **self.headers,
            "Authorization": token,
            "Content-Length": str(len(data))
        }
        for attempt in range(retries):
            try:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return None
                
    async def claim_checkin(self, token: str, retries=5):
        url = "https://prod.haha.me/wallet-api/graphql"
        data = json.dumps({"operationName":None,"variables":{"timezone":"Asia/Jakarta"},"query":"mutation ($timezone: String) {\n  setDailyCheckIn(timezone: $timezone)\n}"})
        headers = {
            **self.headers,
            "Authorization": token,
            "Content-Length": str(len(data))
        }
        for attempt in range(retries):
            try:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']['setDailyCheckIn']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return None
        
    async def process_accounts(self, email: str, password: str):
        token = await self.user_login(email, password)
        if not token:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Login Failed {Style.RESET_ALL}"
            )
            return
        
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} Login Success {Style.RESET_ALL}"
        )

        balance = "N/A"

        user = await self.user_balance(token)
        if user:
            balance = user["getKarmaPoints"]
            
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}Balance :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {balance} Karma {Style.RESET_ALL}"
        )
        
        check_in = await self.daily_checkin(token)
        if not check_in:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} GET Data Failed {Style.RESET_ALL}"
            )
            return
        
        is_claimable = check_in['getDailyCheckIn']

        if is_claimable:
            claim = await self.claim_checkin(token)
            
            if claim:

                balance = "N/A"
                user = await self.user_balance(token)
                if user:
                    balance = user["getKarmaPoints"]

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Is Claimed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT} Balance {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{balance} Karma{Style.RESET_ALL}"
                )
            else:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Isn't Claimed {Style.RESET_ALL}"
                )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} Is Already Claimed {Style.RESET_ALL}"
            )
    
    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED}No Accounts Loaded.{Style.RESET_ALL}")
                return

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )
        
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
                            await self.process_accounts(email, password)
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