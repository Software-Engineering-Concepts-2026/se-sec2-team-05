"""Boundary and equivalence-partition tests for notes-service validation."""

import io

import pytest
from werkzeug.datastructures import FileStorage

from validation import MAX_FILE_BYTES, MAX_LENGTHS, validate_file, validate_metadata


VALID_FORM = {
    "title": "Data structures summary",
    "subject_name": "Data Structures",
    "subject_code": "CS201",
    "faculty": "ICT",
    "year_level": "2",
    "lesson": "Linked List",
}


@pytest.mark.parametrize("year_level, expected_year", [("1", 1), ("8", 8)])
def test_year_level_inclusive_boundaries_are_accepted(year_level, expected_year):
    # Arrange
    form = {**VALID_FORM, "year_level": year_level}

    # Act
    cleaned, errors = validate_metadata(form)

    # Assert
    assert errors == {}
    assert cleaned["year_level"] == expected_year


@pytest.mark.parametrize("year_level", ["0", "9"])
def test_year_level_values_just_outside_boundaries_are_rejected(year_level):
    # Arrange
    form = {**VALID_FORM, "year_level": year_level}

    # Act
    cleaned, errors = validate_metadata(form)

    # Assert
    assert "year_level" in errors
    assert "year_level" not in cleaned


@pytest.mark.parametrize("field, limit", sorted(MAX_LENGTHS.items()))
def test_each_field_accepts_its_maximum_length(field, limit):
    # Arrange
    value = "x" * limit
    form = {**VALID_FORM, field: value}

    # Act
    cleaned, errors = validate_metadata(form)

    # Assert
    assert errors == {}
    assert cleaned[field] == value


@pytest.mark.parametrize("field, limit", sorted(MAX_LENGTHS.items()))
def test_each_field_rejects_one_character_over_its_maximum(field, limit):
    # Arrange
    form = {**VALID_FORM, field: "x" * (limit + 1)}

    # Act
    cleaned, errors = validate_metadata(form)

    # Assert
    assert field in errors
    assert field not in cleaned


def _file_storage(content, filename="note.pdf", mimetype="application/pdf"):
    return FileStorage(
        stream=io.BytesIO(content),
        filename=filename,
        content_type=mimetype,
    )


def test_validate_file_rejects_zero_byte_boundary():
    # Arrange
    upload = _file_storage(b"")

    # Act
    content_type, size, error = validate_file(upload)

    # Assert
    assert content_type is None
    assert size is None
    assert error is not None


def test_validate_file_accepts_exactly_twenty_megabytes():
    # Arrange
    upload = _file_storage(b"x" * MAX_FILE_BYTES)

    # Act
    content_type, size, error = validate_file(upload)

    # Assert
    assert content_type == "application/pdf"
    assert size == MAX_FILE_BYTES
    assert error is None


def test_validate_file_rejects_one_byte_over_twenty_megabytes():
    # Arrange
    upload = _file_storage(b"x" * (MAX_FILE_BYTES + 1))

    # Act
    content_type, size, error = validate_file(upload)

    # Assert
    assert content_type is None
    assert size is None
    assert error is not None
