"""Description:
    * author: Magdy Abdelkader
    * company: Fresh Futures/Seeka Technology
    * position: IT Intern
    * date: 11-11-20
    * description:This script extracts all the courses links and save it in txt file.
"""
from pathlib import Path
from selenium import webdriver
from urllib.parse import urljoin
import os


option = webdriver.ChromeOptions()
option.add_argument(" - incognito")
option.add_argument("headless")
exec_path = Path(os.getcwd().replace('\\', '/'))
exec_path = exec_path.parent.__str__() + '/Libraries/Google/v86/chromedriver.exe'
browser = webdriver.Chrome(executable_path=exec_path, options=option)

# MAIN ROUTINE
courses_page_url = 'https://www.northmetrotafe.wa.edu.au/courses'
base_url = 'https://www.northmetrotafe.wa.edu.au/'
list_of_links = []
browser.get(courses_page_url)
the_url = browser.page_source
delay_ = 15  # seconds

# SAVE THE LINKS TO LIST
tr_list = browser.find_elements_by_class_name('c-course.award-course')
for i, tr in enumerate(tr_list):
    td = tr.find_element_by_class_name('c-course-title')
    a_tag = td.find_element_by_tag_name('a')
    sup_url = a_tag.get_property('href')
    url = urljoin(base_url,sup_url)
    list_of_links.append(url)


# SAVE TO FILE
course_links_file_path = os.getcwd().replace('\\', '/') + '/NMTAFE_courses_links.txt'
course_links_file = open(course_links_file_path, 'w')
for link in list_of_links:
    if link is not None and link != "" and link != "\n":
        if link == list_of_links[-1]:
            course_links_file.write(link.strip())
        else:
            course_links_file.write(link.strip() + '\n')
course_links_file.close()
