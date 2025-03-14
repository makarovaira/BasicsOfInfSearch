import os
import requests
from bs4 import BeautifulSoup

# Список URL-адресов для скачивания
urls = [
    "https://habr.com/ru/articles/",
    "http://www.givc.ru",
    "http://www.culture.ru/",
    "http://fcpkultura.ru",
    "https://godliteratury.ru/main-news",
    "http://www.russianculture.ru",
    "http://kazan.muzkult.ru/contacts",
    "http://infoculture.rsl.ru/RSKD/main.htm",
    "http://rus-eu-culture.ru",
    "https://lgz.ru/",
    "http://www.inostranka.ru/",
    "https://magazines.gorky.media/",
    "http://nasledie-rus.ru",
    "http://old.russ.ru/",
    "http://int-ant.ru/about-the-project/information/",
    "http://www.archi.ru",
    "http://www.heritage-institute.ru/",
    "http://www.art-education.ru/",
    "http://smallbay.ru",
    "http://www.artprojekt.ru/",
    "https://rusmuseumvrm.ru/collections/painting/index.php?show=asc&p=0&mpage=3&ps=20",
    "http://gallerix.ru/",
    "https://gallerix.ru/album/200-Russian",
    "http://sova-art.com/main",
    "https://artchive.ru/artworks/type:graphics",
    "https://masterkrasok.ru/pictures/graphics",
    "http://www.les-gallery.ru/about/",
    "https://icr.su/",
    "http://dinu3.chat.ru/e/index.htm",
    "http://www.rychkovart.ru/",
    "http://shulgin-gallery.ru/",
    "http://www.postcard.ru",
    "http://www.riversongs.com",
    "http://www.museum.ru",
    "https://ar.culture.ru/ru",
    "https://ok.ru/group/61155207020689",
    "http://www.hermitagemuseum.org",
    "http://www.rusmuseum.ru",
    "https://theatre-museum.ru/",
    "http://yusupov-palace.ru",
    "http://www.pavlovskmuseum.ru",
    "http://www.peterhof.ru",
    "http://www.kreml.ru/",
    "http://www.openkremlin.ru",
    "https://mediashm.ru/",
    "http://www.shm.ru",
    "https://um.mos.ru/museums/",
    "http://www.arts-museum.ru/",
    "http://www.tretyakovgallery.ru",
    "http://www.mmoma.ru",
    "http://www.museum-esenin.ru",
    "http://www.museum.ru/museum/Ostankino",
    "http://museum.rsuh.ru",
    "http://museum.pereslavl.ru",
    "http://www.museum.ru/palekh",
    "http://www.ustjug.museum.ru",
    "http://www.museum.ru/museum/mscreg",
    "http://www.tsaritsyno-museum.ru",
    "http://www.museum.ru/museum/primitiv",
    "http://www.orientmuseum.ru",
    "http://www.kuskovo.ru",
    "http://portret.ru/",
    "https://www.museum-tanais.ru/",
    "http://www.theatre.ru",
    "http://www.theatreinform.ru",
    "https://www.bolshoi.ru/",
    "http://www.maly.ru",
    "https://kremlinpalace.org/",
    "http://actors.khv.ru",
    "https://gtrf.ru/",
    "http://www.museikino.ru/",
    "https://gosfilmofond.ru/",
    "https://mosfilmgold.ru/",
    "https://smotri.rgdb.ru/",
    "https://smotrim.ru/",
    "https://www.net-film.ru/",
    "http://www.gnesin-academy.ru",
    "https://music-museum.ru/",
    "http://www.bso.ru",
    "http://www.meloman.ru/",
    "http://www.music-competitions.ru",
    "http://www.daymusic.ru",
    "http://www.classic-music.ru",
    "http://www.zvuki.ru",
    "https://guitarmag.net/",
    "http://www.fondrii.ru",
    "http://operaclassic.net/",
    "http://www.belcanto.ru",
    "http://horist.ru/",
    "http://www.shanson-plus.ru",
    "http://www.pesni.ru",
    "http://www.zvukobaza.ru/",
    "https://jephtha010.nethouse.ru/",
    "http://www.karaoke.ru",
    "http://song-book.ru/songs/",
    "http://www.gitaristu.ru",
    "http://www.homecoming.ru",
    "http://zipsites.ru/music/bach",
    "http://www.beethoven.ru/",
    "http://bellini.belcanto.ru",
    "http://itopera.narod.ru",
    "http://glinka1804.narod.ru",
    "http://debussy.ru",
    "http://mozart.belcanto.ru",
    "http://www.mussorgsky.ru",
    "http://musorgskiy1839.narod.ru",
    "http://puccini.belcanto.ru",
    "http://www.tchaikov.ru",
    "http://fchopin.ru"
]

# Папка для сохранения выкачанных страниц
output_folder = "downloaded_pages"
os.makedirs(output_folder, exist_ok=True)

# Файл для хранения индекса
index_file = "index.txt"

# Функция для скачивания страницы
def download_page(url, file_number):
    try:
        # Отправляем GET-запрос
        response = requests.get(url)
        response.raise_for_status()  # Проверяем, что запрос успешен

        # Сохраняем HTML-код страницы в файл
        file_path = os.path.join(output_folder, f"page_{file_number}.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(response.text)

        # Записываем информацию в index.txt
        with open(index_file, "a", encoding="utf-8") as index:
            index.write(f"{file_number}: {url}\n")

        print(f"Скачано: {url} -> {file_path}")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при скачивании {url}: {e}")


if __name__ == "__main__":
    # Очищаем файл index.txt перед началом
    with open(index_file, "w", encoding="utf-8") as index:
        index.write("")

    # Скачиваем каждую страницу
    for i, url in enumerate(urls, start=1):
        download_page(url, i)

    print("Скачивание завершено.")