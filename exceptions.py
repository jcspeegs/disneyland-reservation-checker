class Error(Exception):
    ''' Base class for custom exceptions'''

    pass


class StatusCodeError(Error):
    ''' Requests response status code indicates an error'''

    def __init__(self, status_code, message='Bad status code'):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.status_code}->{self.message}'


class EmptyResponseError(Error):
    ''' Requests response is empty''' 

    def __init__(self, message= 'Calendar query response empty.'):
        self.message = message
        super().__init__(self.message)
