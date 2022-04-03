__auth__ = 'Hadi Ayoub'
__date__ = '11/25/2020'
__name__ = '__EgyBest__'

import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import chromedriver_autoinstaller
from webdriver_manager.chrome import ChromeDriverManager
# from pywinauto import application
# from pywinauto.keyboard import send_keys
# from win10toast import ToastNotifier

from requests import request
from bs4 import BeautifulSoup
import time
import sys
import re
import os


class EgyBest:
    home_page = 'https://uper.egybest.org/'

    # this for save the memory
    __slots__ = ['_name', 'path', '_results', '_titles', '_choices', '_links', '_driver', 'tries',
                 'toaster', 'counter', 'story', 'info', 'trailer', 'img_saved_path']

    def __init__(self, name):
        
        self._name = str(name).strip()  # the name of desired type
        self._results = []  # a lists to hold the results
        self._titles = []  # a list to hold the names of the results
        self._choices = []  # a list to hold the desired choices
        self._links = []  # a list that hold the links of the videos
        self.path = os.getcwd()  # get the current directory
        self.tries = self.counter = 0

        # open the browser
        caps = DesiredCapabilities.CHROME
        caps['pageLoadStrategy'] = 'eager'
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        self._driver = webdriver.Chrome(desired_capabilities=caps, executable_path=ChromeDriverManager().install(), options=option)

        # get to EgyBest home page and close notifications
        sys.stdout.write(f' Launching the browser..')
        sys.stdout.flush()
        self._driver.get(self.home_page)

        self.close_notifications()

        # search in the search box
        self.search()
        # sys.stdout.write('\r')
        # sys.stdout.flush()

    """ close the notification alert that pop-up once the page loaded """

    def close_notifications(self):
        try:
            later = WebDriverWait(self._driver, 15, poll_frequency=1).until(
                EC.presence_of_element_located((By.LINK_TEXT, 'لاحقاً')))
            later.click()
            self.close_ads()
        except:
            pass
            # print('\r The website doesn\'t show notification alert... maybe the connection is too bad!')

    """ close any ads that may pop-up """

    def close_ads(self):
        time.sleep(1)
        # get the current active tab
        main_tab = self._driver.current_window_handle
        # loop through each tab and close all, except the main_tab
        for tab in self._driver.window_handles:
            if tab != main_tab:  # it's not the main_tab
                self._driver.switch_to.window(tab)
                time.sleep(.5)
                self._driver.close()

        #  get back to the main_tab
        self._driver.switch_to.window(main_tab)

    """ search for the {name} in the search box """

    def search(self):
        # filtering the results to be limited on those whom have the {self._name} in their text

        def results_filter(res):
            # time.sleep(2)
            # #movies > a:nth-child(1) > span.title
            try:
                title = str(res.find_element_by_css_selector('span.title').text).lower().strip()
                print(title)
            except NoSuchElementException as e:
                print(res.get_attribute('innerHTML'))
                return False
            if isinstance(self, Movie) and self._name in title and title.find('(') != -1:
                return True
            if isinstance(self, Series) and self._name in title and title.find('(') == -1:
                return True

        # type the name in the search box
        try:
            search_box = WebDriverWait(self._driver, 20, poll_frequency=1).until(
                EC.presence_of_element_located((By.NAME, 'q'))
            )
            search_box.click()
            self.close_ads()
            # print('\rWe\'re in the search box')

            # type the name
            search_box.send_keys(self._name)
            time.sleep(1)
            search_box.send_keys(Keys.RETURN)

            print('', end='\r')
            for i in range(100): print(' ', end='')
            print('', end='\r')
            sys.stdout.write(f' Getting results..')
            sys.stdout.flush()

        except:
            print('\r Cannot find the search box\n Your connection is bad!')
            sys.exit(0)

        self.close_ads()

        # an error because of ads blocker
        while True:
            try:
                box = WebDriverWait(self._driver, 5, poll_frequency=1).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#mainLoad > div'))
                )

                # error
                if 'error' in box.getAttribute('class').split():
                    retry = box.find_element_by_tag_name('a')
                    retry.click()
                    time.sleep(1)
                    self.close_ads()
                    # print('\rwhile')
            except:
                break

        # self.scroll()

        # wait for the appearance of search results
        try:
            # #movies > a > span.title
            self._results = WebDriverWait(self._driver, 10, poll_frequency=1).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#movies > a'))
            )
        except:  # no result found
            # print a text
            print(f' \r* No results found! *')
            self._driver.quit()  # close the browser
            sys.exit(0)  # terminate the program

        self._results = list(filter(results_filter, self._results))
        found_results = int(len(self._results))

        print('', end='\r')
        for i in range(100): print(' ', end='')
        print('', end='\r')

        import inflect
        print(f' >=> {found_results} {inflect.engine().plural_noun("result", found_results)} found\n')

        if found_results == 0:
            sys.exit(0)

        """
            if there is only one result, then don't add (all and all-) to the option, just choose the only found one
            else add the options (all, all-) to options list
        """

        if found_results > 1:
            # make a tuple of results with an id for each result
            self._results = [(str(i), res) for i, res in zip(range(1, len(self._results) + 1), self._results)]
            self._titles = [(str(i), str(res.find_element_by_class_name('title').text)) for i, res in self._results]
            self._titles.extend([(str(len(self._titles) + 1), 'all'), (str(len(self._titles) + 2), 'all-')])

        else:
            self._results = [(str(1), self._results[0])]
            self._titles = [(str(1), str(self._results[0][1].find_element_by_class_name('title').text))]

        # display the results

        self.display_results()

    def get_search_results(self):
        return self._results

    """ scroll down to see all results """

    def scroll(self):
        # results found, keep scrolling till no result found
        while True:
            time.sleep(1)
            body = self._driver.find_element_by_tag_name('body')
            body.send_keys(Keys.END)  # use the END key to scroll-down
            try:
                WebDriverWait(self._driver, 10, poll_frequency=1).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, '#movies > a.auto.load.btn.b')))
            except:  # we reach the end of the page and an exception is raised, so scroll-up to the beginning
                body.send_keys(Keys.HOME)  # use the HOME key to scroll-up
                break

    """ display the results """

    def display_results(self):

        for i, title in self._titles:
            print(f'    {i}. {title}')
        print()

    def get_available_qualities(self) -> list:
        available_qualities = []

        # pattern to extract only quality from text
        pattern = re.compile(r'\d{3,4}p')

        selector = '#watch_dl > table > tbody > tr'
        tr = self._driver.find_elements_by_css_selector(selector)

        for td in tr:
            td = td.find_element_by_css_selector('td:nth-child(2)')
            quality = td.text.strip()
            match = re.search(pattern, quality)
            available_qualities.append(match.group())

        return available_qualities

    def get_pic(self) -> str:
        selector = '#mainLoad > div:nth-child(1) > div.full_movie.table.full.mgb > div.movie_cover.mgb.tam.td.vat.pdl > div > a > img'
        img = self._driver.find_element_by_css_selector(selector)

        src_attr = img.get_attribute('src')

        # print(f'pic src_attr is {src_attr}')

        pic_name = src_attr.split('/')[-1]
        save_path = os.path.join(os.getcwd().split('/EgyBest')[0], 'media', pic_name)

        # print(f'pic saved at {save_path}')

        import requests

        with open(save_path, 'wb') as f:
            for chunk in requests.get(src_attr, stream=True).iter_content():
                if chunk:
                    f.write(chunk)

        # return save path
        return save_path

    def get_trailer(self) -> str:
        # print('get_trailer() function')

        selector = '#yt_trailer > div.play.p.api'
        video = self._driver.find_element_by_css_selector(selector)
        yt_id = str(video.get_attribute('url')).split('/')[-1].split('?')[0]

        url = f'https://www.youtube.com/watch?v={yt_id}'
        return url

    def get_story(self) -> str:
        # print('get_story() function', self._driver.title)
        selector = '#mainLoad > div:nth-child(1) > div:nth-child(5) > div:nth-child(2)'
        story = self._driver.find_element_by_css_selector(selector)
        story = str(story.text).strip()

        return story

    def get_rating(self):
        # print('get_rating() function', self._driver.title)
        selector = '#mainLoad > div:nth-child(1) > div.full_movie.table.full.mgb > div:nth-child(2) > ' \
                   'table > tbody > tr:nth-child(5) > td:nth-child(2) > strong > span'

        # #mainLoad > div:nth-child(1) > div.full_movie.table.full.mgb > div:nth-child(2)
        # > table > tbody > tr:nth-child(5) > td:nth-child(2) > strong > span

        rating = self._driver.find_element_by_css_selector(selector)
        rating = str(rating.text).strip()

        return f'{rating}/10'

    def get_class(self):
        # print('get_class() function', self._driver.title)
        selector = '#mainLoad > div:nth-child(1) > div.full_movie.table.full.mgb > div:nth-child(2) > ' \
                   'table > tbody > tr:nth-child(3) > td:nth-child(2)'

        class_ = self._driver.find_element_by_tag_name('a').text.strip()
        class_ = f'{class_} {self._driver.find_element_by_css_selector(selector).text.strip(".")}'

        return class_

    def get_types(self) -> str:
        # print('get_types() function', self._driver.title)
        selector = '#mainLoad > div:nth-child(1) > div.full_movie.table.full.mgb > div:nth-child(2) > table > tbody > tr:nth-child(4) > td:nth-child(2)'
        types = self._driver.find_element_by_css_selector(selector)
        types = types.find_elements_by_tag_name('a')

        types = ' | '.join([t.text.strip() for t in types])

        return types

    # def get_info(self):
    #     print('get_info() function')
    #
    #     info = f'**التصنيف**\n {self.get_class()}\n\n**النوع**\n {self.get_types()}\n\n**التقييم**\n {self.get_rating()}\n\n**القصة**\n' \
    #            f' {self.get_story()}'
    #
    #     return info

    """ go through each choice and get the download link """

    def get_to_vidstream(self, quality, episodes=None):
        i = 0
        # print(f'choices = {self._choices} *** {len(self._choices)}')
        # print(f'episodes = {episodes} *** {len(episodes)}')
        for link in self._choices:
            sys.stdout.write(f' Getting download page..')
            sys.stdout.flush()
            self.close_ads()
            self._driver.get(link)  # go to webpage of this choice
            self.get_video_download_link(quality)

            # quality = f'{self.quality} > td.tar > a.nop.btn.g.dl._open_window'
            # '''#watch_dl > table > tbody > tr:nth-child(1) > td.tar > a.nop.btn.g.dl._open_window'''
            # try:
            #     download_btn = self._driver.find_element_by_css_selector(quality)
            #     download_btn.click()  # click on the download button of the high-quality
            # except:
            #     print("Video not available now!")
            #     sys.exit(0)

            # get the video download link
            # try:
            #     self.get_video_download_link(quality)
            #     i = (i + 1) % len(episodes)
            #
            # except:
            #     self.get_video_download_link(quality)

    """ get the download links from VidStream """

    def get_video_download_link(self, quality):
        while self._driver.title != 'VidStream':
            # print('\rtrying finding the button')
            # print(self._driver.title, self._driver.current_url)
            # btn = self._driver.find_element_by_css_selector(quality)
            # print(btn.get_attribute('class'))
            # print(quality)
            try:
                download_btn = WebDriverWait(self._driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f'{quality} > td.tar > '
                                                                     f'a.nop.btn.g.dl._open_window'))
                )
                download_btn.click()
                time.sleep(4)
                # print('clicked')
                """
                    make the active tab is VidStream
                    by closing other tabs
                """
                main_tab = self._driver.current_window_handle
                same_title = self._driver.title
                q = True
                for tab in self._driver.window_handles:
                    if self._driver.title == 'VidStream':  # it's vidstream page
                        self._driver.switch_to.window(tab)
                        q = False
                        break

                    if self._driver.title == same_title:
                        main_tab = tab

                    else:
                        self._driver.close()

                    self._driver.switch_to.window(tab)  # switch active tab to this one

                # if q:
                #     self._driver.switch_to.window(main_tab)

                if self._driver.title == 'VidStream':
                    try:
                        WebDriverWait(self._driver, 60).until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'bigbutton'))
                        )
                        url = self._driver.current_url
                        # print('\rgot the url')
                        break

                    # VidStream page url is received successfully
                    except:
                        print("Your internet connection is slow!")
                        self._driver.quit()
                        break
                # print('\rdone')
            except Exception as e:
                print('\rerror, ', self._driver.title)
                print(e)

                try:
                    self._driver.find_element_by_css_selector('#mainLoad > div.msg_box.error.full.tam')
                except:
                    try:
                        retry = WebDriverWait(self._driver, 60).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainLoad > div > a'))
                        )
                        while True:
                            retry.click()
                            try:
                                self._driver.find_element_by_css_selector('#mainLoad > div.msg_box.error.full.tam')
                            except:
                                break
                    except:
                        print('\rpage found')

            self.tries += 1
            if self.tries >= 5:
                self.tries = 0
                body = self._driver.find_element_by_tag_name('body')
                body.click()
                self.close_ads()

        """****************************************************************************"""
        # """
        #     make the active tab is VidStream
        #     by closing other tabs
        # """
        # for tab in self._driver.window_handles:
        #     if self._driver.title == 'VidStream':
        #         self._driver.switch_to.window(tab)
        #         break
        #     self._driver.switch_to.window(tab)
        #
        # """
        #     if when click on the <body> another ads tab just popup and not the VidStream
        #         make sure this tab is VidStream.
        # """
        if self._driver.title == 'VidStream':
            # wait the download button to be shown
            download_btn = self._driver.find_element_by_class_name('bigbutton')
            link = download_btn.get_attribute('href')

            # the button is not clickable from the first time
            if not link:
                download_btn.click()
                self.close_ads()

            # fetch the download link and store it
            time.sleep(1)
            download_btn = self._driver.find_element_by_class_name('bigbutton')
            # print(download_btn.text, download_btn.get_attribute())
            time.sleep(1)
            link = download_btn.get_attribute('href')
            self._links.append(link)
            # print(f'\rlink is: {link}')

            # get the name of the file from the end of the link
            # name = link.split('/')[-1].replace('[EgyBest]', '').replace('.', ' ').strip()
            name = self._driver.find_element_by_css_selector('body > div.mainbody > div > h2').text.strip()

            # if isinstance(self, Series):
            #     season_pattern = re.compile(r'S[0-9][0-9]E[0-9][0-9]')
            #     try:
            #         match = season_pattern.search(name)
            #         print(f'match season = {match.group()}')
            #         name = f'{self._name.title()} {match.group()}'
            #     except:
            #         print(f'match error\nname = {name}')
            #         name = f'{self._name.title()} S{str(self.get_season()).zfill(2)}E{str(attr).zfill(2)}'
            #
            # elif isinstance(self, Movie):
            #     name = f'{self._name.title()}'
            #     # movie_pattern = re.compile(r'(\d{4})[^p]')
            #     # try:
            #     #     match = movie_pattern.search(name)
            #     #     name = f'{self._name.title()} ({match.group(1)})'
            #     # except:
            #     #     name = f'{self._name} ({attr})'

            print(f'\r [*] Link received for => \033[1m{name}\033[0m')
            self.save_links(link)


        # else:  # it's not the VidStream tab so try again
        #     # if self.tries > 10:
        #     #     if isinstance(self, Movie):
        #     #         self._driver.quit()
        #     #         Movie(self._name, self.quality)
        #     #     else:
        #     #         self._driver.quit()
        #     #         with open('inputs.txt', 'r') as f:
        #     #             f.readline()
        #     #             season, *episodes = f.readline().strip().split()
        #     #         Series(self._name, self.quality, season, episodes)
        #
        #     time.sleep(1)
        #     self._driver.refresh()
        #     quality = f'{self.quality} > td.tar > a.nop.btn.g.dl._open_window'
        #     try:
        #         download_btn = WebDriverWait(self._driver, 10, poll_frequency=1).until(
        #             EC.presence_of_element_located((By.CSS_SELECTOR, quality))
        #         )
        #         download_btn.click()
        #     except:
        #         sys.exit(0)
        #     self.tries += 1
        #     self.get_video_download_link()

    """ save the links in a .txt file """

    def save_links(self, link):

        from pathlib import Path

        password = str(os.environ.get("PASS")).strip('"')

        desktop = os.path.join(Path.home(),  'Desktop')
        os.chdir(desktop)  # change the work directory to DESKTOP

        name = self._name
        for char in "\\ \'\"!@#$%^&*(){}[]?":
            name = name.replace(char, f"\{char}")

        name = name.title() + '.txt'

        # source path
        src = os.path.join(desktop, name)
        # print()
        # print(src, name, sep=' *** ')

        # file name to save it in the server
        # name_to_save = name
        # for char in "\\ \'\"!@#$%^&*(){}[]?-_=+<>":
        #     name_to_save = name_to_save.replace(char, '')

        # dest = os.path.join('/var/www/html/', name_to_save.lower())
        # dest = '/var/www/html/'

        # there is only one link to save
        if self.counter == 0:
            with open(f'{self._name.title()}.txt', 'w', encoding='utf-8') as f:
                f.write(f'{link}\n')
            self.counter += 1

            # os.chdir(dest)  # change work directory to /var/www/html/
            # print(src, name, sep=' *** ')
            # if len(self._choices) == 1:
            #    os.popen(f'sudo -S cp {src} {name_to_save.lower()}', 'w').write(password)
            # os.popen(f"sudo -S mv /var/www/html/{name} {dest}", 'w').write(password)

            return

        # file doesn't exist
        # if not os.path.isfile(f'{self._name.title()}.txt'):
        #     self._name = f'{self._name}_{self.counter}'
        #     self.counter += 1

        with open(f'{self._name.title()}.txt', 'a', encoding='utf-8') as f:
            f.write(f'{link}\n')
            self.counter += 1
        # print(self.counter)
        # command = f"sudo -S cp {os.path.join(desktop, name)} /var/www/html/{name_to_save.lower().strip()}"
        # print(command)

        # os.popen(f"sudo -S cp {src} {os.path.join(dest, name_to_save.lower())}", 'w').write(password)
        # os.popen(f"sudo -S mv /var/www/html/{name} {dest}", 'w').write(password)

    """ choose quality """

    @staticmethod
    def choose_quality(quality) -> str:
        # self.quality = str(input('\t\t * Choose quality (1080 | 720 | 480 | 360 | 240): '))
        # qualities table
        qualities = {
            '1080p': '#watch_dl > table > tbody > tr:nth-child(1)',
            '720p': '#watch_dl > table > tbody > tr:nth-child(2)',
            '480p': '#watch_dl > table > tbody > tr:nth-child(3)',
            '360p': '#watch_dl > table > tbody > tr:nth-child(4)',
            '240p': '#watch_dl > table > tbody > tr:nth-child(5)'
        }

        # f'{quality} > td.tar > a.nop.btn.g.dl._open_window'

        # for q, pos in qualities.items():
        #     if quality == q:
        #         quality = pos
        #         break

        return qualities[quality]


