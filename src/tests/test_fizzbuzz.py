from src.fizzbuzz import fizzbuzz


def test_fizzbuzz_returns_number_as_string_for_one():
    # Arrange
    number = 1

    # Act
    result = fizzbuzz(number)

    # Assert
    assert result == "1"
