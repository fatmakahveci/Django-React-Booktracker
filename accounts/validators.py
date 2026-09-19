from django.core.validators import RegexValidator

validate_user_name = RegexValidator(
    regex=r"\A[\w.-]{4,24}\Z",
    message="Use 4–24 letters, numbers, dots, underscores or hyphens.",
)
