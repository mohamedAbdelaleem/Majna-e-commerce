from django.contrib.auth.tokens import PasswordResetTokenGenerator



class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    pass


def clean_email(email: str):
    """Make the email insensitive"""
    email = email.lower()
    try:
        email_name, domain_part = email.strip().rsplit("@", 1)
        email_name = email_name.replace(".", "")
        email = email_name + "@" + domain_part
    except ValueError:
        pass

    return email
