from telethon import TelegramClient, Button, events
from telethon.tl.custom import messagebutton

from collections import defaultdict
from EgyBest.egybest import *

import os


API_ID = ####
API_HASH = ''

MEDIA_URL = os.path.join(os.getcwd(), 'media')
if not os.path.isdir(MEDIA_URL):
    os.mkdir(MEDIA_URL)

kind, name, quality, season, episodes, movie_results, movies = None, None, None, None, [], {}, []
series, movie = None, None
last_movie_option = None

USER_LOCATION = defaultdict(list)

client = TelegramClient('bot session', API_ID, API_HASH)
client.start(bot_token='1891279302:AAEmbhZ4dGAXYskYcfw8Aop-RksiFxUKyQw')
# client.start()
print('bot is running!')

"""
show the start message and welcome the User
and give him a choice to choose (Movie | Series)
"""


@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    global kind
    kind = None

    string = 'هل تريد مسلسل أم فيلم؟'

    await event.client.send_message(event.chat_id, string,
                                    buttons=[Button.text('فيلم', resize=True, single_use=True),
                                             Button.text('مسلسل', resize=True, single_use=True)])

    USER_LOCATION[event.sender_id].append(start_handler)
    raise events.StopPropagation


"""
store the user preferred kind to download
and prompt him his choice's name (Movie | Series)
just once when kind is None
"""


@client.on(events.NewMessage(pattern=r'مسلسل|فيلم', func=lambda e: kind is None))
async def kind_handler(event):
    global kind, name
    name = None

    if event.raw_text != 'رجوع':
        kind = event.raw_text

    string = f'اكتب اسم ال{kind}'

    await event.client.send_message(event.chat_id, string,
                                    buttons=[
                                        [Button.text('رجوع', resize=True, single_use=True)],
                                        [Button.text('إلفاء', resize=True, single_use=True)]
                                    ])

    USER_LOCATION[event.sender_id].append(kind_handler)
    raise events.StopPropagation


"""
store the name
and prompt the user to choose the season if the kind == مسلسل

in this function we also prompt the user to choose an option to what to do with movie
e.g.
1. معلومات عن الفيلم (التقييم، القصة، نوع الفيلم)
2. تنزيل صورة الفيلم
3. مشاهدة التريلر
4. روابط التنزيل
"""


@client.on(events.NewMessage(pattern=r'.+', func=lambda e: kind and name is None and season is None and quality is None and
                             e.raw_text not in ('رجوع', 'إلغاء', 'موافق', 'جميع الحلقات')))
async def name_handler(event):
    global series, season, name, movie, movie_results
    season = None

    if event.raw_text != 'رجوع':
        name = event.raw_text.lower()

    if kind == 'مسلسل':
        searching_msg = await event.respond('جاري البحث عن المسلسل ...')
        series = Series(name)
        await searching_msg.delete()

        # await event.client.send_message(event.chat_id, string, buttons=option_buttons)

        string = 'اختر الموسم'

        seasons_buttons = [
            [Button.text(f'{i}', resize=True, single_use=True)] for i in range(1, series.get_seasons_number() + 1)
        ]

        btns = [
            [Button.text('رجوع', resize=True, single_use=True)],
            [Button.text('إلفاء', resize=True, single_use=True)]
        ]

        btns.extend(seasons_buttons)

        await event.client.send_message(event.chat_id, string, buttons=btns)

    elif kind == 'فيلم':
        searching_msg = await event.respond('جاري البحث عن الفيلم ...')
        movie = Movie(name)
        await searching_msg.delete()

        for i, res in movie.get_search_results():
            movie_results[res.find_element_by_css_selector('span.title').text] = res.get_attribute('href')

        option_buttons = [
            [Button.text('معلومات (التصنيف، النوع، التقييم، القصة)', resize=True)],
            [Button.text('تنزيل الصورة', resize=True)],
            [Button.text('مشاهدة التريلر', resize=True)],
            [Button.text('روابط التنزيل', resize=True)],
            [Button.text('رجوع', resize=True)]
        ]

        string = 'اختر ما تريد'

        await event.client.send_message(event.chat_id, string, buttons=option_buttons)

    USER_LOCATION[event.sender_id].append(season_handler)
    raise events.StopPropagation


