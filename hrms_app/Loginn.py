import bcrypt
import hashlib
from django.contrib.auth.hashers import check_password, identify_hasher
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def _is_bcrypt_hash(self, hash_string):
        """
        Check if a string is a valid bcrypt hash format using bcrypt's own validation.
        This is more reliable than hardcoded prefixes as it uses bcrypt library's logic.
        """
        if not hash_string:
            return False
        
        try:
            # bcrypt.checkpw will raise ValueError if hash format is invalid
            # We use a dummy password to test format validity
            # This is safe because we only care about format validation, not matching
            bcrypt.checkpw(b"dummy", hash_string.encode('utf-8'))
            return True
        except ValueError:
            # Invalid bcrypt format
            return False
        except Exception:
            # Other errors (shouldn't happen with valid bcrypt, but being safe)
            return False

    def _is_argon2_hash(self, hash_string):
        """
        Check if a string is a valid argon2 hash format.
        More comprehensive than just checking prefixes.
        """
        if not hash_string:
            return False
        
        # Argon2 format: $argon2{variant}${params}${salt}${hash}
        # Variants: i (argon2i), d (argon2d), id (argon2id)
        argon2_pattern = hash_string.split('

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            raise serializers.ValidationError("Username and password are required.")
        
        try:
            user = ERPUser.objects.get(username=username)
        except ERPUser.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
        
        stored_password = user.password.strip()
        
        if not stored_password:
            raise serializers.ValidationError("Invalid credentials.")
        
        # Detect hash format automatically
        hash_format = self._detect_hash_format(stored_password)
        
        try:
            # Handle different hash formats based on detection
            if hash_format == 'django':
                if check_password(password, stored_password):
                    data["user"] = user
                    return data
            
            elif hash_format == 'bcrypt':
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    data["user"] = user
                    return data
            
            elif hash_format == 'md5':
                if hashlib.md5(password.encode('utf-8')).hexdigest().lower() == stored_password.lower():
                    data["user"] = user
                    return data
            
            elif hash_format == 'sha1':
                if hashlib.sha1(password.encode('utf-8')).hexdigest().lower() == stored_password.lower():
                    data["user"] = user
                    return data
            
            elif hash_format == 'sha256':
                if hashlib.sha256(password.encode('utf-8')).hexdigest().lower() == stored_password.lower():
                    data["user"] = user
                    return data
            
            elif hash_format == 'argon2':
                # Try Django's check_password as fallback for argon2
                if check_password(password, stored_password):
                    data["user"] = user
                    return data
            
            elif hash_format == 'scrypt':
                raise serializers.ValidationError("Scrypt format detected but not supported. Please reset your password.")
            
            elif hash_format == 'unknown_structured':
                raise serializers.ValidationError("Unknown hash format detected. Please reset your password.")
            
            else:  # unknown or unsupported format
                raise serializers.ValidationError("Unsupported password format. Please reset your password.")
        
        except Exception as e:
            # Log the error for debugging purposes (optional)
            # logger.warning(f"Password validation error for user {username}: {str(e)}")
            pass
        
        # If we reach here, the password didn't match or there was an error
        raise serializers.ValidationError("Invalid credentials."))
        
        if len(argon2_pattern) < 4:
            return False
        
        if not argon2_pattern[1].startswith('argon2'):
            return False
        
        # Check if it's a known variant
        variant = argon2_pattern[1]
        valid_variants = ['argon2i', 'argon2d', 'argon2id']
        
        return variant in valid_variants

    def _is_scrypt_hash(self, hash_string):
        """
        Check if a string is a valid scrypt hash format.
        """
        if not hash_string:
            return False
        
        # Basic scrypt format validation
        return (hash_string.startswith('$scrypt

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            raise serializers.ValidationError("Username and password are required.")
        
        try:
            user = ERPUser.objects.get(username=username)
        except ERPUser.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
        
        stored_password = user.password.strip()
        
        if not stored_password:
            raise serializers.ValidationError("Invalid credentials.")
        
        # Method 1: Try Django's identify_hasher first (most reliable)
        try:
            identify_hasher(stored_password)
            # If we reach here, it's a valid Django hash format
            if check_password(password, stored_password):
                data["user"] = user
                return data
            else:
                raise serializers.ValidationError("Invalid credentials.")
        except (ValueError, DjangoValidationError):
            # Not a Django hash, try other formats
            pass
        
        # Method 2: Check for bcrypt format using bcrypt's own validation
        if self._is_bcrypt_hash(stored_password):
            try:
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    data["user"] = user
                    return data
                else:
                    raise serializers.ValidationError("Invalid credentials.")
            except (ValueError, TypeError) as e:
                raise serializers.ValidationError("Invalid credentials.")
        
        # Method 3: Check for other common hash formats
        try:
            # Check for plain MD5 (32 hex characters)
            if len(stored_password) == 32 and all(c in '0123456789abcdefABCDEF' for c in stored_password):
                if hashlib.md5(password.encode('utf-8')).hexdigest().lower() == stored_password.lower():
                    data["user"] = user
                    return data
            
            # Check for SHA1 (40 hex characters)
            elif len(stored_password) == 40 and all(c in '0123456789abcdefABCDEF' for c in stored_password):
                if hashlib.sha1(password.encode('utf-8')).hexdigest().lower() == stored_password.lower():
                    data["user"] = user
                    return data
            
            # Check for SHA256 (64 hex characters)
            elif len(stored_password) == 64 and all(c in '0123456789abcdefABCDEF' for c in stored_password):
                if hashlib.sha256(password.encode('utf-8')).hexdigest().lower() == stored_password.lower():
                    data["user"] = user
                    return data
            
            # Check for argon2 variants (more comprehensive)
            elif stored_password.startswith(('$argon2i$', '$argon2d$', '$argon2id$')):
                # These should be caught by Django's check_password, but adding as fallback
                if check_password(password, stored_password):
                    data["user"] = user
                    return data
            
            # Check for scrypt format
            elif stored_password.startswith('$scrypt$'):
                # Note: You'd need to implement scrypt checking if needed
                raise serializers.ValidationError("Scrypt format detected but not supported. Please reset your password.")
            
            # Check for other formats that might exist
            elif '$' in stored_password and len(stored_password.split('$')) >= 3:
                # This might be a custom or unknown hash format
                # You can add specific handlers here if needed
                raise serializers.ValidationError("Unknown hash format detected. Please reset your password.")
        
        except Exception as e:
            # Log the error for debugging purposes (optional)
            # logger.warning(f"Password validation error for user {username}: {str(e)}")
            raise serializers.ValidationError("Invalid credentials.")
        
        # If we reach here, the password format is unsupported or password doesn't match
        raise serializers.ValidationError("Invalid credentials.")) and 
                len(hash_string.split('

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            raise serializers.ValidationError("Username and password are required.")
        
        try:
            user = ERPUser.objects.get(username=username)
        except ERPUser.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
        
        stored_password = user.password.strip()
        
        if not stored_password:
            raise serializers.ValidationError("Invalid credentials.")
        
        # Method 1: Try Django's identify_hasher first (most reliable)
        try:
            identify_hasher(stored_password)
            # If we reach here, it's a valid Django hash format
            if check_password(password, stored_password):
                data["user"] = user
                return data
            else:
                raise serializers.ValidationError("Invalid credentials.")
        except (ValueError, DjangoValidationError):
            # Not a Django hash, try other formats
            pass
        
        # Method 2: Check for bcrypt format using bcrypt's own validation
        if self._is_bcrypt_hash(stored_password):
            try:
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    data["user"] = user
                    return data
                else:
                    raise serializers.ValidationError("Invalid credentials.")
            except (ValueError, TypeError) as e:
                raise serializers.ValidationError("Invalid credentials.")
        
        # Method 3: Check for other common hash formats
        try:
            # Check for plain MD5 (32 hex characters)
            if len(stored_password) == 32 and all(c in '0123456789abcdefABCDEF' for c in stored_password):
                if hashlib.md5(password.encode('utf-8')).hexdigest().lower() == stored_password.lower():
                    data["user"] = user
                    return data
            
            # Check for SHA1 (40 hex characters)
            elif len(stored_password) == 40 and all(c in '0123456789abcdefABCDEF' for c in stored_password):
                if hashlib.sha1(password.encode('utf-8')).hexdigest().lower() == stored_password.lower():
                    data["user"] = user
                    return data
            
            # Check for SHA256 (64 hex characters)
            elif len(stored_password) == 64 and all(c in '0123456789abcdefABCDEF' for c in stored_password):
                if hashlib.sha256(password.encode('utf-8')).hexdigest().lower() == stored_password.lower():
                    data["user"] = user
                    return data
            
            # Check for argon2 variants (more comprehensive)
            elif stored_password.startswith(('$argon2i$', '$argon2d$', '$argon2id$')):
                # These should be caught by Django's check_password, but adding as fallback
                if check_password(password, stored_password):
                    data["user"] = user
                    return data
            
            # Check for scrypt format
            elif stored_password.startswith('$scrypt$'):
                # Note: You'd need to implement scrypt checking if needed
                raise serializers.ValidationError("Scrypt format detected but not supported. Please reset your password.")
            
            # Check for other formats that might exist
            elif '$' in stored_password and len(stored_password.split('$')) >= 3:
                # This might be a custom or unknown hash format
                # You can add specific handlers here if needed
                raise serializers.ValidationError("Unknown hash format detected. Please reset your password.")
        
        except Exception as e:
            # Log the error for debugging purposes (optional)
            # logger.warning(f"Password validation error for user {username}: {str(e)}")
            raise serializers.ValidationError("Invalid credentials.")
        
        # If we reach here, the password format is unsupported or password doesn't match
        raise serializers.ValidationError("Invalid credentials."))) >= 4)

    def _detect_hash_format(self, hash_string):
        """
        Detect the hash format of a given string.
        Returns the format type or None if unknown.
        """
        if not hash_string:
            return None
        
        # Try Django formats first
        try:
            identify_hasher(hash_string)
            return 'django'
        except (ValueError, DjangoValidationError):
            pass
        
        # Check bcrypt
        if self._is_bcrypt_hash(hash_string):
            return 'bcrypt'
        
        # Check argon2 (might not be Django format)
        if self._is_argon2_hash(hash_string):
            return 'argon2'
        
        # Check scrypt
        if self._is_scrypt_hash(hash_string):
            return 'scrypt'
        
        # Check for plain hash formats based on characteristics
        clean_hash = hash_string.strip()
        if clean_hash and all(c in '0123456789abcdefABCDEF' for c in clean_hash):
            if len(clean_hash) == 32:
                return 'md5'
            elif len(clean_hash) == 40:
                return 'sha1'
            elif len(clean_hash) == 64:
                return 'sha256'
        
        # Check for other structured formats
        if '

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            raise serializers.ValidationError("Username and password are required.")
        
        try:
            user = ERPUser.objects.get(username=username)
        except ERPUser.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
        
        stored_password = user.password.strip()
        
        if not stored_password:
            raise serializers.ValidationError("Invalid credentials.")
        
        # Method 1: Try Django's identify_hasher first (most reliable)
        try:
            identify_hasher(stored_password)
            # If we reach here, it's a valid Django hash format
            if check_password(password, stored_password):
                data["user"] = user
                return data
            else:
                raise serializers.ValidationError("Invalid credentials.")
        except (ValueError, DjangoValidationError):
            # Not a Django hash, try other formats
            pass
        
        # Method 2: Check for bcrypt format using bcrypt's own validation
        if self._is_bcrypt_hash(stored_password):
            try:
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    data["user"] = user
                    return data
                else:
                    raise serializers.ValidationError("Invalid credentials.")
            except (ValueError, TypeError) as e:
                raise serializers.ValidationError("Invalid credentials.")
        
        # Method 3: Check for other common hash formats
        try:
            # Check for plain MD5 (32 hex characters)
            if len(stored_password) == 32 and all(c in '0123456789abcdefABCDEF' for c in stored_password):
                if hashlib.md5(password.encode('utf-8')).hexdigest().lower() == stored_password.lower():
                    data["user"] = user
                    return data
            
            # Check for SHA1 (40 hex characters)
            elif len(stored_password) == 40 and all(c in '0123456789abcdefABCDEF' for c in stored_password):
                if hashlib.sha1(password.encode('utf-8')).hexdigest().lower() == stored_password.lower():
                    data["user"] = user
                    return data
            
            # Check for SHA256 (64 hex characters)
            elif len(stored_password) == 64 and all(c in '0123456789abcdefABCDEF' for c in stored_password):
                if hashlib.sha256(password.encode('utf-8')).hexdigest().lower() == stored_password.lower():
                    data["user"] = user
                    return data
            
            # Check for argon2 variants (more comprehensive)
            elif stored_password.startswith(('$argon2i$', '$argon2d$', '$argon2id$')):
                # These should be caught by Django's check_password, but adding as fallback
                if check_password(password, stored_password):
                    data["user"] = user
                    return data
            
            # Check for scrypt format
            elif stored_password.startswith('$scrypt$'):
                # Note: You'd need to implement scrypt checking if needed
                raise serializers.ValidationError("Scrypt format detected but not supported. Please reset your password.")
            
            # Check for other formats that might exist
            elif '$' in stored_password and len(stored_password.split('$')) >= 3:
                # This might be a custom or unknown hash format
                # You can add specific handlers here if needed
                raise serializers.ValidationError("Unknown hash format detected. Please reset your password.")
        
        except Exception as e:
            # Log the error for debugging purposes (optional)
            # logger.warning(f"Password validation error for user {username}: {str(e)}")
            raise serializers.ValidationError("Invalid credentials.")
        
        # If we reach here, the password format is unsupported or password doesn't match
        raise serializers.ValidationError("Invalid credentials.") in hash_string and len(hash_string.split('

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            raise serializers.ValidationError("Username and password are required.")
        
        try:
            user = ERPUser.objects.get(username=username)
        except ERPUser.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
        
        stored_password = user.password.strip()
        
        if not stored_password:
            raise serializers.ValidationError("Invalid credentials.")
        
        # Method 1: Try Django's identify_hasher first (most reliable)
        try:
            identify_hasher(stored_password)
            # If we reach here, it's a valid Django hash format
            if check_password(password, stored_password):
                data["user"] = user
                return data
            else:
                raise serializers.ValidationError("Invalid credentials.")
        except (ValueError, DjangoValidationError):
            # Not a Django hash, try other formats
            pass
        
        # Method 2: Check for bcrypt format using bcrypt's own validation
        if self._is_bcrypt_hash(stored_password):
            try:
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    data["user"] = user
                    return data
                else:
                    raise serializers.ValidationError("Invalid credentials.")
            except (ValueError, TypeError) as e:
                raise serializers.ValidationError("Invalid credentials.")
        
        # Method 3: Check for other common hash formats
        try:
            # Check for plain MD5 (32 hex characters)
            if len(stored_password) == 32 and all(c in '0123456789abcdefABCDEF' for c in stored_password):
                if hashlib.md5(password.encode('utf-8')).hexdigest().lower() == stored_password.lower():
                    data["user"] = user
                    return data
            
            # Check for SHA1 (40 hex characters)
            elif len(stored_password) == 40 and all(c in '0123456789abcdefABCDEF' for c in stored_password):
                if hashlib.sha1(password.encode('utf-8')).hexdigest().lower() == stored_password.lower():
                    data["user"] = user
                    return data
            
            # Check for SHA256 (64 hex characters)
            elif len(stored_password) == 64 and all(c in '0123456789abcdefABCDEF' for c in stored_password):
                if hashlib.sha256(password.encode('utf-8')).hexdigest().lower() == stored_password.lower():
                    data["user"] = user
                    return data
            
            # Check for argon2 variants (more comprehensive)
            elif stored_password.startswith(('$argon2i$', '$argon2d$', '$argon2id$')):
                # These should be caught by Django's check_password, but adding as fallback
                if check_password(password, stored_password):
                    data["user"] = user
                    return data
            
            # Check for scrypt format
            elif stored_password.startswith('$scrypt$'):
                # Note: You'd need to implement scrypt checking if needed
                raise serializers.ValidationError("Scrypt format detected but not supported. Please reset your password.")
            
            # Check for other formats that might exist
            elif '$' in stored_password and len(stored_password.split('$')) >= 3:
                # This might be a custom or unknown hash format
                # You can add specific handlers here if needed
                raise serializers.ValidationError("Unknown hash format detected. Please reset your password.")
        
        except Exception as e:
            # Log the error for debugging purposes (optional)
            # logger.warning(f"Password validation error for user {username}: {str(e)}")
            raise serializers.ValidationError("Invalid credentials.")
        
        # If we reach here, the password format is unsupported or password doesn't match
        raise serializers.ValidationError("Invalid credentials."))) >= 3:
            return 'unknown_structured'
        
        return 'unknown'

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            raise serializers.ValidationError("Username and password are required.")
        
        try:
            user = ERPUser.objects.get(username=username)
        except ERPUser.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
        
        stored_password = user.password.strip()
        
        if not stored_password:
            raise serializers.ValidationError("Invalid credentials.")
        
        # Method 1: Try Django's identify_hasher first (most reliable)
        try:
            identify_hasher(stored_password)
            # If we reach here, it's a valid Django hash format
            if check_password(password, stored_password):
                data["user"] = user
                return data
            else:
                raise serializers.ValidationError("Invalid credentials.")
        except (ValueError, DjangoValidationError):
            # Not a Django hash, try other formats
            pass
        
        # Method 2: Check for bcrypt format using bcrypt's own validation
        if self._is_bcrypt_hash(stored_password):
            try:
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    data["user"] = user
                    return data
                else:
                    raise serializers.ValidationError("Invalid credentials.")
            except (ValueError, TypeError) as e:
                raise serializers.ValidationError("Invalid credentials.")
        
        # Method 3: Check for other common hash formats
        try:
            # Check for plain MD5 (32 hex characters)
            if len(stored_password) == 32 and all(c in '0123456789abcdefABCDEF' for c in stored_password):
                if hashlib.md5(password.encode('utf-8')).hexdigest().lower() == stored_password.lower():
                    data["user"] = user
                    return data
            
            # Check for SHA1 (40 hex characters)
            elif len(stored_password) == 40 and all(c in '0123456789abcdefABCDEF' for c in stored_password):
                if hashlib.sha1(password.encode('utf-8')).hexdigest().lower() == stored_password.lower():
                    data["user"] = user
                    return data
            
            # Check for SHA256 (64 hex characters)
            elif len(stored_password) == 64 and all(c in '0123456789abcdefABCDEF' for c in stored_password):
                if hashlib.sha256(password.encode('utf-8')).hexdigest().lower() == stored_password.lower():
                    data["user"] = user
                    return data
            
            # Check for argon2 variants (more comprehensive)
            elif stored_password.startswith(('$argon2i$', '$argon2d$', '$argon2id$')):
                # These should be caught by Django's check_password, but adding as fallback
                if check_password(password, stored_password):
                    data["user"] = user
                    return data
            
            # Check for scrypt format
            elif stored_password.startswith('$scrypt$'):
                # Note: You'd need to implement scrypt checking if needed
                raise serializers.ValidationError("Scrypt format detected but not supported. Please reset your password.")
            
            # Check for other formats that might exist
            elif '$' in stored_password and len(stored_password.split('$')) >= 3:
                # This might be a custom or unknown hash format
                # You can add specific handlers here if needed
                raise serializers.ValidationError("Unknown hash format detected. Please reset your password.")
        
        except Exception as e:
            # Log the error for debugging purposes (optional)
            # logger.warning(f"Password validation error for user {username}: {str(e)}")
            raise serializers.ValidationError("Invalid credentials.")
        
        # If we reach here, the password format is unsupported or password doesn't match
        raise serializers.ValidationError("Invalid credentials.")