current_user_role = None


def access_control(roles):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if current_user_role not in roles:
                raise PermissionError(
                    f'Доступ закрыт. У роли "{current_user_role}" '
                    f'не достаточно прав.')
            return func(*args, **kwargs)
        return wrapper
    return decorator


@access_control(roles=['admin', 'moderator'])
def protected_function():
    return 'Доступ разрешён'


try:
    current_user_role = 'admin'
    result = protected_function()
    assert result == 'Доступ разрешён', (
        'Ошибка: роль "admin" должна иметь доступ'
    )
    current_user_role = 'moderator'
    result = protected_function()
    assert result == 'Доступ разрешён', (
        'Ошибка: роль "moderator" должна иметь доступ'
    )

    current_user_role = 'user'
    try:
        protected_function()
        assert False, 'Ошибка: роль "user" не должна иметь доступ'
    except PermissionError as e:
        assert str(e) == 'Доступ закрыт. У роли "user" не достаточно прав.', \
            'Неверное сообщение об ошибке'

    current_user_role = None
    try:
        protected_function()
        assert False, 'Ошибка: роль "None" не должна иметь доступ'
    except PermissionError as e:
        assert str(e) == 'Доступ закрыт. У роли "None" не достаточно прав.', \
            'Неверное сообщение об ошибке'

    print('Все тесты пройдены успешно!')

except AssertionError as e:
    print(f'Тест провален: {e}')
