import time
import urllib2
import requests
import telepot
from telepot.loop import MessageLoop
from configuration import BotData


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print('Mensaje: ' + str(chat_id) + ' ' + content_type + ' ' + msg['text'])

    if msg['text'] == "/top":
        bot.sendMessage(chat_id,
                        "This is the top 10 songs: \n\n" + get_top_songs(BotData.COUNTRY))
    elif msg['text'] == "/start":
        bot.sendMessage(chat_id, "Wellcome to the music bot!")
        bot.sendMessage(chat_id, "Send me part of a song lyrics to know the name and get the Youtube video!")
    else:
        author, song = get_song_from_lyrics(msg['text'], bot, chat_id)
        bot.sendMessage(chat_id, "The song is " + song)
        bot.sendMessage(chat_id, "Song on Youtube: \n" + get_youtube_video(song + " " + author))


bot = telepot.Bot(BotData.TOKEN)
MessageLoop(bot, {'chat': on_chat_message}).run_as_thread()
print('Listening ...')


def split(author, song):
    authors = author.split('-')
    songs = song.split('-')
    cont1 = 0
    cont2 = 0
    author_string = ""
    song_string = ""
    while cont1 < len(authors):
        author_string += authors[cont1] + " "
        cont1 = cont1 + 1
    while cont2 < len(songs):
        song_string += songs[cont2] + " "
        cont2 = cont2 + 1
    return author_string, song_string


def get_song_from_lyrics(song, bot, chat_id):
    try:
        lyrics = urllib2.quote(song.encode('utf-8'))
        json = requests.get(BotData.URL + lyrics + BotData.URL_END)
        song_name = json.json()['message']['body']['track_list'][0]['track']['track_name']
        artist_name = json.json()['message']['body']['track_list'][0]['track']['artist_name']
    except IndexError:
        bot.sendMessage(chat_id, "We cant find any match, write more song lyrics next time")
    return artist_name, song_name


def get_top_songs(country):
    json = requests.get(BotData.URL_DEFAULT + "chart.tracks.get?page=1&page_size=10&country=" + country
                        + BotData.URL_END)
    cont = 0
    tops = ""
    while cont < 10:
        author, song = split(json.json()['message']['body']['track_list'][cont]['track']['artist_name'],
                             json.json()['message']['body']['track_list'][cont]['track']['track_name'])
        tops = tops + "Top " + str(cont + 1) + ": " + song + " from " + author + "\n\n"
        cont = cont + 1
    return tops


def get_youtube_video(song):
    result = "+".join(song.split()) + '+'
    json = requests.get('https://www.youtube.com/results?search_query=' + result.lower())
    point = json.text.find('/watch?v=')
    return 'https://www.youtube.com' + json.text[point:point + 20]


while 1:
    time.sleep(5)


