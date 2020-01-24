import zope.interface
import logging

from certbot import interfaces, errors
from certbot.plugins import dns_common

from certbot_plugin_domreg import domreg_api


logger = logging.getLogger(__name__)


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Domreg."""

    description = 'Obtain certificates using a DNS TXT record (if you are using Domreg for DNS).'

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(add,default_propagation_seconds=6)
        add("credentials", help="Domreg credentials file.")


    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge with ' + \
               'scripting the Domreg web portal.'

    def _setup_credentials(self):
        self._configure_file('credentials',
                             'Absolute path to Domreg credentials file')
        dns_common.validate_file_permissions(self.conf('credentials'))
        self.credentials = self._configure_credentials(
            'credentials',
            'Domreg credentials file',
            {
                'passwd': 'Domreg password'
            }
        )

    def _perform(self, domain, validation_name, validation):
        error = domreg_api.add_txt_record(self.credentials.conf('passwd'),domain, validation_name, validation)
        if error is not None:
            raise errors.PluginError('An error occurred adding the DNS TXT record: {0}'.format(error))
        


    def _cleanup(self, domain, validation_name, validation):
        error = domreg_api.del_txt_record(self.credentials.conf('passwd'),domain, validation_name, validation)
        if error is not None:
            logger.warn('Unable to find or delete the DNS TXT record: %s', error)
