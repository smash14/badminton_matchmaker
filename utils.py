from datetime import datetime


def convert_name_to_variable(name):
    special_char_map = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('ß'): 'ss'}
    name = name.replace(" ", "_")
    name = name.lower()
    name = name.translate(special_char_map)
    return name


def convert_date_string_list_to_datetime(string_list, return_first_entry=False):
    date_list = []
    for datetime_str in string_list:
        datetime_object = convert_date_string_to_datetime(datetime_str)
        date_list.append(datetime_object)
    if return_first_entry:
        return date_list[0]
    return date_list


def convert_date_string_to_datetime(string_date):
    if string_date == "":
        return None
    datetime_object = datetime.strptime(string_date, '%Y-%m-%d')
    return datetime_object

