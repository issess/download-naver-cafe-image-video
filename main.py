import argparse
import os
import shutil
import sys
import time
import traceback
from urllib.parse import urlparse, unquote

import requests
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver


def save_string_to_file(file_path, content):
    try:
        # 파일 열기 또는 생성하여 쓰기 모드로 열기
        with open(file_path, 'w', encoding='utf-8') as file:
            # 문자열을 파일에 쓰기
            file.write(content)
        print(f"파일 '{file_path}'에 성공적으로 저장되었습니다.")
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {e}")


def create_directory(directory_path):
    try:
        # 디렉토리 생성
        os.makedirs(directory_path)
        print(f"디렉토리 '{directory_path}'가 생성되었습니다.")
    except FileExistsError:
        print(f"디렉토리 '{directory_path}'는 이미 존재합니다.")


def remove_extension_from_filename(filename):
    # 파일명과 확장자 분리
    base_name, extension = os.path.splitext(filename)

    # 확장자 제거
    filename_without_extension = base_name

    return filename_without_extension


def extract_filename_from_url(url):
    # URL을 파싱하여 파일 경로 추출
    parsed_url = urlparse(url)
    file_path = unquote(parsed_url.path)

    # 파일 경로에서 마지막 부분(파일명) 추출
    filename = file_path.split('/')[-1]

    return filename


def move_file(source_path, destination_path):
    try:
        # 파일 이동
        shutil.move(source_path, destination_path)
        print(f"파일을 {destination_path}로 이동했습니다.")
    except Exception as e:
        print(f"파일 이동 중 오류 발생: {e}")


def file_exists(file_path):
    return os.path.isfile(file_path)


def createChromeDriver():
    chrome_options = webdriver.ChromeOptions()
    # head less
    #chrome_options.add_argument('headless')
    chrome_options.add_argument("--user-data-dir=selenium")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-web-security')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver


def download_image_with_retry(img_url, title, save_filename, retry_count=0):
    try:
        # 이미지 다운로드
        img_data = requests.get(img_url).content

        # 이미지 저장
        with open(f"downloads/{title}/{save_filename}", 'wb') as f:
            f.write(img_data)

        print(f"{save_filename} 저장 완료")

    except Exception as e:
        print(f"다운로드 실패: {e}")

        # 최대 재시도 횟수를 초과하지 않았을 경우 다시 시도 (5번)
        if retry_count < 5:
            print(f"다시 시도합니다. 재시도 횟수: {retry_count + 1}")
            time.sleep(3)  # 재시도 간격
            download_image_with_retry(img_url, title, save_filename, retry_count + 1)
        else:
            print("최대 재시도 횟수를 초과하였습니다.")


def login():
    driver = createChromeDriver()
    driver.get('https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com')
    print('please press "ctrl+c"')
    while True:
        time.sleep(1)


def downloadImageByArticleByArticleUrl(url):
    driver = createChromeDriver()
    try:
        driver.get(url)
        iframe = WebDriverWait(driver, 5) \
            .until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cafe_main")))
        # iframe으로 전환
        driver.switch_to.frame(iframe)

        time.sleep(2)
        title = driver.find_element(by=By.CSS_SELECTOR,
                                    value="#app > div > div > div.ArticleContentBox > div.article_header > div.ArticleTitle > div > h3").text
        article_date = driver.find_element(by=By.CSS_SELECTOR,
                                           value="#app > div > div > div.ArticleContentBox > div.article_header > div.WriterInfo > div.profile_area > div.article_info > span.date").text
        description = driver.find_element(by=By.CSS_SELECTOR,
                                          value="#app > div > div > div.ArticleContentBox > div.article_container > div.article_viewer > div > div.content.CafeViewer > div > div").text
        comments = driver.find_element(by=By.CSS_SELECTOR,
                                       value="#app > div > div > div.ArticleContentBox > div.article_container > div.CommentBox").text
        print()
        print("url=" + title)
        print("title=" + title)
        print("date=" + article_date)
        print("description=" + description)
        print("comments=" + comments)
        create_directory(f"downloads/{title}")

        images = []
        try:
            images = WebDriverWait(driver, 5) \
                .until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[id^=\"SE-\"] > div > div > div > a > img")))
        except:
            print("Images not found")
            pass

        readmeHead = (f"{title}\n"
                      f"===================\n"
                      f"## 날짜\n"
                      f"{article_date}\n"
                      f"## 내용\n"
                      f"```\n{description}\n```\n"
                      f"## 사진\n")

        readmeFoot = (f"## 댓글\n"
                      f"```\n{comments}\n```")

        readme = readmeHead

        # save photo
        for img in images:
            img_url = img.get_attribute('src').replace('?type=w1600', '')
            filename = extract_filename_from_url(img_url)
            filename_without_extension = remove_extension_from_filename(filename)
            save_filename = f"{filename_without_extension}_{images.index(img) + 1}.jpg"
            readme += f"![alt text]({save_filename})\n"
            # 이미지 다운로드 & 저장
            # download_image_with_retry(img_url, title, save_filename)
            # 이동
            # move_file(save_filename,f"{title}/{save_filename}")
            # validation
            if not file_exists(f"downloads/{title}/{save_filename}"):
                raise FileNotFoundError(f"파일 {save_filename}이 존재하지 않습니다.")

        print(f"이미지 {len(images)} 저장 완료")

        readme += readmeFoot
        # save README
        save_string_to_file(f"downloads/{title}/README.md", readme)

    except:
        traceback.print_exc(file=sys.stdout)
        pass
    finally:
        driver.close()


def getArticleUrlListByList(url):
    try:
        driver = createChromeDriver()
        driver.get(url)
        iframe = WebDriverWait(driver, 5) \
            .until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cafe_main")))
        # iframe으로 전환
        driver.switch_to.frame(iframe)
        articles = WebDriverWait(driver, 10) \
            .until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "#main-area > * > table > tbody > * > td.td_article > div.board-list > div > a.article")))
        # get articles
        texts = []
        hrefs = []
        for article in articles:
            text = article.text
            href = article.get_attribute('href')
            print(f"{text} : {href}")
            texts.append(text)
            hrefs.append(href)
        return hrefs
    except:
        traceback.print_exc(file=sys.stdout)
        pass
    finally:
        driver.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-l", "--login", help="login", action='store_true')
    parser.add_argument("--headless", help="headless", action='store_true')
    parser.add_argument("-au", "--article-url", type=str,
                        help="download image in article (https://cafe.naver.com/ArticleRead.nhn....) ")
    parser.add_argument("-lu", "--list-url", type=str,
                        help="download image in article list (https://cafe.naver.com/ArticleList.nhn...)")
    args = parser.parse_args()
    if args.login:
        login()
    elif args.article_url:
        downloadImageByArticleByArticleUrl(args.article_url)
    elif args.list_url:
        articles_url = getArticleUrlListByList(args.list_url)
        for url in reversed(args.list):
            downloadImageByArticleByArticleUrl(url)
    else:
        parser.print_usage()