@client.on(events.NewMessage(func=lambda e: e.raw_text in movie_results.keys()))
async def movie_handler(event):
    global movie, last_movie_option

    if last_movie_option is not None:
        last_movie_option = None

        if last_movie_option == 'التصنيف':
            await event.respond(movie.get_movie_class(movie_results[event.raw_text.strip()]))

        elif last_movie_option == 'التقييم':
            await event.respond(movie.get_movie_rating(movie_results[event.raw_text.strip()]))

        elif last_movie_option == 'النوع':
            await event.respond(movie.get_movie_types(movie_results[event.raw_text.strip()]))

        elif last_movie_option == 'القصة':
            await event.respond(movie.get_movie_sotry(movie_results[event.raw_text.strip()]))

        elif last_movie_option == 'تنزيل الصورة':
            file_name = movie.get_pic_saved_path(movie_results[event.raw_text.strip()])
            await event.client.send_file(event.chat_id, file=file_name)
            os.remove(file_name)

        elif last_movie_option == 'مشاهدة التريلر':
            await event.respond(movie.get_trailer_link(movie_results[event.raw_text.strip()]))

        elif last_movie_option == 'روابط التنزيل':
            await choose_movie(event)

    else:
        movies.append(event.raw_text.strip())

    raise events.StopPropagation


# @client.on(events.NewMessage(pattern=r'\d{1,2}', func=lambda e: 1 <= len(e.raw_text) <= 2 and kind == 'مسلسل' and name and season is None and
#                             len(episodes) == 0))

"""
store the season if kind == 'مسلسل'
and prompt him to choose episodes
"""


@client.on(events.NewMessage(pattern=r'\d{1,2}', func=lambda e: 1 <= len(e.raw_text) <= 2 and kind == 'مسلسل' and quality is None))
async def season_handler(event):
    global season, episodes

    # user's chosen the season
    if season is None:
        if event.raw_text != 'رجوع':
            season = event.raw_text
            moving_to_season_msg = await event.respond(f'جاري الانتقال إلى الموسم {season}')
            series.set_season(season)
            await moving_to_season_msg.delete()

            option_buttons = [
                # [Button.text('معلومات (التصنيف، النوع، التقييم، القصة)', resize=True)],
                [Button.text('القصة', resize=True)],
                [Button.text('التقييم', resize=True)],
                [Button.text('التصنيف', resize=True)],
                [Button.text('النوع', resize=True)],
                [Button.text('تنزيل الصورة', resize=True)],
                [Button.text('مشاهدة التريلر', resize=True)],
                [Button.text('روابط التنزيل', resize=True)],
                [Button.text('رجوع', resize=True)]
            ]

            string = 'اختر ما تريد'

            await event.client.send_message(event.chat_id, string, buttons=option_buttons)

    else:  # user's chosen an episode
        if str(event.text).isnumeric():
            episodes.append(int(event.raw_text.strip()))

        episodes_choice_buttons = [
            [Button.text('موافق', resize=True)],
            [Button.text('جميع الحلقات', resize=True)],
            [Button.text('إلفاء اختيار الحلقة السابقة', resize=True)]
        ]

        episodes_btns = [
            [Button.text(f'{i}', resize=True)] for i in range(1, series.get_episodes_number() + 1)
        ]

        episodes_choice_buttons.extend(episodes_btns)

        string = 'اختر حلقة\nعند الانتهاء اضغط موافق'

        await event.client.send_message(event.chat_id, string, buttons=episodes_choice_buttons)

    USER_LOCATION[event.sender_id].append(season_handler)
    raise events.StopPropagation


@client.on(events.NewMessage(pattern='جميع الحلقات', func=lambda e: kind == 'مسلسل' and season and quality is None))
async def all_episodes_handler(event):
    global season, episodes

    if event.raw_text != 'رجوع':
        episodes.append('all')

    USER_LOCATION[event.sender_id].append(episodes_handler)
    raise events.StopPropagation

"""
after prompting the user to choose the season and store the quality
we prompt him to choose the episodes and store the season from previous event
"""


