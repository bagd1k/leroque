import time
import re

import requests
from bs4 import BeautifulSoup


class WrongCookies(Exception):
    def __init__(self, message="Wrong RR cookies"):
        self.message = message
        super().__init__(self.message)


class RRSession(requests.Session):
    def __init__(self, c):
        super().__init__()
        self.c = {'c': c}

    def checkValid(self):
        if "$('.vkvk').attr('url', 'https://oauth.vk.com/authorize" in self.get('https://rivalregions.com/').text:
            raise WrongCookies
        return 1

    def upPerk(self, perk, speed):
        if self.checkValid():
            self.post(f"https://rivalregions.com/perks/up/{perk}/{speed}", data=self.c)

    def upPerkUntil(self, perk, speed, border, delay=60):
        while self.getPerk(perk) < border:
            self.upPerk(perk, speed)
            time.sleep(delay)
        return True

    def getPerk(self, perk):
        if self.checkValid():
            def is_stat(tag):
                if tag.has_attr('action'):
                    return 'perk' in tag['action']
                return False

            if self.checkValid():
                soup = BeautifulSoup(self.post('https://rivalregions.com/slide/profile').text, 'html.parser')
                return int(soup.find_all(is_stat)[perk - 1].text)

    def flyTo(self, regId, typeOf=2):
        if self.checkValid():
            data = {}
            data.update(self.c)
            data.update({'type': typeOf})
            data.update({'b': 1})
            timeToReturn = int(re.search(r'until: (\d+)', self.post(f'https://rivalregions.com/map/region_move/{regId}',
                                                                    data=data).text).group(1))
            return timeToReturn

    def autoSet(self, warId, sideId, numOfTanks):
        if self.checkValid():
            data = {}
            data.update({'free_ene': 1})
            data.update(self.c)
            data.update({'n': str({"t1": "0", "t2": str(numOfTanks)}).replace("'", '"')})
            data.update({"aim": sideId})
            data.update({'edit': warId})
            self.get(f'https://rivalregions.com/war/details/{warId}', data=self.c)
            self.post('https://rivalregions.com/war/autoset/', data=data)

    def renewAuto(self, factoryId, enPermit=False):
        if self.checkValid():
            self.post(f"https://rivalregions.com/factory/assign", data={
                'factory': factoryId,
                'c': self.c,
            })
            if enPermit:
                self.get(f"https://rivalregions.com/storage/newproduce/17/300", data=self.c)
            self.post('https://rivalregions.com/work/autoset/', data={
                'c': self.c,
                'mentor': 0,
                'factory': factoryId,
                'type': 0,
                'lim': 0,
            })

    def getRegId(self):
        if self.checkValid():
            def isRegion(tag):
                if tag.has_attr('action'):
                    return "map/details/" in tag
            soup = BeautifulSoup(self.get('https://rivalregions.com/slide/profile/').text)
            return re.search("(\d+)", soup.find_all(isRegion)[0]).group(1)


def authByCookie(_cookies, c, proxies=None, userAgent=None):
    session = RRSession(c)
    if proxies is not None:
        session.proxies.update(proxies)
    if userAgent is None:
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/81.0.4044.142 Safari/537.36'})
    else:
        session.headers.update({'User-Agent': userAgent})
    session.get('https://rivalregions.com/')
    session.cookies.update(_cookies)
    return session

