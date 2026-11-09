from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Django's standard user fields stored in the accounts_user table."""

    class Meta:
        db_table = "accounts_user"
