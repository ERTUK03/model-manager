from app.core.security import hash_password, verify_password


def test_hash_is_not_plain_text_and_verifies():
    hashed = hash_password("Haslo123")
    assert hashed != "Haslo123"
    assert verify_password("Haslo123", hashed)
    assert not verify_password("Inne123", hashed)


def test_same_password_gives_different_hashes():
    assert hash_password("Haslo123") != hash_password("Haslo123")