class Series(EgyBest):
    __slots__ = ['__season', '__episodes', '__seasons_number', '__episodes_number', '__quality', '__pic_saved_path', '__trailer_link',
                 '__types', '__class', '__rating', '__story']

    def __init__(self, name, *args):
        # self._season, self._episodes = args
        super().__init__(name)

        self.__seasons_number = 0
        self.__episodes_number = 0

        self.__quality = None
        self.__season = None
        self.__episodes = []

        self.choose_the_series()  # call the parent method series()

        self.__story = self.get_story()
        self.__types = self.get_types()
        self.__class = self.get_class()
        self.__rating = self.get_rating()

        self.__pic_saved_path = None
        self.__trailer_link = None

        # self.get_links()
        self.format_name()
        # self._driver.quit()
        # self.runIdm()
        print()

    def set_season(self, season):
        self.__season = season

        # go to {season}
        try:
            s = self._driver.find_element_by_css_selector('#mainLoad > div.mbox > div.h_scroll > '
                                                          f'div > a:nth-child('
                                                          f'{(self.__seasons_number + 1) - int(self.__season)})')

            # go to season page to get all episodes
            self._driver.get(s.get_attribute('href'))
            self.close_ads()
        except:
            print(f'\r ->> Season {self.__season} is out of range!')
            # self.toaster.show_toast('Season outta range!', f'Season {self.__season} is out of range!', duration=3)
            sys.exit(0)

        self.__pic_saved_path = self.get_pic()
        self.__trailer_link = self.get_trailer()

    def get_season(self):
        return self.__season

    def set_episodes(self, episodes):
        self.__episodes = episodes
        # print(self.__episodes, episodes, sep='\n\n\n')

    def set_quality(self, quality):
        self.__quality = self.choose_quality(quality)

    def get_pic_saved_path(self):
        return self.__pic_saved_path

    def get_trailer_link(self):
        return self.__trailer_link

    def get_series_story(self):
        return self.__story

    def get_series_rating(self):
        return self.__rating

    def get_series_class(self):
        return self.__class

    def get_series_types(self):
        return self.__types

    """
        this method will search for the series
        and will return True if the series is found, False otherwise
    """

    def choose_the_series(self) -> bool:
        choice = ''
        # there should only be one result for series type, so choose it
        q = False
        for i, res in self._results:
            title = res.find_element_by_class_name('title').text.lower().strip()
            if self._name == title:
                q = True
                choice = res.get_attribute('href')

        # No results found!
        if not q:
            print('\r *** Found no results! ***')
            return False
            # sys.exit(0)

        self._driver.get(choice)
        return True

    def get_seasons_number(self):
        self.__seasons_number = len(
            self._driver.find_element_by_css_selector('#mainLoad > div.mbox > div.h_scroll > div').find_elements_by_tag_name('a'))

        print(f'\r  -> {self._name.title()} has {self.__seasons_number} seasons')

        return self.__seasons_number

    """Get all season episodes and """
    def get_episodes_number(self):
        # self.get_story()

        self.__episodes_number = len(
            self._driver.find_element_by_css_selector('#mainLoad > div.mbox > div.movies_small').find_elements_by_tag_name('a'))

        print(f'\r  -> Season {self.__season} has {self.__episodes_number} episodes\n')

        return self.__episodes_number

    def get_links(self):
        eps = []
        # print(self.__episodes)
        # The choice was 'all' to choose all the episodes
        if self.__episodes[0] == 'all':
            self._choices = self._driver.find_elements_by_css_selector(
                '#mainLoad > div.mbox > div.movies_small > a')

            self._choices = [e.get_attribute('href') for e in self._choices]
            self._choices.reverse()
            eps = list(range(1, self.__episodes_number + 1))
            print(f'episodes number = {len(eps)} *** {eps}')

        # if choice was "#number:"
        elif isinstance(self.__episodes[0], str) and self.__episodes[0].endswith(':'):
            first = int(self.__episodes[0].split(':')[0])

            # extract the episodes from "#number" to the end
            self.__episodes = [e for e in range(first, self.__episodes_number + 1)]

        else:  # The choice was a bunch of episodes or specified one
            for e in self.__episodes:
                print(f'{self.__episodes_number + 1} *** {e}')
                try:
                    selector = f'#mainLoad > div.mbox > div.movies_small > a:nth-child({(self.__episodes_number + 1) - e})'
                    one_episode = self._driver.find_element_by_css_selector(selector)

                except Exception as ex:
                    print(f'\r ->> Episode {e} and episodes after out of range!\n{ex}')
                    break

                eps.append(e)
                self._choices.append(one_episode.get_attribute('href'))

        eps = list(set(eps))
        self.get_to_vidstream(self.__quality, eps)  # get downloads link from VidStream page
        self._driver.quit()  # close browser

    def format_name(self):
        season_pattern = re.compile(r'S[0-9]')
        season = season_pattern.search(self._name)
        try:
            self._name = self._name[:season.end()].replace('.', '').strip().title()
        except:
            self._name = self._name.strip()


