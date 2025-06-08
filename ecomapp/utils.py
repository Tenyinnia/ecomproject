from .models import CustomUser

def get_user_avatar(user):
    # Handle Tutor
    if hasattr(user, 'customuser'):
        profile = user.customuser
        return profile.get_avatar_url() or profile.get_initials()

    # Handle Student

    # Default fallback if no profile
    return user.username[:2].upper()
