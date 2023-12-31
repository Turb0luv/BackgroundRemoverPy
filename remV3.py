import csv
import multiprocessing
import os
import time
from urllib.request import Request, urlopen
from PIL import Image
from rembg import remove, new_session
import ssl

session = new_session()

#############################################CONFIG###############################################################

threads = 2  # Кол-во потоков (АККУРАТНО!!!) (Протестировано 2 ядра/4 потока 2,3ГГц(100%), 8GB RAM(70-90%))
doc = r"To-Do\mk.csv"  # Путь или название .csv документа
save_path = r"To-Do"  # Папка, куда сохраняем обработанные изо
err = False  # Ставим в True если обрабатываем ошибочный файл(который создал сам скрипт) НЕДОРАБОТАНО!!!


# Если хотим работать в однопотоке, комментим tasks.append и threader в мэйне, раскомменчиваем remove_background_multi
# В этом случае в консоль будут выводиться только названия обработанных файлов и ошибки
##################################################################################################################

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

def remove_background_multi(image_urls, output_path, name):
    counter = 1
    if err:
        output_filename = f"{name}.webp"  # Для обработки ошибочного файла
        for image_url in image_urls:
            if output_filename not in os.listdir(output_path):
                output_filename = os.path.join(output_path, output_filename)
                # if ',' in image_url:
                #     image_url = image_url.replace(',', '')
                # if '"' in image_url:
                #     image_url = image_url.replace('"', '')
                if image_url != '':
                    req = Request(url=image_url, headers={'User-Agent': 'Mozilla/5.0'})
                    # try:
                    with urlopen(req, context=context) as f:
                        image = Image.open(f)
                    image = image.convert('RGBA')
                    image = remove(image)
                    image.save(f'{output_filename}', 'WEBP', optimize=True)
                    print(f"{name}")
                    # except:
                    #     print(f'ОШИБКА!!! PIC:{name}')
            else:
                print(f'{output_filename} пропущен')
    if not err:
        for image_url in image_urls:
            output_filename = f"{name}_{image_urls.index(image_url) + 1}.webp"  # Для обработки основного файла
            if output_filename not in os.listdir(output_path):
                output_filename = os.path.join(output_path, output_filename)
                if ',' in image_url:
                    image_url = image_url.replace(',', '')
                if '"' in image_url:
                    image_url = image_url.replace('"', '')
                if image_url != '':
                    req = Request(url=image_url, headers={'User-Agent': 'Mozilla/5.0'})
                    try:
                        with urlopen(req, context=context) as f:
                            image = Image.open(f)
                        image = image.convert('RGBA')
                        image = remove(image)
                        image.save(f'{output_filename}', 'WEBP', optimize=True)
                        print(f"{name}_{counter}")
                        counter += 1
                    except:
                        print(f'ОШИБКА!!! PIC:{name}_{counter}')
                        with open('errors.csv', "a", newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow([f'{name}_{counter}', image_url])
                        counter += 1
            else:
                print(f'{output_filename} пропущен')


def main():
    if err:
        scv = 'errors.csv'
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
                #tasks.append((image_urls, save_path, name))  # Запуск в многопотоке(коммент, если работаем в однопотоке)
                remove_background_multi(image_urls, save_path, name) # Запуск в однопотоке
    #threader(tasks)  # Кидаем в коммент если работаем в однопотоке


def threader(tasks):
    timer = []
    counter = 1
    print(f'{len(tasks)} задач на {round(len(tasks) / threads)} заходов')
    for i in range(0, len(tasks), threads):
        processes = [multiprocessing.Process(target=remove_background_multi, args=task) for task in
                     tasks[i:i + threads]]
        start = time.time()
        print(f'{counter} заход из {round(len(tasks) / threads)} ({round((counter * 100) / (len(tasks) / threads))}%)')
        for p in processes:
            p.start()
        for p in processes:
            p.join()
        print(f'Время {counter}-го захода: {round(time.time() - start)} сек.')
        timer.append(round(time.time() - start))
        counter += 1
    print(f'Общее время: ~{round(sum(timer) / 60)} мин.')
    print(f'Среднее время захода: {round(sum(timer) / len(timer))} сек.')


if __name__ == "__main__":
    main()
