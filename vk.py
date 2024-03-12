import requests 
from os import mkdir
from time import sleep
from multiprocessing import Pool 
import argparse
from sys import exit
from math import inf

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--token", dest = "TOKEN", default = "", help="VK API acess token")
parser.add_argument("-id", "--friend_id", dest = "FRIEND_ID", default = "", help="ID of a vk friend or dialog id")
parser.add_argument("-n", "--numofphotos", dest = "NUMOFPHOTOS", default = "", help="A number of photos to download (from last to upper ones)")

args = parser.parse_args()
if (args.TOKEN == "") or (args.FRIEND_ID == ""):
    exit("Error! No input. Use -h flag for help")

TOKEN = args.TOKEN
FRIEND_ID = args.FRIEND_ID
NUMOFPHOTOS = args.NUMOFPHOTOS
if NUMOFPHOTOS != "":
    try:
        NUMOFPHOTOS = int(NUMOFPHOTOS)
    except ValueError:
        print('Error! Number of photos passed is not integer number')

def get_request(offset):
    r = requests.get('https://api.vk.com/method/messages.getHistoryAttachments', params={'access_token': TOKEN,
                                                                                         'peer_id': FRIEND_ID,
                                                                                         'media_type': 'photo',
                                                                                         'start_from': offset,
                                                                                         'count': 200,
                                                                                         'photo_sizes': True,
                                                                                         'v': 5.131})
    return r.json()


def get_largest_size(photo):
    sizes = photo['sizes']

    return sorted(sizes, key=lambda d: d['width'])[-1]['url']


def download_photo(url):
    r = requests.get(url, stream=True)
    filename = url.split('/')[-1]

    with open(FRIEND_ID + '/' + filename, 'bw') as file:
        for chunk in r.iter_content(4096):
            file.write(chunk)


def main():
    offset = 0
    urls = set()
    
    try:
        while True:
            r = get_request(offset)
            
            length = len(r['response']['items'])
            offset = r['response']['next_from']
 
            if NUMOFPHOTOS == "":
                for number in range(length):
                    photo = r['response']['items'][number]['attachment']['photo']
                    urls.add(get_largest_size(photo))

                if length < 200:
                    break
            
                sleep(0.35)
            else:
                if length < NUMOFPHOTOS:
                    exit('Error! This dialog doesn\'t have that much photos.')
                for number in range(NUMOFPHOTOS):
                    photo = r['response']['items'][number]['attachment']['photo']
                    urls.add(get_largest_size(photo))
                break

                sleep(0.35)

        print(len(urls), 'photos')
        mkdir(FRIEND_ID)
        
    except FileExistsError:
        with Pool(20) as p:
            p.map(download_photo, urls)
    except TypeError:
        print('Error! You don\'t have any photos with this user.')
    except KeyError:
        print(r['error']['error_msg'])


    with Pool(20) as p:
        p.map(download_photo, urls)


if __name__ == '__main__':
    main()
