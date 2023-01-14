import requests
from dotenv import load_dotenv
from os import environ
from pathlib import Path
from random import randint
from sys import exit



def main():

    load_dotenv()
    vk_access_token = environ['VK_ACCESS_TOKEN']
    vk_group_id = environ['VK_GROUP_ID']
    actual_version_api = '5.131'
    file_name = 'image.png'
    try:
        comics_caption = download_random_comics()
        try:
            post_wall_photo(vk_access_token, vk_group_id, actual_version_api, file_name, comics_caption)
        except requests.exceptions.HTTPError:
            print('Ошибка опубликования комикса')
    except requests.exceptions.HTTPError:
        print('Ошибка загрузки комикса')


def download_random_comics():

    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    total_comics = response.json()['num']
    comics_number = randint(1, total_comics)
    url = f'https://xkcd.com/{comics_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()  
    comics_link = response.json()['img']
    comics_caption = response.json()['alt']
    response = requests.get(comics_link)
    response.raise_for_status()
    file_name = Path().cwd() / 'image.png'    
    with open(file_name, 'wb') as file:
        file.write(response.content)

    return comics_caption 


def get_upload_vk_server_url(vk_access_token, vk_group_id, version_api, file_name):

    
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    payloads = {
        'access_token': vk_access_token, 
        'v': version_api,
        'group_id': vk_group_id
    }
    response = requests.get(url, params=payloads)
    response.raise_for_status()    
    response = response.json()    
    if 'error' in response:
        print_error_msg(response, file_name)            
    else:
        return response['response']['upload_url']
        

def print_error_msg(response, file_name):

    Path(file_name).unlink() 
    print('Ошибка. Описание:')
    print(response['error']['error_msg'])
    exit() 


def upload_wall_photos(vk_access_token, vk_group_id, version_api, file_name):
    
    with open(file_name, 'rb') as file:
        url = get_upload_vk_server_url(vk_access_token, vk_group_id, version_api, file_name)
        files = {
            'photo': file
        }
        response = requests.post(url, files=files)
    response.raise_for_status()
    response = response.json()
    if 'error' in response:
        print_error_msg(response, file_name)
    elif response['photo'] == '[]':
        print('Комикс не загружен в группу')
        exit()
    else:
        return response
                 

def save_wall_photo(vk_access_token, vk_group_id,  version_api, file_name):

    url = 'https://api.vk.com/method/photos.saveWallPhoto'  
    
    response_upload_photo = upload_wall_photos(vk_access_token, vk_group_id, version_api, file_name)    
    payloads = {
        'access_token': vk_access_token,         
        'group_id': vk_group_id,
        'photo': response_upload_photo['photo'],
        'server': response_upload_photo['server'],
        'v': version_api,
        'hash': response_upload_photo['hash']
    }
    response = requests.post(url, params=payloads)
    response.raise_for_status()
    response = response.json()    
    if 'error' in response:
        print_error_msg(response, file_name)
    else:
        return response['response']


def post_wall_photo(vk_access_token, vk_group_id, version_api, file_name, caption):

    url = 'https://api.vk.com/method/wall.post'  
    
    response_save_wall_photo = save_wall_photo(vk_access_token, vk_group_id, version_api, file_name)
    owner_id = response_save_wall_photo[0]['owner_id']
    media_id = response_save_wall_photo[0]['id']
    payloads = {
        'access_token': vk_access_token,         
        'owner_id': -int(vk_group_id),
        'from_group': 1,
        'message': caption,
        'attachments': f'photo{owner_id}_{media_id}',        
        'v': version_api,        
    }
    response = requests.post(url, params=payloads)
    response.raise_for_status()
    response = response.json()
    if 'error' in response:
        print_error_msg(response, file_name)
    Path(file_name).unlink()
         


if __name__ == "__main__":
    main()