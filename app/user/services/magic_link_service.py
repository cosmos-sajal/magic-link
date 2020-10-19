import json

from helpers.misc_helper import get_random_string
from helpers.cache_adapter import CacheAdapter
from helpers.domain_helper import DomainHelper
from user.constants import MAGIC_LINK_CONSTANTS


class MagicLinkService():
    def __init__(self, request, user, redirect_link):
        self.user = user
        self.redirect_link = redirect_link
        self.request = request
    
    def __get_cache_key(self, token):
        """
        Returns the cache key to be seached
        in Cache

        Arguments:
            token {str}
        """

        return MAGIC_LINK_CONSTANTS['token_cache_key_prefix'] + token
    
    def __does_token_exist(self, token):
        """
        Returns a boolean if the token exist in
        the system

        Args:
            token (str)
        """

        key = self.__get_cache_key(token)
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
    
    def __get_link(self, token):
        """
        Returns a link

        Arguments:
            token {str}
        """

        domain_helper = DomainHelper(self.request)
        return domain_helper.get_domain_url() + \
            "/api/v1/magic_link/sign_in/" + \
            token + "/"
    
    def generate_magic_link(self):
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
        
        key = self.__get_cache_key(token)
        value = {
            'user': self.user.id,
            'redirect_link': self.redirect_link
        }
        cache_adapter = CacheAdapter()
        cache_adapter.set(
            key,
            json.dumps(value),
            MAGIC_LINK_CONSTANTS['expiry']
        )

        link = self.__get_link(token)
        content = MAGIC_LINK_CONSTANTS['email_body']
        content = content.replace('magic_link_placeholder', link)

        return {
            'is_success': True,
            'content': content,
            'email': self.user.email
        }
