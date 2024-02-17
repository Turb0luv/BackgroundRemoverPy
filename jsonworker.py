import json
import os
import re

################################CONFIG##########################################
# Создание ссылок на файлы
check_path = r"ToDo"  # Папка с файлами(изо)
sample = r"https://xn--80acmfijjefoglo2a.xn--90ais/assets/"  # Сэмпл ссылка
dot = r'.webp'  # Расширение файла
##################################################################################
json_file = r"final2.json"  # Исходный файл
exit_json = r'final2-ready.json'  # Готовый файл/Исходный для создания незаконченными изо csv

color_file = r"colors.json"  # Файл с цветами
exit_csv = r'unfilled.csv'  # Готовый файл с незаконченными изо csv


def url_id_maker():
    files = os.listdir(check_path)
    urls = []
    mk = []
    ids = []
    for file in files:
        urls.append(f'{sample}{file}')
        mk.append(file[:5])
    [ids.append(x) for x in mk if x not in ids]
    return ids, urls


def make_dct():
    dct = {}
    ids, urls = url_id_maker()
    for id in ids:
        mt = re.findall(r'{0}\d'.format(f'{sample}{id}_'), str(urls))
        for i in range(len(mt)):
            mt[i] = f'{mt[i]}{dot}'
        kv = {id: mt}
        dct.update(kv)
    return dct


def make_json():
    with open(json_file, 'r', encoding="utf-8") as f:
        data = json.load(f)
    fold = make_dct()
    for fid, urls in fold.items():
        for i in range(len(data)):
            if data[i]['id'] == int(fid):
                print(f'{fid}')
                data[i]['imgUrls'] = urls
    with open(exit_json, 'x', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print('Обработанный JSON готов')


def make_csv():
    with open(exit_json, 'r', encoding="utf-8") as f:
        data = json.load(f)
    # with open(color_file, 'r', encoding="utf-8") as f:  #Работа с цветами
    #     clrs = json.load(f)
    # colors = {}
    # for i in clrs['data']:
    #     cl = {i: clrs["data"][i]["name"]}
    #     colors.update(cl)
    lst = []
    for i in range(len(data)):
        if not data[i]['imgUrls']:
            idx = data[i]['id']
            brand = data[i]['brand'] if 'brand' in data[i] else 'Бренд не указан'
            name = data[i]['name']
            description = data[i]['description'] if 'description' in data[i] else ''
            # color = colors.get(f'{i}') #Работа с цветами
            lst.append(f'{idx},"{brand}","{name}",{description}') #Работа с цветами(добавить после description перем. colors)
    with open(exit_csv, 'x', encoding="utf-8") as f:
        for i in lst:
            f.write(f'{str(i)}\n')
    print('CSV создан')


def main():
    print('Действие')
    print('1. Обработка JSON')
    print('2. Создание csv из JSON(пустые urlID)')
    print('3. Всё сразу(JSON, csv)')
    print('!!!Убедитесь в правильности указанных данных в конфиге!!!')
    sw = int(input())
    if sw == 1:
        make_json()
    elif sw == 2:
        make_csv()
    elif sw == 3:
        make_json()
        make_csv()


if __name__ == "__main__":
    main()
