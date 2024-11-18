from bs4 import BeautifulSoup
import pymongo
import requests

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['CPP']
collection = db['professors']

url = 'https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml'

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')


faculty_list = []
for faculty in soup.find_all('div', class_="clearfix"):
    name = faculty.find('h2').get_text(strip=True) if faculty.find('h2') else None

    title, phone, office = None, None, None
    strong_tags = faculty.find_all('strong')

    for tag in strong_tags:
        label = tag.get_text(strip=True)

        if 'Title:' in label:
            title = tag.find_next(text=True).strip() if tag.find_next(text=True) else None
        elif 'Office:' in label:
            office = tag.find_next(text=True).strip() if tag.find_next(text=True) else None
        elif 'Phone:' in label:
            phone = tag.find_next(text=True).strip() if tag.find_next(text=True) else None

    email = faculty.find('a', href=lambda href: href and 'mailto:' in href).get_text(strip=True) if faculty.find('a', href=lambda href: href and 'mailto:' in href) else None
    website = faculty.find('a', href=lambda href: href and 'https:' in href)['href'] if faculty.find('a', href=lambda href: href and 'https:' in href) else None

    faculty_data = {
        'name': name,
        'title': title,
        'office': office,
        'phone': phone,
        'email': email,
        'website': website
    }
    faculty_list.append(faculty_data)

if faculty_list:
    collection.insert_many(faculty_list)
    print(f'Successfully inserted {len(faculty_list)} documents into MongoDB.')
else:
    print("Cannot insert data.")