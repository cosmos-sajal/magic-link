import json
from django.urls import reverse

from helpers.misc_helper import get_random_string
from helpers.cache_adapter import CacheAdapter
from helpers.domain_helper import DomainHelper
from user.constants import MAGIC_LINK_CONSTANTS


class MagicLinkService():
    def __does_token_exist(self, token):
        """
        Returns a boolean if the token exist in
        the system

        Args:
            token (str)
        """

        key = self.get_cache_key(token)
        cache_adapter = CacheAdapter()
        val = cache_adapter.get(key)

        return (val is not None)

    
    def __get_magic_link_token(self):
        retry_count = 0

        while True:
            token = get_random_string(8)
            if not self.__does_token_exist(token):
                return token

            retry_count = retry_count + 1

            if retry_count > 5:
                break

        return None
    
    def __get_link(self, request, token):
        """
        Returns a link

        Arguments:
            token {str}
        """

        domain_helper = DomainHelper(request)
        return domain_helper.get_domain_url() + \
            "/api/v1/user/magic_link/sign_in/" + \
            token + "/"
    
    def get_default_redirect_url(self):
        """
        Returns a default url which the user
        will be taken to in case of Magic Link
        gets expired
        """

        return "/api/v1/home/"
    
    def get_cache_key(self, token):
        """
        Returns the cache key to be seached
        in Cache

        Arguments:
            token {str}
        """

        return MAGIC_LINK_CONSTANTS['token_cache_key_prefix'] + token
    
    def generate_magic_link(self, request, user, redirect_link):
        """
        Generates the magic link for the user
        and returns it
        """

        token = self.__get_magic_link_token()
        if token is None:
            return {
                'is_success': False,
                'error': 'Not able to generate unique link'
            }
        
        key = self.get_cache_key(token)
        value = {
            'user_id': user.id,
            'redirect_link': redirect_link
        }
        cache_adapter = CacheAdapter()
        cache_adapter.set(
            key,
            json.dumps(value),
            MAGIC_LINK_CONSTANTS['expiry']
        )

        link = self.__get_link(request, token)
        content = MAGIC_LINK_CONSTANTS['email_body']
        content = content.replace('magic_link_placeholder', link)

        return {
            'is_success': True,
            'content': content,
            'email': user.email
        }

    def set_cookies_in_response(self, request, response, token):
        domain_helper = DomainHelper(request)
        domain = domain_helper.get_domain_url()
        response.set_cookie(
            'token',
            token,
            domain=domain_helper.get_cookie_domain(domain)
        )

        return response
