def get_date(date: dict) -> str | None:
    if date.get('date'):
        response = date.get('date')
        response = str(response).replace('-', '.').split('.')
        return '.'.join(reversed(response))
    if check_choise_field(date.get('date_day')) or check_choise_field(date.get('date_month')) or check_choise_field(date.get('date_year')):
        response = (check_choise_field(str(date.get('date_day'))) + '.' if check_choise_field(date.get('date_day')) else '?.') \
                   + (check_choise_field(str(date.get('date_month'))) + '.' if check_choise_field(date.get('date_month')) else '?.') \
                   + (check_choise_field(str(date.get('date_year'))) if check_choise_field(date.get('date_year')) else '?')
        return response
    return


def check_choise_field(data: str) -> str | None:
    if data == '00':
        return None
    return data
