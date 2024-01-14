import argparse
import json
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
    chrome_options.add_argument('headless')
    chrome_options.add_argument("--user-data-dir=selenium")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-web-security')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver


def download_with_retry(img_url, directory, save_filename, retry_count=0):
    try:
        file_name = f"{directory}/{save_filename}"

        # 파일 사이즈
        resHead = requests.head(img_url)
        total_length = resHead.headers.get('content-length')
        if not file_exists(file_name) or total_length is None or os.path.getsize(file_name) != int(total_length):
            with open(file_name, "wb") as f:
                print("Downloading %s" % file_name)
                response = requests.get(img_url, stream=True)

                if total_length is None:  # no content length header
                    f.write(response.content)
                else:
                    dl = 0
                    total_length = int(total_length)
                    for data in response.iter_content(chunk_size=4096):
                        dl += len(data)
                        f.write(data)
                        done = int(50 * dl / total_length)
                        sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                        sys.stdout.flush()

            print(f" {save_filename} 저장 완료. {total_length}")
        else:
            print(f" {save_filename} 이미 저장되었습니다.")

    except Exception as e:
        print(f"다운로드 실패: {e}")

        # 최대 재시도 횟수를 초과하지 않았을 경우 다시 시도 (5번)
        if retry_count < 5:
            print(f"다시 시도합니다. 재시도 횟수: {retry_count + 1}")
            time.sleep(3)  # 재시도 간격
            download_with_retry(img_url, directory, save_filename, retry_count + 1)
        else:
            print("최대 재시도 횟수를 초과하였습니다.")


def login():
    driver = createChromeDriver()
    driver.get('https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com')
    print('please press "ctrl+c"')
    while True:
        time.sleep(1)


def downloadContentsByArticleByArticleUrl(url):
    driver = createChromeDriver()
    try:
        driver.get(url)
        iframe = WebDriverWait(driver, 3) \
            .until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cafe_main")))
        # iframe으로 전환
        driver.switch_to.frame(iframe)

        time.sleep(2)
        title = driver.find_element(by=By.CSS_SELECTOR,
                                    value="#app > div > div > div.ArticleContentBox > div.article_header > div.ArticleTitle > div > h3").text
        article_date = (driver.find_element(by=By.CSS_SELECTOR,
                                            value="#app > div > div > div.ArticleContentBox > div.article_header > div.WriterInfo > div.profile_area > div.article_info > span.date")
                        .text.replace(". ", "_").replace(".", "").replace(":", ""))
        description = driver.find_element(by=By.CSS_SELECTOR,
                                          value="#app > div > div > div.ArticleContentBox > div.article_container > div.article_viewer > div > div.content.CafeViewer > div > div").text
        comments = driver.find_element(by=By.CSS_SELECTOR,
                                       value="#app > div > div > div.ArticleContentBox > div.article_container > div.CommentBox").text
        directory = f"downloads/{article_date}_{title}"
        print("==============================================")
        print("url=" + url)
        print("title=" + title)
        print("date=" + article_date)
        print("description=" + description)
        print("comments=" + comments)
        create_directory(directory)

        readmeHead = (f"{title}\n"
                      f"===================\n"
                      f"## 날짜\n"
                      f"{article_date}\n"
                      f"## 내용\n"
                      f"```\n{description}\n```\n")

        readmeFoot = (f"## 댓글\n"
                      f"```\n{comments}\n```")

        readme = readmeHead

        # save photo
        images = []
        try:
            images = WebDriverWait(driver, 5) \
                .until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[id^=\"SE-\"] > div > div > div > a > img")))
        except:
            print("이미지가 없습니다.")
            pass
        if len(images) != 0:
            readme += f"## 사진\n"
        for img in images:
            img_url = img.get_attribute('src').replace('?type=w1600', '')
            filename = extract_filename_from_url(img_url)
            filename_without_extension = remove_extension_from_filename(filename)
            save_filename = f"{filename_without_extension}_{images.index(img) + 1}.jpg"
            readme += f"![{save_filename}]({save_filename})\n"
            # 이미지 다운로드 & 저장
            download_with_retry(img_url, directory, save_filename)

        print(f"이미지 {len(images)} 저장 완료")

        # save video
        videos = []
        try:
            videos = driver.find_elements(by=By.CSS_SELECTOR,
                                          value="#app > div > div > div.ArticleContentBox > div.article_container > div.article_viewer > div > div.content.CafeViewer > div > div > div.se-component.se-video.se-l-default > script")
            videos_names = driver.find_elements(by=By.CSS_SELECTOR,
                                          value="#app > div > div > div.ArticleContentBox > div.article_container > div.article_viewer > div > div.content.CafeViewer > div > div > div.se-component.se-video.se-l-default > div > div > div.se-media-meta > div > strong > span")
        except:
            print("Videos not found")
            pass
        if len(videos) != 0:
            readme += f"## 비디오\n"
        for video in videos:
            videoSourceJSON = json.loads(video.get_attribute("data-module"))
            vid = videoSourceJSON['data']['vid']
            inkey = videoSourceJSON['data']['inkey']
            if vid and inkey:
                videoJSON = json.loads(
                    requests.get(f"https://apis.naver.com/rmcnmv/rmcnmv/vod/play/v2.0/{vid}?key={inkey}").text)
                video_url = videoJSON['videos']['list'][-1]['source']
                filename = extract_filename_from_url(video_url)
                filename_without_extension = remove_extension_from_filename(filename)
                #save_filename = f"{filename_without_extension}_{videos.index(video) + 1}.mp4"
                new_save_filename = f"{videos_names[videos.index(video)].text}_{videos.index(video) + 1}.mp4"
                readme += f"![{new_save_filename}]({new_save_filename})\n"
                # 비디오 다운로드 & 저장
                download_with_retry(video_url, directory, new_save_filename)
                #move_file(f"{directory}/{save_filename}", f"{directory}/{new_save_filename}")


            else:
                print(f"vid={vid} key={key}정보가 없습니다.")
        print(f"비디오 {len(videos)} 저장 완료")

        readme += readmeFoot
        # save README
        save_string_to_file(f"{directory}/README.md", readme)

    except:
        print("게시물 정보를 가져 오는데 실패했습니다.")
        traceback.print_exc(file=sys.stdout)
        pass
    finally:
        driver.close()


def getArticleUrlListByList(url):
    try:
        print(url)
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
        print("게시물 리스트 정보를 가져 오는데 실패했습니다.")
        traceback.print_exc(file=sys.stdout)
        pass
    finally:
        driver.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-l", "--login", help="login", action='store_true')
    parser.add_argument("-au", "--article-url", type=str,
                        help="download image in article (https://cafe.naver.com/ArticleRead.nhn....) ")
    parser.add_argument("-lu", "--list-url", type=str,
                        help="download image in article list (https://cafe.naver.com/ArticleList.nhn...)")
    args = parser.parse_args()
    if args.login:
        login()
    elif args.article_url:
        downloadContentsByArticleByArticleUrl(args.article_url)
    elif args.list_url:
        articles_url = getArticleUrlListByList(args.list_url)
        for url in reversed(articles_url):
            downloadContentsByArticleByArticleUrl(url)
    else:
        parser.print_usage()
