def is_multiple(n, factor):
    return n % factor == 0


def fizzbuzz(number):
    if is_multiple(number, 15):
        return "FizzBuzz"
    if is_multiple(number, 3):
        return "Fizz"
    if is_multiple(number, 5):
        return "Buzz"
    return str(number)
