import requests
from bs4 import BeautifulSoup
from google_play_scraper import app,reviews
from google_play_scraper.constants.google_play import Sort

class Authentication_Info:
    def __init__(self,package_name):
        self.package_name = package_name

    def app_details(self,country='in'):
        try:
            details = app(self.package_name,country=country)
        except Exception as e:
            return False
        
        return details

    def user_review(self,country='in',num_reviews=5):
        try:
            rev = reviews(self.package_name,country=country,sort=Sort.MOST_RELEVANT,count=num_reviews)
        except Exception as e:
            return False
        return rev

    def data_accountability(self):
        url = f"https://play.google.com/store/apps/details?id={self.package_name}&hl=en"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        cont = soup.find_all("div", class_="wGcURe")

        data_privacy = []

        for c in cont:
            data_privacy.append(c.text)

        return data_privacy

    def app_permission(self):
        url = f"https://play.google.com/store/apps/datasafety?id={self.package_name}&hl=en"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        res = soup.find_all('div',class_='XgPdwe')

        permissions = []

        if len(res) > 1:
            perm = res[1].find_all('div',{"jscontroller":"ojPjfd"})
            for per in perm:
                permissions.append(per.h3.text)
        elif len(res) == 1:
            perm = res.find_all('div',{"jscontroller":"ojPjfd"})
            if len(perm) == 0:
                return []
            else:
                for per in perm:
                    permissions.append(per.h3.text)
        else:
            return []

        return permissions

    def data_privacy_analysis(self,info):
        non_sus = ["No data shared with third parties",
        "Data is encrypted in transit",
        "No data collected"]
        sus = ["Data shared with third parties",
        "This app may share these data types with third parties",
        "Data isn't encrypted"]
        suspect = 0
        non_suspect = 0
        for i in info:
            if i in non_sus:
                non_suspect += 1
            elif i in sus:
                suspect += 1

        if non_suspect > suspect:
            return "looking genuine"
        elif non_suspect == suspect:
            return "can't say anything"
        else:
            return "suspect"


__all__ = [Authentication_Info]