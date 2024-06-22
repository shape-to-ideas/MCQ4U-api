from datetime import date

__all__ = ['current_date', 'epoch_in_milliseconds', 'date_to_epoch']


def current_date():
    return date.today()


def date_to_epoch(date_object: date):
    return date_object.strftime('%s')


def epoch_in_milliseconds(epoch_val: str):
    return int(epoch_val) * 1000
