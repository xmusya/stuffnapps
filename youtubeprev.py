import os
import re
from urllib.parse import parse_qs, urlparse
import requests


def extract_video_id(url: str) -> str | None:
    """извлекает id видео из любой ссылки ютуба."""
    parsed_url = urlparse(url)

    if parsed_url.hostname in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        if parsed_url.path == "/watch":
            return parse_qs(parsed_url.query).get("v", [None])[0]
        if parsed_url.path.startswith(("/embed/", "/v/")):
            return parsed_url.path.split("/")[2]
        if parsed_url.path.startswith("/shorts/"):
            return parsed_url.path.split("/")[2]

    if parsed_url.hostname == "youtu.be":
        return parsed_url.path.lstrip("/")

    # если передали сразу id, а не ссылку
    if re.match(r"^[a-zA-Z0-9_-]{11}$", url):
        return url

    return None


def download_yt_thumbnail(
    url_or_id: str, output_folder: str = "thumbnails"
) -> bool:
    video_id = extract_video_id(url_or_id)

    if not video_id:
        print("ошибка: не удалось распарсить id видео из этой ссылки.")
        return False

    # создаем папку, если ее еще нет
    os.makedirs(output_folder, exist_ok=True)

    # качества от лучшего к худшему
    qualities = ["maxresdefault", "sddefault", "hqdefault", "mqdefault"]

    for quality in qualities:
        img_url = f"https://img.youtube.com/vi/{video_id}/{quality}.jpg"
        response = requests.get(img_url, timeout=10)

        # 200 ок, и проверяем чтобы ютуб не вернул дефолтную заглушку (она весит около 1кб)
        if response.status_code == 200 and len(response.content) > 2000:
            filepath = os.path.join(
                output_folder, f"{video_id}_{quality}.jpg"
            )
            with open(filepath, "wb") as file:
                file.write(response.content)
            print(f"успешно скачано: {filepath} (качество: {quality})")
            return True

    print("ошибка: не удалось найти превью для этого видео.")
    return False


if __name__ == "__main__":
    link = input("введи ссылку на видео или id: ").strip()
    if link:
        download_yt_thumbnail(link)
    else:
        print("ты опять ничего не ввел, гений.")
