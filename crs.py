import requests
from bs4 import BeautifulSoup
import enum
from prettytable import PrettyTable


class CRSColumn(enum.Enum):
    ClassCode = 1
    Class = 2
    Credits = 3
    Schedule = 4
    Instructor = 5
    Remarks = 6
    EnlistingUnit = 7
    AvailableSlots = 8
    TotalSlots = 9
    Demand = 10
    Restrictions = 11   


class CRS:
    def __init__(self, link: str = 'https://crs.upd.edu.ph/schedule/') -> None:
        self.__base_link = link
        self.__base_soup = self.__download_page(self.__base_link)
        self.__default_schedule_tag = self.__base_soup.find('option', selected = True)
        self.__column_count = len(self.__base_soup.find_all('th'))


    def __process_link(self, search_term: str, schedule_text) -> str:
        # Given the input to forms, generate a link following to the page
        # If schedule_text is False, use the defailt schedule
        schedule_tag = self.__base_soup.find('option', string=schedule_text) if schedule_text else self.__default_schedule_tag
        if schedule_tag == None:
            raise ValueError('Schedule text should be exactly the same with a schedule of classes in CRS, e.g. "First Semester AY 2022-2023"')
        schedule_value = schedule_tag['value']

        word = number = ''
        splitted = search_term.split(' ')
        if len(splitted) == 2:
            word, number = splitted
        elif len(splitted) == 1:
            word = search_term
        else: 
            raise ValueError('Search term should be class word and an optional number, e.g. "cs", "cs 21"')
        
        number = f'%20{number}' if number else ''
        processed_link = f'{self.__base_link}{schedule_value}/{word}{number}'
        return processed_link


    def __download_page(self, processed_link) -> BeautifulSoup:
        # Retrieves the page as a BeautifulSoup object
        r = requests.get(processed_link)
        soup = BeautifulSoup(r.content, 'html.parser')
        return soup


    def __get_row_results(self, soup) -> list:
        

        rows = soup.find_all('tbody')
        results = []
        if len(rows) == 0:
            return []

        for row in rows:
            # Replace br tag with a newline character
            for br in row.find_all('br'):
                br.replace_with('\n')
            
            current_row = list(map(lambda x: x.text, row.find_all('td')))
            class_code = current_row[0]
            crs_class = current_row[1]
            credits = current_row[2]
            
            # schedule, instructor and remarks belong to the same td (cell)
            temp = current_row[3].strip().split('\n')
            schedule = temp[0].strip()
            instructor = temp[1].strip()
            remarks = temp[2].strip() if len(temp) > 2 else ''

            enlisting_unit = current_row[4]

            # When 2 cells are merged in a row, the class is DISSOLVED
            if len(current_row) == self.__column_count - 1:
                available_slots = 'DISSOLVED'
                total_slots = 'DISSOLVED'
                demand = 'DISSOLVED'
                restrictions = current_row[6]
            else:
                temp = current_row[5].strip().split('\n')
                available_slots = temp[0].replace('/', '').strip()
                total_slots = temp[1].strip()
                demand = current_row[6]
                restrictions = current_row[7]
            

            results.append({
                CRSColumn.ClassCode: class_code,
                CRSColumn.Class: crs_class,
                CRSColumn.Credits: credits,
                CRSColumn.Schedule: schedule,
                CRSColumn.Instructor: instructor,
                CRSColumn.Remarks: remarks,
                CRSColumn.EnlistingUnit: enlisting_unit,
                CRSColumn.AvailableSlots: available_slots,
                CRSColumn.TotalSlots: total_slots,
                CRSColumn.Demand: demand,
                CRSColumn.Restrictions: restrictions
            })
        return results


    def __filter_results(self, results, filter_columns: list) -> list:
        filtered_results = []
        for result in results:
            new_result = {}
            for cell, value in result.items():
                if cell in filter_columns:
                    new_result.update({cell: value})
            filtered_results.append(new_result)
        return filtered_results


    def fetch_all(self, search_term: str, schedule_text = False, columns=False):
        processed_link = self.__process_link(search_term, schedule_text)
        soup = self.__download_page(processed_link)
        results = self.__get_row_results(soup)
        if columns:
            results = self.__filter_results(results, columns)
        return results


    def tabulize(self, results:list):
        columns = list(map(lambda col: col.name, results[0].keys()))
        table = PrettyTable(field_names=columns)
        for result in results:
            table.add_row(list(result.values()))
        return table.get_string()
