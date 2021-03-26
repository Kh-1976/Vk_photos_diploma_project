import requests
import json
import os
from pprint import pprint

# Аккаунт https://vk.com/begemot_korovin
# token_vk = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
# user_id_vk = '552934290'

token_vk = input('Введите token vk: ')
user_id_vk = input('Введите id vk пользователя: ')
token_ya = input('Введите token с Полигона Яндекс.Диска: ')


class YaUploader:

    def __init__(self, token_ya):
        self.token = token_ya
        self.folder = input('Введите название папки: ')

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def new_folder(self):
        new_folder_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': self.folder}
        response = requests.put(new_folder_url, headers=self.get_headers(), params=params)
        if response.status_code == 201:
            print(f'Папка {self.folder} создана')
        else:
            print(f'Папка {self.folder} уже существует')

    def upload_photo(self, link):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        for key, val in link.items():
            params = {'path': f'{self.folder}/{key}', 'url': val}
            response = requests.post(upload_url, headers=self.get_headers(), params=params)
            if response.status_code == 202:
                print(f'{key} - Файл добавлен')


class VkUserPhotos:
    url = 'https://api.vk.com/method/photos.get'

    def __init__(self, owner_id_vk):
        self.params = {
            'owner_id': owner_id_vk,
            'access_token': token_vk,
            'v': '5.52',
            'album_id': 'profile',
            'extended': 1
        }

    def photos(self):
        res = requests.get(self.url, params=self.params)
        lst_photos = res.json()['response']['items']
        return lst_photos

    def max_resolution(self, dict_i):
        maximum = 0
        for i in dict_i:
            if i[:5] == 'photo' and int(i[6:]) > maximum:
                maximum = int(i[6:])
        return maximum

    def search_photo(self, lst_photos):
        lst_result, no_repeat, dict_links = [], [], {}
        for dict_i in lst_photos:
            if str(dict_i['likes']['count']) not in no_repeat:
                lst_result.append({'file_name': str(dict_i['likes']['count']) + '.jpg',
                                   'size': str(self.max_resolution(dict_i))})
                no_repeat.append(str(dict_i['likes']['count']))
                dict_links[str(dict_i['likes']['count']) + '.jpg'] = dict_i[f'photo_{str(self.max_resolution(dict_i))}']
            else:
                lst_result.append({'file_name': str(dict_i['likes']['count']) + '_' + str(dict_i['date']) + '.jpg',
                                   'size': str(self.max_resolution(dict_i))})  # если количество лайков одинаково,
                # то к имени добавится дата загрузки, в формате Unix time.
                dict_links[str(dict_i['likes']['count']) + '_' + str(dict_i['date']) + '.jpg'] = dict_i[
                    f'photo_{str(self.max_resolution(dict_i))}']

        with open(os.path.join(os.getcwd(), 'log.json'), 'w', encoding="utf-8") as f:
            json.dump(lst_result, f)

        return dict_links


vk = VkUserPhotos(user_id_vk)
ya = YaUploader(token_ya)

print(ya.new_folder())
print(ya.upload_photo(vk.search_photo(vk.photos())))

with open(os.path.join(os.getcwd(), 'log.json'), 'r', encoding="utf-8") as f:
    data = json.load(f)

print('json-файл:')
pprint(data)
