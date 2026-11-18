# Ядро агента (C)

Ядро собирается в динамическую библиотеку: `sentry_core.dll` в Windows, `libsentry_core.dylib` в macOS,
`libsentry_core.so` в Linux. Первая функция появляется на паре 2.

| Файл | Что в нём |
|---|---|
| `core.h` | структура данных и объявление функции |
| `core_info.c` | сведения о системе и время её работы |
| `show_info.c` | проверка ядра из C |

В Windows сборка библиотеки из x64 Native Tools Command Prompt: `cl /nologo /W4 /LD core_info.c /Fe:sentry_core.dll`.
