# AutoHotkey Keyboard Layout

## Описание

Скрипт для AutoHotKey содает дополнительную раскладку клавиатуры. Скрипт выключает функциоал клавиши `Caps Lock` и добавляет клавишам дополнительный функциана в содчитании с `Caps Lock`.

## Установка

Скачать файлы:

```
git clone https://github.com/InVaeR/ahk-keyboard-layout.git
cd ahk-keyboard-layout
```

Для добавления в автозагрузку:

Нажмите `Win + R`, введите в появившемся окне `shell:startup`, нажмите `Enter` положить ярлык в папку автозапуска.

Или командой:

```
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\keyboard_layout.lnk")
$shortcut.TargetPath = "keyboard_layout.ahk"
$shortcut.Save()
```
