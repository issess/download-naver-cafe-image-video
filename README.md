# download-naver-cafe-images-and-videos

매주 어린이집에서 네이버 카페에 올리는 아이 사진을 하나하나 저장하기 힘들어 
사진, 비디오, 내용, 코멘트를 한번에 다운로드 하기 위해 만들었습니다.
정성스럽게 올려주시는 선생님께 감사드리며, 다운로드에 고통받는 분들이 줄어 들기를...  

 * 다운로드 실패시 다시 시도기능. 
 * 이미지,비디오 원본으로 다운로드
 * Markdown으로 게시글 내용 및 코멘트 저장

## Setup

가상환경 만들기

```
$ python3 -m venv .venv
```

python 가상환경 활성화

```commandline
# activate env
$ . .venv/bin/activate
```

필요한 패키지 설치

```commandline
(.venv) $ pip install -r requirements.txt
```

사용 후 비황성화 (선택사항)

```commandline
# deactivate env
(.venv) $ deactivate
```

## Help
```commandline
$ python main.py -h
usage: main.py [-h] [-l] [-au ARTICLE_URL] [-lu LIST_URL]

optional arguments:
  -h, --help            show this help message and exit
  -l, --login           login (default: False)
  -au ARTICLE_URL, --article-url ARTICLE_URL
                        download image in article (https://cafe.naver.com/ArticleRead.nhn....) (default: None)
  -lu LIST_URL, --list-url LIST_URL
                        download image in article list (https://cafe.naver.com/ArticleList.nhn...) (default: None)
```

## Usage

## 네이버 로그인
로그인 정보를 저장에 체크하고 로그인을 최초 1회 합니다.

```commandline
$ python main.py -l
```

### 네이버 카페글에서 이미지 다운로드
네이버 카페 게시물의 주소를 복사해서 아래와 같이 붙여 넣기 하시면 됩니다.

```commandline
$ python main.py --article-url https://cafe.naver.com/ArticleRead.nhn...
```

### 네이버 목록에서 각게시글 이미지 다운로드
게시물 목록에서 게시글 url을 뽑아 리스트에 있는 데이터를 한번에 추출 할 수 있습니다.
게시글 목록당 출력 갯수를 50개로 변경(카페 내에서)하여 주소를 입력하면 편하게 사용할 수 있습니다.

```commandline
$ python main.py --article-url https://cafe.naver.com/ArticleList.nhn...
```

## Result
downloads 폴더에 게시글 이름으로 저장이 됩니다.