from helpers.domain_helper import DomainHelper


class CookiesService():
    def set_cookies_in_response(self, request, response, token):
        domain_helper = DomainHelper(request)
        domain = domain_helper.get_domain_url()
        response.set_cookie(
            'token',
            token,
            domain=domain_helper.get_cookie_domain(domain)
        )

        return response
