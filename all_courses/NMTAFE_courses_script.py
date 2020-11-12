import csv
import re
import time
from pathlib import Path
from selenium import webdriver
import bs4 as bs4
import os
import copy
from CustomMethods import TemplateData
from CustomMethods import DurationConverter as dura

option = webdriver.ChromeOptions()
option.add_argument(" - incognito")
option.add_argument("headless")
exec_path = Path(os.getcwd().replace('\\', '/'))
exec_path = exec_path.parent.__str__() + '/Libraries/Google/v86/chromedriver.exe'
browser = webdriver.Chrome(executable_path=exec_path, options=option)

# read the url from each file into a list
course_links_file_path = Path(os.getcwd().replace('\\', '/'))
course_links_file_path = course_links_file_path.__str__() + '/NMTAFE_courses_links.txt'
course_links_file = open(course_links_file_path, 'r')

# the csv file we'll be saving the courses to
csv_file_path = Path(os.getcwd().replace('\\', '/'))
csv_file = csv_file_path.__str__() + '/NMTAFE_courses.csv'

course_data = {'Level_Code': '', 'University': 'North Metropolitan TAFE', 'City': '', 'Country': 'Australia',
               'Course': '', 'Int_Fees': '', 'Local_Fees': '', 'Currency': 'AUD', 'Currency_Time': 'year',
               'Duration': '', 'Duration_Time': '', 'Full_Time': 'yes', 'Part_Time': 'yes', 'Prerequisite_1': '',
               'Prerequisite_2': '', 'Prerequisite_3': '', 'Prerequisite_1_grade': '', 'Prerequisite_2_grade': '',
               'Prerequisite_3_grade': '', 'Website': '', 'Course_Lang': '', 'Availability': 'D', 'Description': '',
               'Career_Outcomes': '', 'Online': '', 'Offline': '', 'Distance': 'no', 'Face_to_Face': '',
               'Blended': 'no', 'Course_delivery_mode': '', 'Free_TAFE': 'no', 'Remarks': ''}

possible_cities = {'canberra': 'Canberra', 'bruce': 'Bruce', 'mumbai': 'Mumbai', 'melbourne': 'Melbourne',
                   'brisbane': 'Brisbane', 'sydney': 'Sydney', 'queensland': 'Queensland', 'ningbo': 'Ningbo',
                   'shanghai': 'Shanghai', 'bhutan': 'Bhutan', 'online': 'Online', 'hangzhou': 'Hangzhou',
                   'hanoi': 'Hanoi', 'bundoora': 'Bundoora', 'brunswick': 'Brunswick', 'bendigo': 'Victoria',
                   'balga': 'Balga', 'clarkson': 'Clarkson', 'joondalup': 'Joondalup', 'leederville': 'Leederville',
                   'midland': 'Midland', 'mount lawley': 'Mount Lawley', 'nedlands': 'Nedlands', 'perth': 'Perth'}

possible_languages = {'Japanese': 'Japanese', 'French': 'French', 'Italian': 'Italian', 'Korean': 'Korean',
                      'Indonesian': 'Indonesian', 'Chinese': 'Chinese', 'Spanish': 'Spanish'}

course_data_all = []
level_key = TemplateData.level_key  # dictionary of course levels
faculty_key = TemplateData.faculty_key  # dictionary of course levels

