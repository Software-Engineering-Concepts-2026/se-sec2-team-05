# Saboteur Testing Journal: `year_level` Upper Boundary

## โค้ดที่ตั้งใจทำให้ผิด

จงใจสร้าง Bug แบบ off-by-one ในเงื่อนไขตรวจสอบขอบเขตบนของ `year_level`

```diff
- if not MIN_YEAR_LEVEL <= year <= MAX_YEAR_LEVEL:
+ if not MIN_YEAR_LEVEL <= year < MAX_YEAR_LEVEL:
```

ผลของการเปลี่ยนแปลงคือ `year_level=8` ซึ่งเป็นค่าขอบเขตบนที่ถูกต้อง ถูกปฏิเสธเป็น Error

## Test ที่ควร Fail และ Test ที่ Fail จริง

Test ที่ควรจับ Bug คือ:

```text
src/tests/test_notes_validation_boundary.py::test_year_level_inclusive_boundaries_are_accepted[8-8]
```

Test นี้ตรวจว่า `year_level="8"` ต้องผ่าน และค่าที่ทำความสะอาดแล้วต้องเป็นเลข `8`

ผลจริงคือ Test นี้ Fail ตามคาด ส่วน Test อื่นยังผ่าน

```text
1 failed, 79 passed in 1.99s
```

## ผลลัพธ์ก่อน Revert

คำสั่งที่ใช้:

```powershell
.\.venv\Scripts\python.exe -m pytest src/tests -v
```

ข้อความ Failure เต็มของ Test ที่ตรวจพบ Bug:

```text
___________ test_year_level_inclusive_boundaries_are_accepted[8-8] ____________

year_level = '8', expected_year = 8

    @pytest.mark.parametrize("year_level, expected_year", [("1", 1), ("8", 8)])
    def test_year_level_inclusive_boundaries_are_accepted(year_level, expected_year):
        # Arrange
        form = {**VALID_FORM, "year_level": year_level}

        # Act
        cleaned, errors = validate_metadata(form)

        # Assert
>       assert errors == {}
E       AssertionError: assert {'year_level': 'ต้องอยู่ระหว่าง 1-8'} == {}
E         Left contains 1 more item:
E         {'year_level': 'ต้องอยู่ระหว่าง 1-8'}

src/tests/test_notes_validation_boundary.py:30: AssertionError
======================== 1 failed, 79 passed in 1.99s =========================
```

## Test ใหม่ที่เพิ่ม

ไม่มีการเพิ่ม Test ใหม่ เพราะ Test Boundary เดิมมีกรณี `year_level=8` อยู่แล้ว และสามารถตรวจพบ Saboteur ได้ทันที

## ผลลัพธ์หลัง Revert

Revert เงื่อนไขกลับเป็น:

```python
if not MIN_YEAR_LEVEL <= year <= MAX_YEAR_LEVEL:
```

จากนั้นรัน Test ทั้งชุดซ้ำ ผลลัพธ์คือ:

```text
80 passed in 1.90s
```

สรุป: Test สามารถตรวจจับ Bug แบบ off-by-one ที่ขอบเขตบนของ `year_level` ได้ และ Production code ถูกคืนกลับสู่สถานะเดิมแล้ว
