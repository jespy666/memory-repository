from fastapi import HTTPException, status


class UserNotFoundException(HTTPException):
    """
    Exception template for case if user not found in DB.
    """
    
    def __init__(self) -> None:
        detail = 'User not found'
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class AccessDeniedException(HTTPException):
    """
    Exception template for case if protected endpoint.
    """

    def __init__(self) -> None:
        detail = 'Access denied'
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class InvalidTokenException(HTTPException):
    """
    Exception template for case if JWT token is missing, invalid, expired etc.
    """

    def __init__(self) -> None:
        detail = 'Token is invalid or missing'
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class NonExistedAttributeException(HTTPException):
    """
    Exception template for find object in DB. If given field does not exist.
    """

    def __init__(self) -> None:
        detail = 'Non-existed attribute'
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class NonActiveUserException(HTTPException):
    """
    Exception template for find object in DB. If given field does not exist.
    """

    def __init__(self) -> None:
        detail = 'Account is inactive, check your email'
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )