class ApiException(Exception):
    # for now just call like ApiException(resp), and it will put the whole response as the message
    def __init__(self, resp):
        self.data = resp.data
        super().__init__(resp)
