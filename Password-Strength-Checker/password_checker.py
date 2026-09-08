password = input("Enter your password: ")

score = 0
special_characters = "!@#$%^&*"

if len(password) >= 8:
    score += 1

if any(char.isupper() for char in password):
    score += 1

if any(char.islower() for char in password):
    score += 1

if any(char.isdigit() for char in password):
    score += 1

if any(char in special_characters for char in password):
    score += 1

print("\nPassword Score:", score, "/ 5")

if score <= 2:
    print("Strength: WEAK")
elif score <= 4:
    print("Strength: MEDIUM")
else:
    print("Strength: STRONG")