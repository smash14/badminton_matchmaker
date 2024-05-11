from datetime import datetime


def convert_name_to_variable(name):
    special_char_map = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('ß'): 'ss'}
    name = name.replace(" ", "_")
    name = name.lower()
    name = name.translate(special_char_map)
    return name


def convert_date_string_list_to_datetime(string_list, return_first_entry=False):
    """
    [string] -> [datetime]
    convert list of string to list of datetime
    :param string_list: list with date/time entries of type string
    :param return_first_entry:
    :return: list with date/time entries of type datetime
    """
    date_list = []
    for datetime_str in string_list:
        datetime_object = convert_date_string_to_datetime(datetime_str)
        date_list.append(datetime_object)
    if return_first_entry:
        return date_list[0]
    return date_list


def convert_datetime_list_to_string(datetime_list):
    """
    [datetime] -> [string]
    convert list of string to list of datetime
    :param datetime_list: list with date/time entries of type datetime
    :return: list with date/time entries of type string
    """
    string_list = []
    for datetime_entry in datetime_list:
        datetime_string = convert_datetime_to_string(datetime_entry)
        string_list.append(datetime_string)
    return string_list


def convert_date_string_to_datetime(string_date):
    """
    string -> datetime
    convert string to datetime object
    :param string_date: date/time string of format YYYY-mm-dd
    :return: datetime object
    """
    if string_date == "":
        return None
    datetime_object = datetime.strptime(string_date, '%Y-%m-%d')
    return datetime_object


def convert_datetime_to_string(datetime_object):
    """
    datetime -> string
    convert datetime object to string type
    :param datetime_object: datetime object
    :return: date/time string of format YYYY-mm-dd
    """
    datetime_string = datetime_object.strftime('%Y-%m-%d')
    return datetime_string
