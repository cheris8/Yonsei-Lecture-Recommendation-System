import random
import time
from selenium import webdriver as wd
import selenium
import re
from bs4 import BeautifulSoup
import pandas as pd
from pandas import DataFrame as df

lecturetable = pd.read_csv('2020LectureTable_Demo.csv')
urlList = lecturetable['LectureUrl']


###############로그인 코드#####################

# 자동 로그인

# 에브리타임 자동 로그인

# 가상브라우저 사용
options = wd.ChromeOptions()
options.add_argument("no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument(
    "user-agent={Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36}")  # 내 user-agent값

driver = wd.Chrome(
    executable_path='/usr/local/bin/chromedriver', options=options)
driver.maximize_window()


baseURL = 'https://everytime.kr/login'

rand_value = random.uniform(2, 4)  # 랜덤한 시간으로
time.sleep(rand_value)  # sleep걸어주기
driver.get(baseURL)  # 페이지가 넘어갈 때마다 sleep걸어주어서 서버에 무리가 가지 않게 해야함

rand_value = random.uniform(2, 4)
time.sleep(rand_value)

driver.find_element_by_name('userid').send_keys('jiyoung15105')  # 아이디
driver.find_element_by_name('password').send_keys('dlatnrud105')  # 비밀번호

rand_value = random.uniform(2, 4)
time.sleep(rand_value)
driver.find_element_by_xpath('//*[@class="submit"]/input').click()


################크롤링 코드#####################


# 강의 -> 강의평가
lecture_review_list = []

for url in urlList:
    # 강의 페이지로 넘어가기
    rand_value = random.uniform(2, 5)
    time.sleep(rand_value)
    driver.get(url)

    # 하나의 강의 평가 페이지 bs로 데이터 수집
    time.sleep(3)
    html = driver.page_source
    # 정적텍스트 분석을 사용하는 BS이 selenium보다 빠름 -> 페이지접근에는 동적 수집, 데이터 수집은 정적수집적
    soup = BeautifulSoup(html, 'html.parser')

    lecture_name = soup.select_one("#container > div.side.head > h2").text
    professor_name = soup.select_one(
        "#container > div.side.head > p:nth-of-type(2) > span").text
    review_list = soup.select("article")
    print(lecture_name, professor_name)

    # 강의리뷰
    index = 0
    for review in review_list:
        if review.select_one('div.pay') == None:  # 강의평가가 아니라 중간,기말고사 족보
            rate = review.select_one('p.rate > span > span')[
                "style"]  # str사용해야 re사용가능
            rate = float(rate[-5:-2])  # 숫자만 (리스트형태로 return되는데 [0]하면 오류뜸...)
            semester = review.select_one('p.info > span.semester').text
            semester = semester[0:7]
            text = review.select_one('p.text').text

            lecture_review_list.append({
                "index": index,
                "url": url,
                "lecture_name": lecture_name,
                "professor_name": professor_name,
                "rate": rate,
                "semester": semester,
                "text": text
            }
            )
            index += 1


reviewdf = df.from_records(lecture_review_list)

print(reviewdf)

reviewdf.to_csv("2020ReviewTable_Demo.csv", mode='w')
