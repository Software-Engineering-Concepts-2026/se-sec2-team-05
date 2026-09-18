from hypothesis import assume, given, settings, strategies as st

from tokens import hash_token, token_matches


@settings(max_examples=100)
@given(token=st.text(min_size=1))
def test_token_matches_the_hash_of_the_same_token(token):
    # Arrange
    stored_hash = hash_token(token)

    # If this fails, Hypothesis shrinks the token to the shortest failing value.

    # Act
    result = token_matches(token, stored_hash)

    # Assert
    assert result is True


@settings(max_examples=100)
@given(token=st.text(min_size=1), other_token=st.text(min_size=1))
def test_token_does_not_match_the_hash_of_a_different_token(token, other_token):
    # Arrange
    assume(token != other_token)
    stored_hash = hash_token(other_token)

    # Hypothesis shrinks a failing pair to the shortest distinct pair it can find.

    # Act
    result = token_matches(token, stored_hash)

    # Assert
    assert result is False