# GET EACH COURSE LINK
for each_url in course_links_file:
    remarks_list = []
    actual_cities = []
    browser.get(each_url)
    pure_url = each_url.strip()
    each_url = browser.page_source

    soup = bs4.BeautifulSoup(each_url, 'lxml')
    time.sleep(1)

    # SAVE COURSE URL
    course_data['Website'] = pure_url

    # COURSE TITLE
    title_tag = soup.find('div', class_='container c-page-title')
    if title_tag:
        title_h = title_tag.find('h1')
        if title_h:
            course_data['Course'] = title_h.get_text()
            print('COURSE TITLE: ', title_h.get_text())

    # DECIDE THE LEVEL CODE
    for i in level_key:
        for j in level_key[i]:
            if j in course_data['Course']:
                course_data['Level_Code'] = i
    print('COURSE LEVEL CODE: ', course_data['Level_Code'])

    # DECIDE THE FACULTY
    for i in faculty_key:
        for j in faculty_key[i]:
            if j.lower() in course_data['Course'].lower():
                course_data['Faculty'] = i
    print('COURSE FACULTY: ', course_data['Faculty'])

    # COURSE LANGUAGE
    for language in possible_languages:
        if language in course_data['Course']:
            course_data['Course_Lang'] = language
        else:
            course_data['Course_Lang'] = 'English'
    print('COURSE LANGUAGE: ', course_data['Course_Lang'])

    # COURSE DESCRIPTION
    desc_tag = soup.find('div', class_='field-item even')
    if desc_tag:
        p_list = desc_tag.find_all('p')
        if p_list:
            desc_list = []
            for p in p_list:
                desc_list.append(p.get_text())
            desc_list = ' '.join(desc_list)
            course_data['Description'] = desc_list
            print('COURSE DESCRIPTION: ', desc_list)

    # PREREQUISITES
    prerequisite_table = soup.find('table', class_='entrance_requirement')
    if prerequisite_table:
        t_body = prerequisite_table.find_all('tbody')
        if t_body[1]:
            tr = t_body[1].find('tr')
            if tr:
                non_school_leaver = tr.find('td')
                school_leaver = tr.find_all('td')
                if non_school_leaver:
                    if 'Year 10' in non_school_leaver.get_text():
                        course_data['Prerequisite_1'] = 'year 10'
                    elif 'Year 11' in non_school_leaver.get_text():
                        course_data['Prerequisite_1'] = 'year 11'
                    elif 'Year 9' in non_school_leaver.get_text():
                        course_data['Prerequisite_1'] = 'year 9'
                    else:
                        course_data['Prerequisite_1'] = non_school_leaver.get_text()
                    n_grade = re.search(r'\d+', non_school_leaver.get_text())
                    if 'C Grades' in non_school_leaver.get_text():
                        course_data['Prerequisite_1_grade'] = 'C Grades'
                    elif 'Band' in non_school_leaver.get_text() and n_grade is not None:
                        course_data['Prerequisite_1_grade'] = n_grade.group()
                if school_leaver[1]:
                    if 'Year 10' in school_leaver[1].get_text():
                        course_data['Prerequisite_2'] = 'year 10'
                    elif 'Year 11' in school_leaver[1].get_text():
                        course_data['Prerequisite_2'] = 'year 11'
                    elif 'Year 9' in school_leaver[1].get_text():
                        course_data['Prerequisite_2'] = 'year 9'
                    else:
                        course_data['Prerequisite_2'] = school_leaver[1].get_text()
                    s_grade = re.search(r'\d+', school_leaver[1].get_text())
                    if 'C Grades' in school_leaver[1].get_text():
                        course_data['Prerequisite_2_grade'] = 'C Grades'
                    elif 'Band' in school_leaver[1].get_text() and s_grade is not None:
                        course_data['Prerequisite_2_grade'] = s_grade.group()
    else:
        course_data['Prerequisite_1'] = 'Not mentioned'
        course_data['Prerequisite_2'] = 'Not mentioned'
        course_data['Prerequisite_1_grade'] = 'Not mentioned'
        course_data['Prerequisite_2_grade'] = 'Not mentioned'
    print('PREREQUISITE 1: ', course_data['Prerequisite_1'])
    print('PREREQUISITE 2: ', course_data['Prerequisite_2'])
    print('PRE-1-GRADE: ', str(course_data['Prerequisite_1_grade']))
    print('PRE-2-GRADE: ', str(course_data['Prerequisite_2_grade']))

    # FEES
    fees_container = soup.find('div', class_='field field-name-field-fee-table field-type-text-long field-label-hidden')
    course_data['Local_Fees'] = ''
    if fees_container:
        fee_table = fees_container.find('table')
        if fee_table:
            t_body = fee_table.find('tbody')
            if t_body:
                tr = t_body.find_all('tr')
                if tr:
                    fee_td = tr[1].find_all('td')
                    if fee_td:
                        fee = fee_td[0].get_text()
                        fee_n = re.search(r"\d+(?:.\d+)|\d+", fee)
                        if fee_n is not None:
                            course_data['Local_Fees'] = fee_n.group()
                            print('fee: ', fee_n.group())
                        elif 'Tuition fee' in fee.strip():
                            fee_td_1 = tr[2].find_all('td')
                            if fee_td_1:
                                fee_1 = fee_td_1[0].get_text()
                                fee_n_1 = re.search(r"\d+(?:.\d+)|\d+", fee_1)
                                if fee_n_1 is not None:
                                    course_data['Local_Fees'] = fee_n_1.group()
                                    print('fee 1: ', fee_n_1.group())

    # CITY
    city_tag = soup.find_all('td', class_='c-course-where-icon', text=re.compile('where', re.IGNORECASE))
    if city_tag:
        for city in city_tag:
            city_ = city.find_next_sibling('td')
            if city_:
                city_text = city_.get_text().strip().lower()
                if 'nedlands' in city_text:
                    actual_cities.append('nedlands')
                if 'perth' in city_text:
                    actual_cities.append('perth')
                if 'balga' in city_text:
                    actual_cities.append('balga')
                if 'clarkson' in city_text:
                    actual_cities.append('clarkson')
                if 'joondalup' in city_text:
                    actual_cities.append('joondalup')
                if 'leederville' in city_text:
                    actual_cities.append('leederville')
                if 'midland' in city_text:
                    actual_cities.append('midland')
                if 'mount lawley' in city_text:
                    actual_cities.append('mount lawley')
                if 'online' in city_text:
                    actual_cities.append('online')
        print('CITY: ', actual_cities)

    # DURATION
    duration_tag = soup.find('td', class_='c-course-duration-icon', text=re.compile('duration', re.IGNORECASE))
    if duration_tag:
        duration = duration_tag.find_next_sibling('td')
        if duration:
            converted_dura = dura.convert_duration(duration.get_text().strip())
            if converted_dura is not None:
                duration_list = list(converted_dura)
                if duration_list[0] == 1 and 'Years' in duration_list[1]:
                    duration_list[1] = 'Year'
                if duration_list[0] == 1 and 'Months' in duration_list[1]:
                    duration_list[1] = 'Month'
                if duration_list[0] == 1 and 'Weeks' in duration_list[1]:
                    duration_list[1] = 'Week'
                course_data['Duration'] = duration_list[0]
                course_data['Duration_Time'] = duration_list[1]
                print('Duration: ', str(duration_list[0]) + ' / ' + duration_list[1])

    # COURSE DELIVERY
    ave_list = soup.find_all('a', class_="availability-title accordion-heading")
    if ave_list:
        delivery_mode_list = []
        course_data['Course_delivery_mode'] = ''
        for a in ave_list:
            delivery_text = a.get_text().strip().lower()
            if 'traineeship' in delivery_text:
                delivery_mode_list.append('Traineeship')
            if 'apprenticeship' in delivery_text:
                delivery_mode_list.append('Apprenticeship')
            if 'employer-based' in delivery_text:
                delivery_mode_list.append('Employer-based')
            if 'on campus' in delivery_text:
                delivery_mode_list.append('Normal')
                course_data['Offline'] = 'yes'
                course_data['Face_to_Face'] = 'yes'
            else:
                course_data['Offline'] = 'no'
                course_data['Face_to_Face'] = 'no'
            if 'online' in delivery_text:
                course_data['Online'] = 'yes'
                delivery_mode_list.append('Online')
            else:
                course_data['Online'] = 'no'
        delivery_mode_list = ' '.join(delivery_mode_list)
        mode_list = []
        if 'Traineeship' in delivery_mode_list:
            mode_list.append('Traineeship')
        if 'Apprenticeship' in delivery_mode_list:
            mode_list.append('Apprenticeship')
        if 'Employer-based' in delivery_mode_list:
            mode_list.append('Employer-based')
        if 'Normal' in delivery_mode_list:
            mode_list.append('Normal')
        if 'Online' in delivery_mode_list:
            mode_list.append('Online')
        mode_list = ' / '.join(mode_list)
        course_data['Course_delivery_mode'] = mode_list
    print('COURSE DELIVERY MODE: ', course_data['Course_delivery_mode'])
    print('DELIVERY: online: ' + course_data['Online'] + ' offline: ' + course_data['Offline'] + ' face to face: ' +
          course_data['Face_to_Face'] + ' blended: ' + course_data['Blended'] + ' distance: ' + course_data['Distance'])

    # CAREER OUTCOMES
    career_tag = soup.find_all('div', class_='c-job-opportunities-option')
    if career_tag:
        career_list = []
        for a in career_tag:
            career_a = a.find('a')
            if career_a:
                career_list.append(career_a.get_text().strip())
        career_list = ' | '.join(career_list)
        course_data['Career_Outcomes'] = career_list
    print('CAREER OUTCOMES: ', course_data['Career_Outcomes'])

    # duplicating entries with multiple cities for each city
    for i in actual_cities:
        course_data['City'] = possible_cities[i]
        course_data_all.append(copy.deepcopy(course_data))
    del actual_cities

    # TABULATE THE DATA
    desired_order_list = ['Level_Code', 'University', 'City', 'Course', 'Faculty', 'Int_Fees', 'Local_Fees',
                          'Currency', 'Currency_Time', 'Duration', 'Duration_Time', 'Full_Time', 'Part_Time',
                          'Prerequisite_1', 'Prerequisite_2', 'Prerequisite_3', 'Prerequisite_1_grade',
                          'Prerequisite_2_grade', 'Prerequisite_3_grade', 'Website', 'Course_Lang', 'Availability',
                          'Description', 'Career_Outcomes', 'Country', 'Online', 'Offline', 'Distance', 'Face_to_Face',
                          'Blended', 'Course_delivery_mode', 'Free_TAFE', 'Remarks']

    course_dict_keys = set().union(*(d.keys() for d in course_data_all))

    with open(csv_file, 'w', encoding='utf-8', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, course_dict_keys)
        dict_writer.writeheader()
        dict_writer.writerows(course_data_all)

    with open(csv_file, 'r', encoding='utf-8') as infile, open('NMTAFE_courses_ordered.csv', 'w', encoding='utf-8',
                                                               newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=desired_order_list)
        # reorder the header first
        writer.writeheader()
        for row in csv.DictReader(infile):
            # writes the reordered rows to the new file
            writer.writerow(row)
