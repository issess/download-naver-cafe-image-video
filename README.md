# download-naver-cafe-images

네이버 카페에 있는 사진을 다운로드 하기 위해 만들었습니다.

## Setup

파이선 가상환경 만들기

```
$ python3 -m venv .venv
```

가상환경 활성와

```commandline
# activate env
$ . .venv/bin/activate
```

필요한 패키지 설치

```commandline
(.venv) $ pip install -r requirements.txt
```

다 사용 후 비황성화 (선택사항)

```commandline
# deactivate env
(.venv) $ deactivate
```

## Usage

도움말

```commandline
$ python main.py -h
```

네이버 카페글에서 이미지 다운로드

```commandline
$ python main.py --article-url https://cafe.naver.com/ArticleRead.nhn...
```

네이버 목록에서 각게시글 이미지 다운로드

```commandline
$ python main.py --article-url https://cafe.naver.com/ArticleList.nhn...
```