@client.on(events.NewMessage(pattern='موافق', func=lambda e: ((kind == 'مسلسل' and season and quality is None) or (kind == 'فيلم')) and name))
async def episodes_handler(event):
    global kind, name, quality, season, episodes

    qualities = [
        [Button.text('1080p', resize=True, single_use=True)],
        [Button.text('720p', resize=True, single_use=True)],
        [Button.text('480p', resize=True, single_use=True)],
        [Button.text('360p', resize=True, single_use=True)],

        [Button.text('رجوع', resize=True, single_use=True)],
        [Button.text('إلفاء', resize=True, single_use=True)]
    ]

    string = 'اختر الدقة'

    if kind == 'مسلسل':  # kind is series
        if name:  # name is not None
            if season:  # season is not None
                if len(episodes):  # and there are episodes chosen
                    eps = set(episodes)
                    episodes = sorted(list(eps))
                    series.set_episodes(episodes)

                    # qualities = [
                    #     [Button.text('1080p', resize=True, single_use=True)],
                    #     [Button.text('720p', resize=True, single_use=True)],
                    #     [Button.text('480p', resize=True, single_use=True)],
                    #     [Button.text('360p', resize=True, single_use=True)],
                    #
                    #     [Button.text('رجوع', resize=True, single_use=True)],
                    #     [Button.text('إلفاء', resize=True, single_use=True)]
                    # ]
                    #
                    # string = 'اختر الدقة'
                    #
                    # await event.client.send_message(event.chat_id, string, buttons=qualities)

                    # series.get_links()

    elif kind == 'فيلم':
        # qualities = [
        #     [Button.text('1080p', resize=True, single_use=True)],
        #     [Button.text('720p', resize=True, single_use=True)],
        #     [Button.text('480p', resize=True, single_use=True)],
        #     [Button.text('360p', resize=True, single_use=True)],
        #
        #     [Button.text('رجوع', resize=True, single_use=True)],
        #     [Button.text('إلفاء', resize=True, single_use=True)]
        # ]
        #
        # string = 'اختر الدقة'
        #
        # await event.client.send_message(event.chat_id, string, buttons=qualities)
        pass

    await event.client.send_message(event.chat_id, string, buttons=qualities)
    # kind, name, quality, season, episodes = None, None, None, None, []
    USER_LOCATION[event.sender_id].append(episodes_handler)
    raise events.StopPropagation


@client.on(events.NewMessage(pattern=r'\d{3,4}p', func=lambda e: ((kind == 'مسلسل' and season and len(episodes)) or kind == 'فيلم') and name and
                             quality is None))
async def quality_handler(event):
    global quality, series, movie, kind

    if event.raw_text != 'رجوع':
        quality = event.raw_text

    if kind == 'مسلسل':
        from pathlib import Path

        series.set_quality(quality)

        # fetching links
        results_msg = 'جاري إحضار الروابط...'
        results_msg = await event.respond(results_msg)
        series.get_links()
        await results_msg.delete()

        desktop = os.path.join(Path.home(), 'Desktop')
        links_file = f'{os.path.join(desktop, name.title())}.txt'
        await event.client.send_file(event.chat_id, file=links_file, force_document=True)
        os.remove(links_file)

        await cancel_handler(event)

    elif kind == 'فيلم':
        from pathlib import Path

        movie.set_quality(quality)

        # fetching links
        results_msg = 'جاري إحضار الروابط...'
        results_msg = await event.respond(results_msg)
        movie.get_links()
        await results_msg.delete()

        desktop = os.path.join(Path.home(), 'Desktop')
        links_file = f'{os.path.join(desktop, name.title())}.txt'
        await event.client.send_file(event.chat_id, file=links_file, force_document=True)
        os.remove(links_file)

        await cancel_handler(event)

    USER_LOCATION[event.sender_id].append(quality_handler)
    raise events.StopPropagation


# @client.on(events.NewMessage(func=lambda e: e.raw_text == 'معلومات (التصنيف، النوع، التقييم، القصة)' and ((series and season) or movie)))
# async def info_handler(event):
#     global series, movie
#
#     if series:
#         await event.respond(series.get_info())
#
#     elif movie:
#         await event.respond(movie.get_info())
#
#     raise events.StopPropagation

async def choose_movie(event):
    movies_btn = []
    for mv_name, _ in movie_results.items():
        movies_btn.append([Button.text(mv_name, resize=True)])
    movies_btn.append([Button.text('رجوع', resize=True)])

    string = 'اختر فيلماً'

    await event.client.send_message(event.chat_id, string, buttons=movies_btn)


@client.on(events.NewMessage(pattern='القصة', func=lambda e: series or movie))
async def story_handler(event):
    global series, movie, last_movie_option

    if series:
        await event.respond(series.get_series_story())

    elif movie:
        await choose_movie(event)

    last_movie_option = event.raw_text.strip()

    raise events.StopPropagation


