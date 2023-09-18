import requests
import json


def check_if_year_valid(year):
    if (len(str(year)) != 2) or (type(year) is not int):
        raise Exception("The entered year must be a two digit integer, like 22 or 23")


def check_if_semester_valid(semester):
    if semester not in ["fall", "spring"]:
        raise Exception("The entered semester must either be 'fall' or 'spring'")


def validate_input(year, semester):
    check_if_year_valid(year)
    check_if_semester_valid(semester)


def get_semester_to_URL_number(semester):
    check_if_semester_valid(semester)
    semester_to_url_mapping = {"fall": "8", "spring": "2"}
    return semester_to_url_mapping[semester]


def return_all_department_mnemonics(year, semester):
    # Input handling
    semester = semester.lower()  # ensures "Spring" is treated the same as "SPRING" and "spring"
    validate_input(year, semester)

    # URL building
    base_url = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula" \
               ".IScript_ClassSearchOptions?institution=UVA01"

    term_parameter = "&term=1" + str(year) + get_semester_to_URL_number(semester)
    full_url = base_url + term_parameter

    # requesting data
    r = requests.get(full_url)
    json_data = r.json()

    # JSON parsing
    list_of_search_fields = json_data["subjects"]

    mnemonics_list = []
    for entry in list_of_search_fields:
        mnemonics_list.append(entry["subject"])

    with open("department_mnemonics.json", "w") as outfile:
        json.dump(mnemonics_list, outfile)

    return mnemonics_list


def return_all_courses_from_department(year, semester, department):
    # Input handling
    semester = semester.lower()  # ensures "Spring" is treated the same as "SPRING" and "spring"
    validate_input(year, semester)
    # TODO: should probably validate "department" somehow - maybe make sure it exists in the list returned by
    #  return_all_department_mnemonics() above?

    # URL building
    base_url = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula" \
               ".IScript_ClassSearch?institution=UVA01"

    term_parameter = "&term=1" + str(year) + get_semester_to_URL_number(semester)
    subject_parameter = "&subject=" + department

    base_url = base_url + term_parameter + subject_parameter

    current_page = 1  # used to handle getting several pages of json data
    page_parameter = "&page=" + str(current_page)

    # requesting data
    r = requests.get(base_url + page_parameter)
    json_data = r.json()

    data_to_save = []

    # json parsing
    for entry in json_data:
        if not entry:
            break

        chunk = {}
        chunk["index"] = entry["index"]
        chunk["subject"] = entry["subject"]
        chunk["catalog_nbr"] = entry["catalog_nbr"]

        if int(chunk["catalog_nbr"]) > 4999:
            break

        chunk["descr"] = entry["descr"]
        chunk["topic"] = entry["topic"]
        chunk["instructor"] = entry["instructors"][0]["name"]
        chunk["units"] = entry["units"]

        chunk["class_capacity"] = entry["class_capacity"]
        chunk["wait_cap"] = entry["wait_cap"]

        if entry["meetings"] == []:
            continue

        chunk["days"] = entry["meetings"][0]["days"]

        chunk["start_time"] = entry["meetings"][0]["start_time"]
        chunk["end_time"] = entry["meetings"][0]["end_time"]
        chunk["facility_descr"] = entry["meetings"][0]["facility_descr"]

        chunk["acad_career"] = entry["acad_career"]
        chunk["campus_descr"] = entry["campus_descr"]
        chunk["instruction_mode_descr"] = entry["instruction_mode_descr"]

        data_to_save.append(chunk)

    with open(department + "_" + semester + str(year) + ".json", "w") as outfile:
        json.dump(data_to_save, outfile)

