COMMON_PASSWORDS = [
    "password",
    "123456",
    "12345678",
    "qwerty",
    "abc123",
    "password123",
    "admin",
    "letmein",
    "welcome",
    "iloveyou"
]

SPECIAL_CHARACTERS = "!@#$%^&*"


def check_password(password):
    score = 0
    suggestions = []

    if password.lower() in COMMON_PASSWORDS:
        score -= 3
        suggestions.append(
            "This is a commonly used password. Choose something more unique."
        )

    if len(password) < 8:
        suggestions.append("Use at least 8 characters.")
    elif len(password) >= 12:
        score += 2
    else:
        score += 1

    if any(char.isupper() for char in password):
        score += 1
    else:
        suggestions.append("Add an uppercase letter.")

    if any(char.islower() for char in password):
        score += 1
    else:
        suggestions.append("Add a lowercase letter.")

    if any(char.isdigit() for char in password):
        score += 1
    else:
        suggestions.append("Add a number.")

    if any(char in SPECIAL_CHARACTERS for char in password):
        score += 1
    else:
        suggestions.append("Add a special character.")

    if len(set(password)) < len(password) * 0.7:
        score -= 1
        suggestions.append("Avoid using too many repeated characters.")

    lower_password = password.lower()

    sequences = [
        "123",
        "234",
        "345",
        "456",
        "567",
        "678",
        "789",
        "abc",
        "bcd",
        "cde",
        "def",
        "qwe",
        "wer",
        "ert"
    ]

    if any(sequence in lower_password for sequence in sequences):
        score -= 1
        suggestions.append(
            "Avoid predictable sequences such as 123 or abc."
        )

    if score < 0:
        score = 0

    return score, suggestions


def get_strength(score):
    if score <= 2:
        return "WEAK"
    elif score <= 4:
        return "MEDIUM"
    else:
        return "STRONG"


print("================================")
print("   PASSWORD STRENGTH CHECKER")
print("================================")

password = input("\nEnter your password: ")

score, suggestions = check_password(password)
strength = get_strength(score)

print("\nPassword Score:", score, "/ 6")
print("Strength:", strength)

if suggestions:
    print("\nSuggestions:")

    for suggestion in suggestions:
        print("-", suggestion)
else:
    print("\nExcellent! Your password meets all requirements.")
