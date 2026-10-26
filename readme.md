# AutoHotkey Keyboard Layout

## Описание

Скрипт для **AutoHotkey v2** создаёт дополнительный слой клавиатуры: `Caps Lock` перестаёт переключать регистр и используется как модификатор. В сочетании с ним доступны:

- дата и время, переключение раскладок RU/EN и конвертация уже набранного текста;
- спецсимволы, типографика и псевдографика для рамок и таблиц на цифровом блоке;
- навигация по тексту, работа со строками и буфером обмена;
- управление окнами и быстрый запуск приложений.

Полная карта клавиатуры и список всех комбинаций: [cheatsheet/keyboard_map.svg](cheatsheet/keyboard_map.svg), [cheatsheet/cheatsheet.md](cheatsheet/cheatsheet.md) и [cheatsheet/cheatsheet.html](cheatsheet/cheatsheet.html).

## Требования

- Windows 10+;
- AutoHotkey v2.0 или новее.

## Установка

### 1. Установить AutoHotkey v2

Выберите один из вариантов.

**Официальный установщик (рекомендуется)**

1. Скачайте AutoHotkey v2 со страницы [autohotkey.com](https://www.autohotkey.com/).
2. Запустите установщик и выберите версию **v2**.
3. После установки файлы `.ahk` будут открываться двойным щелчком.

**Через winget**

```powershell
winget install --id AutoHotkey.AutoHotkey -e
```

Проверить, что v2 установлена:

```powershell
Test-Path "$env:ProgramFiles\AutoHotkey\v2\AutoHotkey64.exe"
```

Команда должна вывести `True`.

### 2. Скачать проект

```powershell
git clone https://github.com/InVaeR/ahk-keyboard-layout.git
cd ahk-keyboard-layout
```

### 3. Запустить скрипт

Откройте `keyboard_layout.ahk` двойным щелчком или запустите из PowerShell:

```powershell
& "$env:ProgramFiles\AutoHotkey\v2\AutoHotkey64.exe" .\keyboard_layout.ahk
```

После запуска в области уведомлений появится значок AutoHotkey. Завершить скрипт можно сочетанием `Ctrl + Alt + Q`.

### 4. Добавить в автозагрузку

Нажмите `Win + R`, введите `shell:startup` и нажмите `Enter` — откроется папка автозагрузки. Поместите в неё ярлык на `keyboard_layout.ahk`.

Или создайте ярлык командой PowerShell из папки проекта:

```powershell
$shell = New-Object -ComObject WScript.Shell
$script = (Resolve-Path ".\keyboard_layout.ahk").Path
$shortcut = $shell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\keyboard_layout.lnk")
$shortcut.TargetPath = $script
$shortcut.WorkingDirectory = Split-Path $script
$shortcut.Save()
```

## Схема скрипта

```ahk
#Requires AutoHotkey v2.0
#SingleInstance Force

; cheatsheet-title: Кастомная раскладка клавиатуры

; CapsLock используется исключительно как дополнительный модификатор.
; Обычное переключение регистра через CapsLock отключено.
SetCapsLockState("AlwaysOff")

; ==============================================================================
; ГОРЯЧИЕ КЛАВИШИ CAPSLOCK
; ==============================================================================

; Все горячие клавиши ниже работают только при физическом удержании CapsLock.
#HotIf GetKeyState("CapsLock", "P")

; 📅 Дата и время
; Caps + T          | *D    | Вставить дату в формате ДД.ММ.ГГГГ
; Caps + Shift + T  | *DT   | Вставить дату и время в формате ДД.ММ.ГГГГ ЧЧ:ММ
; Caps + A          | *DA   | Вставить компактную дату в формате ГГГГММДД

t::SendText(FormatTime(, "dd.MM.yyyy"))
+t::SendText(FormatTime(, "dd.MM.yyyy HH:mm"))
a::SendText(FormatTime(, "yyyyMMdd"))

; 🌐 Переключение раскладки
; Caps + E          | EN    | Переключить раскладку на English (US)
; Caps + R          | RU    | Переключить раскладку на Russian

e::SwitchLayout("00000409", "English (US)")
r::SwitchLayout("00000419", "Русская")

; ...

; Завершение области действия условия.
; Следующие горячие клавиши уже не требуют удержания CapsLock.

#HotIf

; ⚙ Сервис
; Ctrl + Alt + Q    | Завершить работу скрипта

^!q::ExitApp()


; ==============================================================================
; ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
; ==============================================================================

; Показывает временное всплывающее сообщение о смене раскладки.
ShowLayoutMessage(text) {
    TrayTip(text)
    SetTimer(() => TrayTip(), -1500)
}

; Переключает раскладку активного окна.
SwitchLayout(locale, label := "") {
    ; ...
}

; Функция конвертации раскладки
ConvertLayout(text) {
    ; ...
}
```
