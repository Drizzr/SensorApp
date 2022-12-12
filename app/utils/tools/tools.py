from flask import url_for, request


def referrerRequest(default='views.home'):
    return request.args.get('next', '') if request.args.get('next', '') and request.args.get('next', '') != 'None' else url_for(default)

