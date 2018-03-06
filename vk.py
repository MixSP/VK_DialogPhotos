# requests==2.18.4

import requests 
from os import mkdir
from time import sleep
from multiprocessing import Pool 


TOKEN = 'токен пользователя'
FRIEND_ID = 'id друга'


def get_request(offset):
    r = requests.get('https://api.vk.com/method/messages.getHistoryAttachments', params={'access_token': TOKEN,
                                                                                         'peer_id': FRIEND_ID,
                                                                                         'media_type': 'photo',
                                                                                         'start_from': offset,
                                                                                         'count': 200, 
                                                                                         'photo_sizes': True})
    
    return r.json()


def get_largest_size(photo):
    sizes = photo['sizes']

    return sorted(sizes, key=lambda d: d['width'])[-1]['src']


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
        
            length = len(r['response'])
            offset = r['response']['next_from']

            for number in range(1, length - 1):
                photo = r['response'][str(number)]['photo']
                urls.add(get_largest_size(photo))

            if length < 202:
                break

            sleep(0.35)

        print(len(urls), 'photos')
        mkdir(FRIEND_ID)

        with Pool(20) as p:
            p.map(download_photo, urls)

    except FileExistsError:
        with Pool(20) as p:
            p.map(download_photo, urls)
    except KeyError:
        print('Error!', r['error']['error_msg'])
    except TypeError:
        print('Error! You don\'t have any photos with this user.')


if __name__ == '__main__':
    main()
