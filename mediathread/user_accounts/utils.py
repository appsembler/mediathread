from django.conf import settings

import mailchimp


def add_email_to_mailchimp_list(email_address, list_id, test_client=None, **kwargs):
    merge_vars_dict = {}

    for k, v in kwargs.items():
        merge_vars_dict[k.upper()] = v

    if test_client:
        ms = test_client
    else:
        ms = mailchimp.Mailchimp(settings.MAILCHIMP_API_KEY)

    # new version API require email as a struct with an email field.
    email_struct = {
        'email': email_address
        }

    result = ms.lists.subscribe(
        id=list_id,
        email=email_struct,
        merge_vars=merge_vars_dict,
        update_existing=True,
        double_optin=False)

    return True


def unsubscribe_user_from_list(email_address, list_id):
    ms = mailchimp.Mailchimp(settings.MAILCHIMP_API_KEY)
    ms.lists.unsubscribe(list_id, email_address)
    return True


def display_user(user):
    if user.first_name or user.last_name:
        return user.get_full_name()
    else:
        return user.username
