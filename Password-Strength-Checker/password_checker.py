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


def check_password(password):
    score = 0
    suggestions = []

    special_characters = "!@#$%^&*"

    # Check if password is commonly used
    if password.lower() in COMMON_PASSWORDS:
        suggestions.append("This is a common password. Choose something more unique.")
    else:
        score += 1

    # Check length
    if len(password) >= 8:
        score += 1
    else:
        suggestions.append("Use at least 8 characters")

    # Check uppercase
    if any(char.isupper() for char in password):
        score += 1
    else:
        suggestions.append("Add an uppercase letter")

    # Check lowercase
    if any(char.islower() for char in password):
        score += 1
    else:
        suggestions.append("Add a lowercase letter")

    # Check number
    if any(char.isdigit() for char in password):
        score += 1
    else:
        suggestions.append("Add a number")

    # Check special character
    if any(char in special_characters for char in password):
        score += 1
    else:
        suggestions.append("Add a special character")

    return score, suggestions


print("================================")
print("   PASSWORD STRENGTH CHECKER")
print("================================")

password = input("\nEnter your password: ")

score, suggestions = check_password(password)

print("\nScore:", score, "/ 6")

if score <= 2:
    print("Strength: WEAK")
elif score <= 4:
    print("Strength: MEDIUM")
else:
    print("Strength: STRONG")

if suggestions:
    print("\nSuggestions:")

    for suggestion in suggestions:
        print("-", suggestion)
else:
    print("\nExcellent! Your password meets all requirements.")
    