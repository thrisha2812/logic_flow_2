def calculate_average(numbers):
    # BUG: This will crash with ZeroDivisionError if list is empty
    return sum(numbers) / len(numbers)

# Test cases
print(calculate_average([10, 20, 30])) # Should pass
print(calculate_average([]))           # Should fail