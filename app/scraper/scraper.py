"""
For now this scraper is standalone
"""
import json

from bs4 import BeautifulSoup
from selenium import webdriver
import requests
from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
courses_data = {}

course_code_file = open("course_codes.txt", "r")

for line in course_code_file.readlines():
    course = line.split(" ")[0]
    print(course)
    url = "https://www.handbook.unsw.edu.au/undergraduate/courses/2021/{}".format(course)
    try:
        driver.get(url)

        inner = driver.find_element_by_class_name("OverviewInner")
        print("Getting course:", course)

        buttons = inner.find_elements_by_tag_name("button")
        buttons[0].click()

        p_tags = inner.find_elements_by_tag_name("p")
        paragraphs = []
        for p in p_tags:
            paragraphs.append(p.text)
        courses_data[course] = "\n\n".join(paragraphs)
    except Exception:
        pass # Lazily skip if can't find elements

with open("course_data.json", "w") as f:
    f.write(json.dumps(courses_data))

# print(inner.text)
# page_content = res.content
# soup = BeautifulSoup(page_content, 'html.parser')
# handbook = soup.find("div", {"id": "handbook"})
# with open("out.html", "w") as f:
#     f.write(soup.prettify())
#     f.close()
# print(handbook.findAll(True))
# inf = soup.find('div', class_="OverviewInner")
# info = inf.find_all('p')