@client.on(events.NewMessage(pattern='التقييم', func=lambda e: series or movie))
async def rating_handler(event):
    global series, movie, last_movie_option

    if series:
        await event.respond(series.get_series_rating())

    elif movie:
        await choose_movie(event)

    last_movie_option = event.raw_text.strip()

    raise events.StopPropagation


@client.on(events.NewMessage(pattern='التصنيف', func=lambda e: series or movie))
async def class_handler(event):
    global series, movie, last_movie_option

    if series:
        await event.respond(series.get_series_class())

    elif movie:
        await choose_movie(event)

    last_movie_option = event.raw_text.strip()

    raise events.StopPropagation


@client.on(events.NewMessage(pattern='النوع', func=lambda e: series or movie))
async def types_handler(event):
    global series, movie, last_movie_option

    if series:
        await event.respond(series.get_series_types())

    elif movie:
        await choose_movie(event)

    last_movie_option = event.raw_text.strip()

    raise events.StopPropagation


@client.on(events.NewMessage(pattern='مشاهدة التريلر', func=lambda e: (series and season) or movie))
async def trailer_handler(event):
    global series, movie, last_movie_option

    if series:
        await event.respond(series.get_trailer_link())

    elif movie:
        await choose_movie(event)

    last_movie_option = event.raw_text.strip()

    raise events.StopPropagation


@client.on(events.NewMessage(pattern='تنزيل الصورة', func=lambda e: (series and season) or movie))
async def pic_handler(event):
    global series, movie, last_movie_option

    if series:
        file_name = series.get_pic_saved_path()
        await event.client.send_file(entity=event.chat_id, file=file_name)
        os.remove(file_name)

    elif movie:
        await choose_movie(event)

    last_movie_option = event.raw_text.strip()

    raise events.StopPropagation


"""
when a user wants the download links
if his kind was a series, then he should
choose season's episodes.

if his kind was a movie, the bot should show the search results
"""


@client.on(events.NewMessage(pattern='روابط التنزيل', func=lambda e: ((series and season and len(episodes) == 0) or movie)
                             and name and quality is  None))
async def links_handler(event):
    global series, movie, last_movie_option

    # if event.raw_text == 'رجوع':
    #     episodes.append(int(event.raw_text.strip()))

    if kind == 'مسلسل':

        episodes_choice_buttons = [
            [Button.text('موافق', resize=True)],
            [Button.text('جميع الحلقات', resize=True)],
            [Button.text('إلفاء اختيار الحلقة السابقة', resize=True)]
        ]

        episodes_btns = [
            [Button.text(f'{i}', resize=True)] for i in range(1, series.get_episodes_number() + 1)
        ]

        episodes_choice_buttons.extend(episodes_btns)

        string = 'اختر حلقة\nعند الانتهاء اضغط موافق'

        await event.client.send_message(event.chat_id, string, buttons=episodes_choice_buttons)

    elif movie:
        await choose_movie(event)

    last_movie_option = event.raw_text.strip()

    USER_LOCATION[event.sender_id].append(episodes_handler)
    raise events.StopPropagation


@client.on(events.NewMessage(pattern='إلغاء', func=lambda e: ((kind == 'مسلسل' and season) or (kind == 'فيلم')) and quality and name))
async def cancel_handler(event):
    global kind, name, quality, season, episodes, movie_results, movies, last_movie_option

    kind, name, quality, season, episodes, movie_results, movies = None, None, None, None, [], {}, []
    last_movie_option = None


@client.on(events.NewMessage(pattern='رجوع'))
async def back_handler(event):
    stack = USER_LOCATION[event.sender_id]

    if not stack:
        return

    stack.pop()
    if stack:
        await stack.pop()(event)


@client.on(events.NewMessage(pattern='إلفاء اختيار الحلقة السابقة', func=lambda e: series and name and season and len(episodes)))
async def delete_last_episodes(event):
    global episodes

    episodes.pop()
    await event.client.send_message(event.chat_id, 'تم الإلغاء')
    await season_handler(event)


@client.on(events.NewMessage(pattern='إلغاء اختيار الفيلم السابق', func=lambda e: kind == 'فيلم' and movie and name))
async def delete_last_movie(event):
    global movies

    await event.client.send_message(event.chat_id, 'تم الإلغاء')
    await movie_handler(event)


# async def callback(event, string):
#     await event.respond(string)


if __name__ == '__main__':
    client.run_until_disconnected()
