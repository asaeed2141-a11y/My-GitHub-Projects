import random
import string


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

    if len(password) > 0 and len(set(password)) < len(password) * 0.7:
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


def generate_password(length):
    characters = (
        string.ascii_letters +
        string.digits +
        SPECIAL_CHARACTERS
    )

    password = ""

    for _ in range(length):
        password += random.choice(characters)

    return password


def check_password_mode():
    print("\n================================")
    print("      PASSWORD CHECKER")
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


def generate_password_mode():
    print("\n================================")
    print("      PASSWORD GENERATOR")
    print("================================")

    while True:
        try:
            length = int(input("\nEnter password length (8-50): "))

            if 8 <= length <= 50:
                break

            print("Please enter a length between 8 and 50.")

        except ValueError:
            print("Please enter a valid number.")

    password = generate_password(length)

    print("\nGenerated Password:")
    print(password)


def main():
    while True:
        print("\n================================")
        print("     PASSWORD SECURITY TOOL")
        print("================================")

        print("\n1. Check password strength")
        print("2. Generate secure password")
        print("3. Exit")

        choice = input("\nChoose an option: ")

        if choice == "1":
            check_password_mode()

        elif choice == "2":
            generate_password_mode()

        elif choice == "3":
            print("\nGoodbye!")
            break

        else:
            print("\nInvalid option. Please choose 1, 2, or 3.")


main()