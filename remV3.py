import csv
import os
from urllib.request import Request, urlopen
from PIL import Image
from rembg import remove, new_session
import ssl

session = new_session()

#############################################CONFIG###############################################################

doc = r"ToDo\new.csv"  # Путь или название .csv документа
save_path = r"ToDo"  # Папка, куда сохраняем обработанные изо

err_doc = r'errors.csv'
err = False  # Ставим в True если обрабатываем ошибочный файл(который создал сам скрипт) НЕДОРАБОТАНО!!!

##################################################################################################################

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE


def queue_handler(image_urls, output_path, name):
    counter = 1
    for image_url in image_urls:
        if image_url != '':
            if not err:
                output_filename = f"{name}_{image_urls.index(image_url) + 1}.webp"  # Для обработки основного файла
            else:
                output_filename = f"{name}.webp"  # Для обработки ошибочного файла
            if output_filename not in os.listdir(output_path):
                output_filename = os.path.join(output_path, output_filename)
                image_url, repeat = prepare_url(image_url)
                removebg(image_url, output_filename, name, counter, repeat)
            else:
                print(f'{output_filename} пропущен')


def prepare_url(image_url):
    repeat = 0
    if ',' in image_url:
        image_url = image_url.replace(',', '')
    if '"' in image_url:
        image_url = image_url.replace('"', '')
    if "'" in image_url:
        image_url = image_url.replace("'", '')
    if 'xn--80acmfijjefoglo2a.xn--90ais/assets' in image_url:
        print('ПОВТОРКА!!!!!!!!!!!')
        repeat = 1
    return image_url, repeat


def removebg(image_url, output_filename, name, counter, repeat):
    req = Request(url=image_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urlopen(req, context=context) as f:
            image = Image.open(f)
        image = image.convert('RGBA')
        if repeat == 0:
            image = remove(image)
        image.save(f'{output_filename}', 'WEBP', optimize=True)
        if not err:
            print(f"{name}_{counter}")
        else:
            print(f"{name}")
        counter += 1
    except:
        if not err:
            print(f'ОШИБКА!!! PIC:{name}_{counter}')
            with open('errors.csv', "a", newline='') as f:
                writer = csv.writer(f)
                writer.writerow([f'{name}_{counter}', image_url])
            counter += 1
        else:
            print(f'ОШИБКА!!! PIC:{name}')


def main():
    if err:
        scv = err_doc
    else:
        scv = doc
    with open(scv, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        # next(reader)  # Кидаем в коммент в случае отсутствия строки описания
        tasks = []
        for row in reader:
            if row[0] != '':
                name = row[0]
                image_urls = row[1:]
                queue_handler(image_urls, save_path, name)


if __name__ == "__main__":
    main()
