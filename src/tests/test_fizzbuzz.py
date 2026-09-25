from fizzbuzz import fizzbuzz


def test_fizzbuzz_returns_number_as_string_for_one():
    # Arrange
    number = 1

    # Act
    result = fizzbuzz(number)

    # Assert
    assert result == "1"


def test_fizzbuzz_returns_fizz_for_three():
    # Arrange
    number = 3

    # Act
    result = fizzbuzz(number)

    # Assert
    assert result == "Fizz"


def test_fizzbuzz_returns_buzz_for_five():
    # Arrange
    number = 5

    # Act
    result = fizzbuzz(number)

    # Assert
    assert result == "Buzz"


def test_fizzbuzz_returns_fizzbuzz_for_fifteen():
    # Arrange
    number = 15

    # Act
    result = fizzbuzz(number)

    # Assert
    assert result == "FizzBuzz"


def test_fizzbuzz_returns_number_as_string_for_non_multiple():
    # Arrange
    number = 7

    # Act
    result = fizzbuzz(number)

    # Assert
    assert result == "7"
