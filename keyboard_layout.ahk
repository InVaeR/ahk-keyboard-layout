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
; Благодаря этому можно использовать scan code и явно задавать сочетания с Shift.

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
; TODO: Добавить сообщение о смене раскладки

e::SwitchLayout("00000409")
r::SwitchLayout("00000419")

; Caps + L          | *CL   | Переключить раскладку
; переключение раскладки (Win+Space)
l::Send("# ")

; или если у вас Alt+Shift:
; l::Send("!+")


; SC034 — scan code физическая клавиша точки: . / >
; SC033 — scan code физическая клавиша запятой: , / <
;
; Физические scan code используются для символов, которые могут занимать
; разное положение в разных раскладках.

; ✨ Спецсимволы

; Caps + H          | ₽     | Вставить знак рубля: ₽
; Caps + .          | …     | Вставить многоточие: …
; Caps + Shift + .  | ≥     | Вставить знак «больше или равно»: ≥
; Caps + ,          | ,     | Вставить запятую: ,
; Caps + Shift + ,  | ≤     | Вставить знак «меньше или равно»: ≤
; Caps + 1          | «»    | Вставить кавычки «» и оставить курсор внутри
; Caps + Shift + 1  | °     | Вставить знак градуса: °
; Caps + 2          | ±     | Вставить знак «плюс-минус»: ±
; Caps + Shift + 2  | €     | Вставить знак евро: $
; Caps + 3          | #     | Вставить решётку: #
; Caps + Shift + 3  | ₽     | Вставить знак доллара: ₽
; Caps + 4          | ≈     | Вставить знак «примерно равно»: ≈
; Caps + Shift + 4  | $     | Вставить знак доллара: $
; Caps + 5          | ≠     | Вставить знак «не равно»: ≠
; Caps + Shift + 5  |       | 
; Caps + 6          | №     | Вставить знак номера: №
; Caps + Shift + 6  |       | 
; Caps + 7          | §     | Вставить знак параграфа: §
; Caps + Shift + 7  |       | 
; Caps + 8          | ©     | Вставить знак копирайта: ©
; Caps + Shift + 8  |       | 
; Caps + 9          | ®     | Вставить знак «зарегистрировано»: ®
; Caps + Shift + 9  |       | 
; Caps + 0          | ™     | Вставить знак товарного знака: ™
; Caps + Shift + 0  |       | 

h::SendText("₽")

SC034::SendText("…")
+SC034::SendText("≥")

SC033::SendText(",")
+SC033::SendText("≤")

1::Send("«»{Left}")
+1::SendText("°")
2::SendText("±")
+2::SendText("€")
3::SendText("#")
+3::SendText("$")
4::SendText("≈")
5::SendText("≠")
6::SendText("№")
7::SendText("§")
8::SendText("©")
9::SendText("®")
0::SendText("™")

; 🎛️ Управление системой 
; Caps + Q          | *QW   | Закрыть окно
; Caps + Shift + Q  | *QS   | Выключение компьютера
; Caps + F          | *FW   | Открыть на весь экран

q::Send("!{F4}")
+q::DllCall("PowrProf\SetSuspendState", "Int", 1, "Int", 0, "Int", 0)


; 🚀 Запуск приложений
; Caps + C          | *TE   | Открыть терминал PowerShell
; Caps + Shift + C  | *CA   | Открыть калькулятор
; Caps + V          | *VC   | Открыть VSCode
; Caps + B          | *BR   | Открыть браузер (домашняя страница)

; c::Run("powershell.exe -NoExit -Command `"cd '~'`"")
c::Run("powershell.exe -NoExit -Command `"cd 'C:\Users\WorkBook\Documents\Projects'`"")
v::Run("code.exe")
+c::Run("calc.exe")
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

; Клавиша `\ / |` TODO: найти сканкод клавиши и сделать втсавку / и \
; Caps + \              | \     | Вставить |
; Caps + Shift + \      | /     | Вставить \


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

; Переключает раскладку активного окна.
;
; locale:
;   00000409 — English (United States)
;   00000419 — Russian
SwitchLayout(locale) {
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
}