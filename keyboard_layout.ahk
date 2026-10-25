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

; Caps + L          | *CL   | Переключить раскладку
; переключение раскладки (Win+Space)
l::Send("# ")

; или если Alt+Shift:
; l::Send("!+")

; Caps + Shift + L  | *CLL  | Поменять раскладку написанного текста
+l::
{
    savedClip := ClipboardAll()
    A_Clipboard := ""

    ; Копируем выделенное
    Send("^c")
    if !ClipWait(0.5) {          ; ничего не выделено — выходим
        A_Clipboard := savedClip
        return
    }

    ; Меняем раскладку и вставляем обратно
    A_Clipboard := ConvertLayout(A_Clipboard)
    Send("^v")
    Sleep(150)                   ; даём целевому приложению забрать текст
    A_Clipboard := savedClip
}

; SC034 — scan code физическая клавиша точки: . / >
; SC033 — scan code физическая клавиша запятой: , / <
;
; Физические scan code используются для символов, которые могут занимать
; разное положение в разных раскладках.

; Цифровой ряд

; Caps + 1          | °     | 
; Caps + 2          | «»    | Вставить кавычки «» и оставить курсор внутри
; Caps + 3          | #     | 
; Caps + 4          | $     | 
; Caps + 5          | ₽     | 
; Caps + 6          | ^     | 
; Caps + 7          | ?     | 
; Caps + 8          | ∞     | 
; Caps + 9          | ✓     | 
; Caps + 0          | ✗     | 
; Caps + =          | ±     | 
; Caps + Shift + 1  | ≈     | 
; Caps + Shift + 2  | @     | 
; Caps + Shift + 3  | №     | 
; Caps + Shift + 4  |       | 
; Caps + Shift + 5  |       | 
; Caps + Shift + 6  |       | 
; Caps + Shift + 7  | ¿     | 
; Caps + Shift + 8  | ©     | 
; Caps + Shift + 9  | ®     | 
; Caps + Shift + 0  | ™     | 
; Caps + Shift + =  | ≠     | 

1::SendText("°")
2::Send("«»{Left}")
3::SendText("#")
4::SendText("$")
5::SendText("₽")
6::SendText("^")
7::SendText("?")
8::SendText("∞")
9::SendText("✓")
0::SendText("✗")
=::SendText("±")

+1::SendText("≈")
+2::SendText("@")
+3::SendText("№")
+7::SendText("¿")
+8::SendText("©")
+9::SendText("®")
+0::SendText("™")
+=::SendText("≠")


; Caps + H          | ₽     | 
; Caps + ,          | ,     | 
; Caps + Shift + ,  | ≤     | 
; Caps + .          | …     | 
; Caps + Shift + .  | ≥     | 

h::SendText("₽")

SC034::SendText("…")
+SC034::SendText("≥")

SC033::SendText(",")
+SC033::SendText("≤")


; Языконезависимые символы ; : ' " [ ] { }
; Caps + ;          | ;     | 
; Caps + Shift + ;  | :     | 
; Caps + Shift + NumpadDot | .     | Вставить точку
; Caps + [          | [     | 
; Caps + Shift + [  | {     | 
; Caps + ]          | ]     | 
; Caps + Shift + ]  | }     | 

; SC027 — scan code физической клавиши `;` (в RU-раскладке там «ж»).
SC027::SendText(";")
+SC027::SendText(":")

; SC01A — scan code физической клавиши `[` (в RU-раскладке там «х»).
; SC01B — scan code физической клавиши `]` (в RU-раскладке там «ъ»).
SC01A::SendText("[")
+SC01A::SendText("{")
SC01B::SendText("]")
+SC01B::SendText("}")

; Точка с Numpad (RU точка на основном блоке недоступна).
+NumpadDot::SendText(".")

