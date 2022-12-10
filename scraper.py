import mechanicalsoup
import pandas as pd
import getpass
import login

urls = {
    "login":"https://justfor.fans/login.php",
    "home_url":"https://justfor.fans/home",

}

# User agent of your choice
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
session_file = "session.j4f"

# Create a browser object
class Browser:
    def __init__(self,name):
        self.media = {}
        self.name = name
        self.poster_id=""
        self.hash4=""
        if not self.load_session():
            self.browser = mechanicalsoup.StatefulBrowser(user_agent=user_agent)
            self.browser.open(urls["login"])
            self.url = self.browser.get_url()
            self.page = self.browser.get_current_page()
            self.session = self.browser.session
            self.cookies = self.session.cookies.get_dict()
            self.headers = self.session.headers
            self.user_agent = user_agent

    def print(self):
        print(self.url)
        print(self.media)
        print(self.poster_id)

    def login(self):
        try:
            # _u = input("Email: ")
            # _p = input("Password: ")
            _u = login._u
            _p = login._p
            self.browser.select_form()
            self.browser["Email"] = _u
            self.browser["Password"] = _p
            self.browser.submit_selected()
            self.page = self.browser.get_current_page()
            self.session = self.browser.session
            self.cookies = self.session.cookies.get_dict()
            self.headers = self.session.headers
            self.url = self.browser.get_url()
        except:
            print("Login Failed")
    def go(self,url):
        try:
            self.browser.open(url)
            self.page = self.browser.get_current_page()
            self.session = self.browser.session
            self.cookies = self.session.cookies.get_dict()
            self.headers = self.session.headers
            self.url = self.browser.get_url()
            if not self.url == url:
                raise Exception("Failed to go to url")
        except Exception as e:
            print(e)
    def save_session(self):
        session = pd.DataFrame([self.name,self.cookies,self.headers,self.user_agent])
        session.to_csv(session_file)
    def load_session(self):
        try:
            session_info = pd.read_csv(session_file)
            if not self.name == session_info[0][0]:
                return False
            self.cookies = session_info[1][0]
            self.headers = session_info[2][0]
            self.user_agent = session_info[3][0]
            self.browser = mechanicalsoup.StatefulBrowser(user_agent=self.user_agent)
            self.browser.set_cookiejar(self.cookies)
            self.browser.session.headers = self.headers
            self.go(urls["home_url"])
            if self.browser.get_url() == urls["home_url"]:
                return True
            else:
                return False
        except:
            return False
    def get_subs(self):
        performers_div = self.browser.get_current_page().find_all("div", {"id": "homeMyPerformers"})
        performers_data = []
        for performer in performers_div:
            data = {"profile_url": "https://justfor.fans{}".format(performer.find("a")["href"]),
                    "name": performer.find("a").text.strip(), "image": performer.find("img")["src"]}
            performers_data.append(data)
        self.performers_data = performers_data

    def parse_subs(self):
        for sub in self.performers_data:
            self.go(sub["profile_url"])
            sub_photo_data = self.page.find_all("div" , {"id":"postAreaAutoScroll"})
            print(sub_photo_data)

            ub_video_data = self.page.find_all("div", {"class": "video"})
            sub_audio_data = self.page.find_all("div", {"class": "audio"})
            sub_photos = []
            sub_videos = []
            sub_audios = []
            sub_name = sub["name"]
            sub_data = {"name": sub_name, "photos": sub_photos, "videos": sub_videos, "audios": sub_audios}
            self.media.update({sub_name:sub_data})
    def get_poster_id(self):
        links = self.page.find_all("a")
        for link in links:
            if not link["href"].startswith("/ajax"):
                links.remove(link)
        x = links[0]["href"]
        for i in x.split('&'):
            if i.startswith("UserHash4"):
                self.hash4 = i.split("=")[1]
        print(self.hash4)




def process():
    j4f = Browser("j4f")
    j4f.login()
    j4f.save_session()
    j4f.go(urls["home_url"])
    j4f.get_subs()
    j4f.parse_subs()
    j4f.get_poster_id()
    j4f.print()


if __name__ == "__main__":
    process()