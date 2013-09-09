from django.test import TestCase
from django.conf import settings

from mediathread.user_accounts.utils import add_email_to_mailchimp_list

import mailchimp
from mock import patch, MagicMock


mock_mailchimp = MagicMock(spec=mailchimp.Mailchimp)

"""
Exceptions
"""


class ApiKeyNotValid(Exception):
    pass


class ListIdNotValid(Exception):
    pass

"""
Test Cases
"""


@patch("mailchimp.Mailchimp", mock_mailchimp)
class MailChimpTest(TestCase):
    def setUp(self):
        self.test_mailchimp_data = {
            'list_id': settings.MAILCHIMP_REGISTRATION_LIST_ID,
            'api_key': settings.MAILCHIMP_API_KEY
            }

        print 'Using list id: %s' % self.test_mailchimp_data['list_id']
        print 'Using api key: %s' % self.test_mailchimp_data['api_key']
        self.test_mailchimp_fields = {
            u'EMAIL': u'mediathreadtest@mediathread.com',
            u'FNAME': u'Tester',
            u'LNAME': u'Su',
            u'HEAR': u'Conference',
            u'ORG': u'Appsembler',
            u'TITLE': u'student'
            }

        #self.ms = mailchimp.Mailchimp(self.test_mailchimp_data['api_key'])
        self.ms = mock_mailchimp(self.test_mailchimp_data['api_key'])
        self.ms.lists.subscribe.return_value = {
            u'email': u'mediathreadtest@mediathread.com',
            u'leid': u'75399789',
            u'euid': u'acab2f8087'
        }

    def test_subscribe_user(self):
        # subscribe user
        test_data = self.test_mailchimp_data
        test_fields = self.test_mailchimp_fields

        test_fields_arg = dict([(k.lower(), v) for k, v in test_fields.items()])
        result = add_email_to_mailchimp_list(test_fields['EMAIL'], test_data['list_id'], test_client=self.ms, **test_fields_arg)
        self.assertEqual(result, True)