class Movie(EgyBest):
    __slots__ = ['__movies_choices', 'years', '__quality', '__pic_saved_path', '__trailer_link',
                 '__types', '__class', '__rating', '__story']

    def __init__(self, name):
        super().__init__(name)
        self.__movies_choices = []
        self.years = []

        # self.choose_the_movies()

        self.__quality = None
        self.__pic_saved_path = None
        self.__trailer_link = None
        self.__types = None
        self.__class = None
        self.__rating = None
        self.__story = None

        self.get_to_vidstream(self.__quality)
        # self._name = self._name.title()
        # self._driver.quit()
        # print()

    def set_quality(self, quality):
        self.__quality = quality

    @staticmethod
    def get_movie_class(movie_link):
        selector = '#mainLoad > div:nth-child(1) > div.full_movie.table.full.mgb > div:nth-child(2) > ' \
                   'table > tbody > tr:nth-child(3) > td:nth-child(2)'

        req = request('GET', movie_link)
        bs = BeautifulSoup(req.text, features='html.parser')

        class_ = bs.select_one(selector).find('a').text.strip()
        class_ = f'{class_} {bs.select_one(selector).text.strip(".")}'

        return class_

    @staticmethod
    def get_movie_rating(movie_link):
        selector = '#mainLoad > div:nth-child(1) > div.full_movie.table.full.mgb > div:nth-child(2) > ' \
                   'table > tbody > tr:nth-child(5) > td:nth-child(2) > strong > span'

        req = request('GET', movie_link)
        bs = BeautifulSoup(req.text, features='html.parser')

        rating = bs.select_one(selector)
        rating = str(rating.text).strip()

        return f'{rating}/10'

    @staticmethod
    def get_movie_types(movie_link):
        selector = '#mainLoad > div:nth-child(1) > div.full_movie.table.full.mgb > div:nth-child(2) > table > tbody > tr:nth-child(4) > td:nth-child(2)'

        req = request('GET', movie_link)
        bs = BeautifulSoup(req.text, features='html.parser')

        types = bs.select_one(selector).find('a')
        # types = types.find_elements_by_tag_name('a')

        types = ' | '.join([t.text.strip() for t in types])

        return types

    @staticmethod
    def get_movie_story(movie_link):
        selector = '#mainLoad > div:nth-child(1) > div:nth-child(5) > div:nth-child(2)'

        req = request('GET', movie_link)
        bs = BeautifulSoup(req.text, features='html.parser')

        story = bs.select_one(selector)
        story = str(story.text).strip()

        return story

    @staticmethod
    def get_movie_pic(movie_link):
        selector = '#mainLoad > div:nth-child(1) > div.full_movie.table.full.mgb > div.movie_cover.mgb.tam.td.vat.pdl > div > a > img'

        req = request('GET', movie_link)
        bs = BeautifulSoup(req.text, features='html.parser')

        img = bs.select_one(selector)

        src_attr = img.attrs.get('src')

        # print(f'pic src_attr is {src_attr}')

        pic_name = src_attr.split('/')[-1]
        save_path = os.path.join(os.getcwd().split('/EgyBest')[0], 'media', pic_name)

        # print(f'pic saved at {save_path}')

        import requests

        with open(save_path, 'wb') as f:
            for chunk in requests.get(src_attr, stream=True).iter_content():
                if chunk:
                    f.write(chunk)

        # return save path
        return save_path

    @staticmethod
    def get_movie_trailer(movie_link):
        selector = '#yt_trailer > div.play.p.api'

        req = request('GET', movie_link)
        bs = BeautifulSoup(req.text, features='html.parser')

        video = bs.select_one(selector)
        yt_id = str(video.attrs.get('url')).split('/')[-1].split('?')[0]

        url = f'https://www.youtube.com/watch?v={yt_id}'
        return url

    def choose_the_movies(self):
        # check if there is one result, so that's the one. Download it
        if len(self._results) == 1:
            self._choices.append(self._results[0][1].get_attribute('href'))
            return True

        if len(self._results) == 0:
            print('\r\t *** No results found! ***')
            self._driver.quit()
            sys.exit(0)

        self.__movies_choices = [i for i, _ in self._titles]  # get a list of the IDs of results
        for _, y in self._titles:
            match = re.search(r'(\d{4})[^p]', y)
            if match:
                self.years.append(match.group())

        """ Prompt to the user to choose """
        i = 1
        print('\r ==> Choose one of the above (type the number of your choice) (q/quit to stop)')
        print('\r\t Choice (all is to choose all results), (all- is to choose all results except some names)')
        choice = input(f'\t\t{i} # ')

        while choice not in ('q', 'quit'):
            # wrong input
            while choice not in self.__movies_choices:
                # print(f'\rchoice is: {choice} *** {choice in self.__movies_choices}, {self.__movies_choices}')
                print('\r\t\t*** Please choose one of the list above (quit/q to stop) ***')
                choice = input(f'\t\t{i} # ')
            # terminate
            if choice in ('quit', 'q'):
                break

            # choice is all
            if choice == len(self._titles) - 1:
                self.choose_aLl()
                break

            # choice is all-
            elif choice == len(self._titles):
                self.choose_aLl_()

            else:
                if choice in self.__movies_choices:
                    # print(f"choice is {choice}")
                    # print(self._choices)
                    self._choices.append(
                        list(filter(lambda res: res[0] == str(int(choice)), self._results))[0][0])

            i += 1
            choice = input(f'\t\t{i} # ')
        print()
        self.get_links()

    def choose_aLl(self):
        self._choices = [res.get_attribute('href') for _, res in self._results]

    def choose_aLl_(self):
        j = 1
        all_but = []

        choice = input(
            f'\t\t\t\t* Enter the exception number from list above (make sure you type a number)\n\t\t\t\t{j} # ').strip()
        while choice not in ('quit', 'q'):
            # wrong input
            while choice not in self.__movies_choices or choice in ('quit', 'q'):
                choice = input(f'\t\t*** Please Enter the exception number from list above ***\n\t\t\t\t{j} # ').strip()

            # terminate
            if choice in ('quit', 'q'):
                break

            all_but.append(choice)
            j += 1

            choice = input(f'\t\t\t\t{j} # ').strip()

        self._choices = list(map(lambda res: res.get_attribute('href'),
                                 list(filter(
                                     lambda res: res.find_element_by_class_name('title').text.strip() not in all_but,
                                     [res for _, res in self._results]))))

    def get_links(self):
        choices = [int(i) for i in self._choices]
        self._choices.clear()
        for i, res in self._results:
            for choice in choices:
                # print(f'\ri = {i} ({type(i)}) | {choice} ({type(choice)})')
                if choice == int(i):
                    self._choices.append(res.get_attribute('href'))
                    break