; 🎛️ Управление системой 
; Caps + Q          | *QW   | Закрыть окно
; Caps + Shift + Q  | *QS   | Выключение компьютера
; Caps + F          | *FW   | Открыть на весь экран
; Caps + G          | *CW   | Центрировать окно
; Caps + Shift + G  | *G720 | Установить размер окна 1280x720

q::Send("!{F4}")
+q::DllCall("PowrProf\SetSuspendState", "Int", 1, "Int", 0, "Int", 0)

f::{
    ; Переключает разворот активного окна на весь экран и обратно.
    if WinGetStyle("A") & 0x1000000
        WinRestore("A")
    else
        WinMaximize("A")
}

g::{
    ; Разместить окно по центру экрана
    WinGetPos(, , &winW, &winH, "A")
    screenW := A_ScreenWidth
    screenH := A_ScreenHeight
    newX := (screenW - winW) / 2
    newY := (screenH - winH) / 2
    WinMove(newX, newY, , , "A")
}

+g::{
    ; Установить размер окна 1280x720
    WinMove(, , 1280, 720, "A")
}

; 🚀 Запуск приложений
; Caps + C          | *CMD | Открыть терминал PowerShell
; Caps + Shift + C  | *CALC | Открыть калькулятор
; Caps + V          | *VSC  | Открыть VSCode
; Caps + Shift + V  | *VPN  | Открыть VPN приложение
; Caps + B          | *BR   | Открыть браузер

