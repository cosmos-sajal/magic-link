from helpers.domain_helper import DomainHelper


class CookiesService():
    def __init__(self):
        self.token_name = 'token'

    def set_cookies_in_response(self, request, response, token):
        domain_helper = DomainHelper(request)
        domain = domain_helper.get_domain_url()
        response.set_cookie(
            self.token_name,
            token,
            domain=domain_helper.get_cookie_domain(domain)
        )

        return response

    def delete_cookies_in_response(self, response):
        response.delete_cookie(self.token_name)

        return response