c::Run("powershell.exe -NoExit -Command `"cd '~'`"")
v::Run("code.exe")
+c::Run("calc.exe")

+v::{
    ; TODO: вставьте команду запуска вашего VPN-приложения, например:
    ; Run("C:\Program Files\VPN\VPN.exe")
}

b::Run("http://")
; e::Run("explorer.exe") 
; +e::Run("shell:Downloads")


; ✍️ Типографика
; SC00C — физическая клавиша минуса: - / _

; Caps + -              | –     | Вставить короткое тире (en dash): –
; Caps + Shift + -      | —     | Вставить длинное тире (em dash): —
; Caps + Space          | *NBS  | Вставить неразрывный пробел (U+00A0)
; Caps + Shift + Space  | *THIN | Вставить тонкий пробел (U+2009)

SC00C::SendText("–")
+SC00C::SendText("—")
Space::Send("{U+00A0}")
+Space::Send("{U+2009}")

; Caps + \              | \     | Вставить \
; Caps + Shift + \      | /     | Вставить /

; SC02B — scan code физической клавиши `\` над Enter.
SC02B::SendText("/")
+SC02B::SendText("\")


; 📋 Работа со строками
; Caps + Y          | *YL   | Скопировать текущую строку в буфер обмена
; Caps + Shift + Y  | *YA   | Выделить и скопировать весь текст
; Caps + D          | *DL   | Дублировать текущую строку
; Caps + Shift + D  | *DEL  | Удалить текущую строку

y::{
    ; Выделяем строку вместе с переносом и копируем её в буфер обмена.
    Send("{Home}")
    Send("{Shift down}{Down}{Shift up}")
    Send("^c")
    Send("{Home}")
}

+y::{
    Send("^a")
    Send("^c")
}

d::{
    ; Сохраняем текущий буфер обмена, чтобы вернуть его после вставки копии.
    savedClipboard := ClipboardAll()

    Send("{Home}")
    Send("{Shift down}{Down}{Shift up}")
    Send("^c")
    if !ClipWait(1)
        return

    Send("{End}")
    Send("{Enter}")
    Send("^v")
    Sleep(50)

    A_Clipboard := savedClipboard
}

+d::{
    ; Выделяем строку вместе с переносом и удаляем её без использования буфера обмена.
    Send("{Home}")
    Send("{Shift down}{Down}{Shift up}")
    Send("{Delete}")
}


; ↑ Стрелки
; Caps + Up         | ↑     | Вставить стрелку вверх: ↑
; Caps + Down       | ↓     | Вставить стрелку вниз: ↓
; Caps + Left       | ←     | Вставить стрелку влево: ←
; Caps + Right      | →     | Вставить стрелку вправо: →

Up::SendText("↑")
Down::SendText("↓")
Left::SendText("←")
Right::SendText("→")


; ▦ Псевдографика — NumPad
; Цифровой блок используется как панель для построения рамок и таблиц.

; Caps + Numpad7    | ┌     | Вставить верхний левый угол: ┌
; Caps + Numpad8    | ┬     | Вставить верхнее соединение: ┬
; Caps + Numpad9    | ┐     | Вставить верхний правый угол: ┐
; Caps + Numpad4    | ├     | Вставить левое соединение: ├
; Caps + Numpad5    | ┼     | Вставить центральное соединение: ┼
; Caps + Numpad6    | ┤     | Вставить правое соединение: ┤
; Caps + Numpad1    | └     | Вставить нижний левый угол: └
; Caps + Numpad2    | ┴     | Вставить нижнее соединение: ┴
; Caps + Numpad3    | ┘     | Вставить нижний правый угол: ┘
; Caps + Numpad0    | ─     | Вставить горизонтальную линию: ─
; Caps + NumpadDot  | │     | Вставить вертикальную линию: │

Numpad7::SendText("┌")
Numpad8::SendText("┬")
Numpad9::SendText("┐")

Numpad4::SendText("├")
Numpad5::SendText("┼")
Numpad6::SendText("┤")

Numpad1::SendText("└")
Numpad2::SendText("┴")
Numpad3::SendText("┘")

Numpad0::SendText("─")
NumpadDot::SendText("│")


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
;
; locale:
;   00000409 — English (United States)
;   00000419 — Russian
; label — отображаемое название раскладки в сообщении о смене.
SwitchLayout(locale, label := "") {
    ; Загружаем или активируем запрошенную раскладку клавиатуры.
    keyboardLayout := DllCall(
        "LoadKeyboardLayout",
        "Str", locale,
        "UInt", 1,
        "Ptr"
    )

    ; WM_INPUTLANGCHANGEREQUEST = 0x0050.
    ; Отправляем активному окну запрос на изменение языка ввода.
    PostMessage(0x0050, 0, keyboardLayout, , "A")

    if (label != "")
        ShowLayoutMessage(label)
}

; Функция конвертации раскладки
ConvertLayout(text) {
    ; Карта физических клавиш: позиция N в enMap соответствует позиции N в ruMap.
    ; Порядок: ` + цифровой ряд, верхний ряд, home-ряд, нижний ряд.
    ; Сначала все unshifted-слои, затем все shifted-слои.
    static enMap := "``1234567890-="        ; ` 1 2 3 4 5 6 7 8 9 0 - =
                  . "qwertyuiop[]"          ; q w e r t y u i o p [ ]
                  . "asdfghjkl;'"           ; a s d f g h j k l ; '
                  . "zxcvbnm,./"            ; z x c v b n m , . /
                  . "~!@#$%^&*()_+"         ; ~ ! @ # $ % ^ & * ( ) _ +
                  . "QWERTYUIOP{}"
                  . "ASDFGHJKL:`""
                  . "ZXCVBNM<>?"

    static ruMap := "ё1234567890-="
                  . "йцукенгшщзхъ"
                  . "фывапролджэ"
                  . "ячсмитьбю."
                  . "Ё!`"№;%:?*()_+"
                  . "ЙЦУКЕНГШЩЗХЪ"
                  . "ФЫВАПРОЛДЖЭ"
                  . "ЯЧСМИТЬБЮ,"

    out := ""
    for char in StrSplit(text) {
        if (p := InStr(ruMap, char, true))       ; true = учитывать регистр
            out .= SubStr(enMap, p, 1)
        else if (p := InStr(enMap, char, true))
            out .= SubStr(ruMap, p, 1)
        else
            out .= char                          ; пробелы, Enter, эмодзи и пр.
    }
    return out
}