#!/usr/bin/env python3
"""Генератор карты клавиатуры и шпаргалок из комментариев AutoHotkey v2.

Поддерживаемый формат комментариев
---------------------------------

    ; cheatsheet-title: Кастомная раскладка клавиатуры

    ; Дата
    ; Caps + D          | *DT  | *DT: Вставить дату ДД.ММ.ГГГГ

    ; Спецсимволы
    ; Caps + .          | …    | Вставить многоточие
    ; Caps + Shift + .  | ≥    | Вставить знак «больше или равно»

    ; Сервис
    ; Ctrl + Alt + Q    | Завершить работу скрипта

Правила:
* строка без ``|`` перед таблицей задаёт раздел для HTML и Markdown;
* три колонки означают: комбинация | метка на карте | описание;
* две колонки добавляют комбинацию только в полный список;
* ``*`` перед меткой создаёт пояснение под картой, но не рисуется на клавише;
* на карте нижний правый символ означает Caps, верхний правый — Caps + Shift.

Примеры запуска
---------------

    python cheatsheet/generate_cheatsheet.py keyboard_layout.ahk
    python cheatsheet/generate_cheatsheet.py keyboard_layout.ahk --mode image
    python cheatsheet/generate_cheatsheet.py keyboard_layout.ahk --image-format both
    python cheatsheet/generate_cheatsheet.py keyboard_layout.ahk --theme both

"""
from __future__ import annotations

import argparse
import html
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Sequence


# =============================================================================
# МОДЕЛИ ДАННЫХ
# =============================================================================

@dataclass
class Entry:
    """Одно назначение клавиши или одна служебная комбинация."""

    key: str
    label: str
    group: str

    # Содержимое двух слоёв физической клавиши.
    caps: str = ""
    caps_shift: str = ""

    # Короткие подписи, которые непосредственно рисуются на клавише.
    caps_label: str = ""
    caps_shift_label: str = ""

    # Нужно ли вынести расшифровку метки в блок пояснений под картой.
    caps_note: bool = False
    caps_shift_note: bool = False

    # Полные описания для таблиц и пояснений.
    description: str = ""
    shift_description: str = ""

    # Для комбинаций, которые не относятся к слою Caps.
    combo: str = ""
    action: str = ""
    keyboard: bool = True


@dataclass(frozen=True)
class Theme:
    """Цвета SVG. Меняйте этот блок для настройки внешнего вида."""

    page_bg: str = "#11111b"
    key_bg: str = "#292a36"
    key_border: str = "#45475a"
    key_text: str = "#8f91a8"
    main_text: str = "#cdd6f4"
    muted_text: str = "#a6adc8"
    accent: str = "#f5a65b"
    note_bg: str = "#1e1e2e"
    note_border: str = "#313244"


@dataclass(frozen=True)
class RenderSettings:
    """Геометрия SVG-карты.

    Все значения задаются в пикселях, кроме ширины
    элементов LAYOUT, которая указывается в относительных единицах u.
    """

    unit: int = 64
    key_height: int = 64
    key_gap: int = 6
    row_gap: int = 7
    function_row_extra_gap: int = 17

    margin_x: int = 34
    keyboard_top: int = 96
    corner_radius: int = 7

    title_y: int = 43
    subtitle_y: int = 69

    notes_gap_top: int = 56
    notes_columns: int = 3
    note_height: int = 54
    note_gap: int = 8
    bottom_padding: int = 34

    # Геометрия карточек пояснений.
    # Левая область предназначена для меток DT, DTM, DTA и т. п.
    note_padding_x: int = 14

    # Широкая область под метку: DTM и более длинные обозначения
    # теперь не упираются в основной текст карточки.
    note_marker_width: int = 92

    # Дополнительное свободное место между меткой и правым текстовым блоком.
    note_content_gap: int = 18

    # Приблизительная ширина символа используется для вычисления того,
    # сколько текста реально помещается справа. Уменьшите значение, если
    # хотите выводить больше текста до многоточия.
    note_average_char_width: float = 6.0
    note_min_text_chars: int = 24

    # Ширина серой левой части активной клавиши.
    active_key_label_width: int = 31


THEME = Theme()
RENDER = RenderSettings()


# Светлая тема для печати. Тот же набор полей, что и у THEME.
def light_theme() -> Theme:
    return Theme(
        page_bg="#ffffff",
        key_bg="#ececf1",
        key_border="#c9c9d6",
        key_text="#6a6a76",
        main_text="#1f1f28",
        muted_text="#45454f",
        accent="#c4540f",
        note_bg="#f4f4f7",
        note_border="#d7d7e0",
    )


LIGHT_THEME = light_theme()


# =============================================================================
# ФИЗИЧЕСКАЯ РАСКЛАДКА
# =============================================================================

# Каждый элемент: (внутреннее имя, видимая подпись, ширина в единицах u).
# ("GAP", "", 0.65) создаёт пустой промежуток и ничего не рисует.
# Чтобы добавить ещё один разрыв, просто вставьте GAP в нужное место строки.
LAYOUT: list[list[tuple[str, str, float]]] = [
    [
        ("Esc", "Esc", 1), ("GAP", "", 1),
        ("F1", "F1", 1), ("F2", "F2", 1), ("F3", "F3", 1), ("F4", "F4", 1),
        ("GAP", "", .45),
        ("F5", "F5", 1), ("F6", "F6", 1), ("F7", "F7", 1), ("F8", "F8", 1),
        ("GAP", "", .45),
        ("F9", "F9", 1), ("F10", "F10", 1), ("F11", "F11", 1), ("F12", "F12", 1),
        ("GAP", "", .20),
        ("PrintScreen", "PrtSc", 1), ("ScrollLock", "ScrLk", 1), ("Pause", "Pause", 1),
    ],
    [
        ("Backtick", "`", 1), ("1", "1", 1), ("2", "2", 1), ("3", "3", 1),
        ("4", "4", 1), ("5", "5", 1), ("6", "6", 1), ("7", "7", 1),
        ("8", "8", 1), ("9", "9", 1), ("0", "0", 1),
        ("Minus", "-", 1), ("Equal", "=", 1), ("Backspace", "Backspace", 2),
        ("GAP", "", .20),
        ("Insert", "Ins", 1), ("Home", "Home", 1), ("PgUp", "PgUp", 1),
        ("GAP", "", .20),
        ("NumLock", "Num", 1), ("NumpadDiv", "/", 1),
        ("NumpadMult", "*", 1), ("NumpadSub", "-", 1),
    ],
    [
        ("Tab", "Tab", 1.5), ("Q", "Q", 1), ("W", "W", 1), ("E", "E", 1),
        ("R", "R", 1), ("T", "T", 1), ("Y", "Y", 1), ("U", "U", 1),
        ("I", "I", 1), ("O", "O", 1), ("P", "P", 1),
        ("LBracket", "[", 1), ("RBracket", "]", 1), ("Backslash", "\\", 1.5),
        ("GAP", "", .20),
        ("Delete", "Del", 1), ("End", "End", 1), ("PgDn", "PgDn", 1),
        ("GAP", "", .20),
        ("Numpad7", "7", 1), ("Numpad8", "8", 1),
        ("Numpad9", "9", 1), ("NumpadAdd", "+", 1),
    ],
    [
        ("CapsLock", "Caps", 1.75), ("A", "A", 1), ("S", "S", 1),
        ("D", "D", 1), ("F", "F", 1), ("G", "G", 1), ("H", "H", 1),
        ("J", "J", 1), ("K", "K", 1), ("L", "L", 1),
        ("Semicolon", ";", 1), ("Quote", "'", 1), ("Enter", "Enter", 2.25),
        ("GAP", "", .2), ("GAP", "", 1), ("GAP", "", 1), ("GAP", "", 1),
        ("GAP", "", .2),
        ("Numpad4", "4", 1), ("Numpad5", "5", 1), ("Numpad6", "6", 1),
    ],
    [
        ("LShift", "Shift", 2.25), ("Z", "Z", 1), ("X", "X", 1),
        ("C", "C", 1), ("V", "V", 1), ("B", "B", 1),
        ("N", "N", 1), ("M", "M", 1),
        ("Comma", ",", 1), ("Period", ".", 1), ("Slash", "/", 1),
        ("RShift", "Shift", 2.75), ("GAP", "", 1), ("GAP", "", .2),
        ("Up", "↑", 1), ("GAP", "", 1), ("GAP", "", .2),
        ("Numpad1", "1", 1), ("Numpad2", "2", 1),
        ("Numpad3", "3", 1), ("NumpadEnter", "Enter", 1),
    ],
    [
        ("LCtrl", "Ctrl", 1.4), ("LWin", "Win", 1.2), ("LAlt", "Alt", 1.2),
        ("Space", "Space", 6.2),
        ("RAlt", "Alt", 1.2), ("RWin", "Win", 1.2),
        ("Menu", "Menu", 1.2), ("RCtrl", "Ctrl", 1.4),
        ("GAP", "", .20),
        ("Left", "←", 1), ("Down", "↓", 1), ("Right", "→", 1),
        ("GAP", "", .20),
        ("Numpad0", "0", 2), ("NumpadDot", ".", 1),
    ],
]

# Клавиши, которые занимают несколько рядов по вертикали (двухрядная высота).
# Ключ — внутреннее имя клавиши, значение — число рядов, которые она перекрывает.
TALL_KEYS = {
    "NumpadAdd": 2,
    "NumpadEnter": 2,
}

# Альтернативные обозначения одной и той же физической клавиши.
ALIASES = {
    "SC033": "Comma",
    "SC034": "Period",
    ",": "Comma",
    ".": "Period",
    "Numpad/": "NumpadDiv",
    "Numpad*": "NumpadMult",
    "Numpad-": "NumpadSub",
    "Numpad+": "NumpadAdd",
    "NumpadDecimal": "NumpadDot",
}

SYMBOLIC_KEYS = {
    "-": "Minus",
    "=": "Equal",
    ",": "Comma",
    ".": "Period",
    "`": "Backtick",
    "[": "LBracket",
    "]": "RBracket",
    ";": "Semicolon",
    "'": "Quote",
    "/": "Slash",
    "\\": "Backslash",
}


# =============================================================================
# ЧТЕНИЕ КОММЕНТАРИЕВ AHK
# =============================================================================

def clean_comment_text(text: str) -> str:
    """Убирает пробелы и необязательные внешние кавычки."""

    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ('"', "'"):
        return text[1:-1].strip()
    return text


def split_combo(combo: str) -> list[str]:
    """Разбивает `Caps + Shift + .` на отдельные названия клавиш."""

    return [part.strip() for part in combo.split("+") if part.strip()]


def combo_key(combo: str) -> tuple[str, str]:
    """md 
    Возвращает (внутреннее имя, видимую подпись) последней клавиши.

    Например, для `Caps + Shift + ,` результатом будет
    `("Comma", ",")`. Внутреннее имя используется для поиска в LAYOUT,
    а видимая подпись рисуется в серой части клавиши.
    """

    parts = split_combo(combo)
    if not parts:
        raise ValueError(f"Пустая комбинация: {combo!r}")

    visible_label = parts[-1]
    internal_name = SYMBOLIC_KEYS.get(visible_label, visible_label)
    internal_name = ALIASES.get(internal_name, internal_name)

    if len(internal_name) == 1 and internal_name.isalpha():
        internal_name = internal_name.upper()

    return internal_name, visible_label


def strip_marker_prefix(description: str, marker: str) -> str:
    """Преобразует строку убирая префикс 
    пример: `*DT: Вставить дату` в `Вставить дату`."""

    for prefix in (f"*{marker}:", f"{marker}:"):
        if description.startswith(prefix):
            return description[len(prefix):].strip()
    return description


def parse_source(path: Path) -> tuple[list[Entry], dict[str, Any]]:
    """Извлекает таблицы комбинаций из AHK-файла.

    Раздел распознаётся только тогда, когда после комментария без ``|`` идёт
    строка таблицы. Благодаря этому большинство обычных поясняющих комментариев
    в коде не попадают в Markdown и HTML как заголовки разделов.
    """

    source_lines = path.read_text(encoding="utf-8-sig").splitlines()
    comments: list[tuple[int, str]] = []

    for line_number, raw_line in enumerate(source_lines, 1):
        stripped = raw_line.strip()
        if stripped.startswith(";"):
            comments.append((line_number, stripped[1:].strip()))

    entries: list[Entry] = []
    config: dict[str, Any] = {}
    current_group = "Прочее"

    for index, (line_number, text) in enumerate(comments):
        if not text:
            continue

        if text.casefold().startswith("cheatsheet-title:"):
            config["title"] = text.split(":", 1)[1].strip()
            continue

        if "|" not in text:
            # Заглядываем к следующему непустому комментарию. Если он является
            # строкой таблицы, текущий комментарий считаем названием раздела.
            next_text = next(
                (candidate for _, candidate in comments[index + 1:] if candidate),
                "",
            )
            if "|" in next_text:
                current_group = text.lstrip("# ").strip()
            continue

        columns = [clean_comment_text(part) for part in text.split("|", 2)]
        if len(columns) < 2 or not columns[0]:
            raise ValueError(
                f"Некорректная строка шпаргалки {line_number}: {text}"
            )

        combo = columns[0]
        short_label = columns[1]
        description = columns[2] if len(columns) == 3 else short_label
        combo_parts = split_combo(combo)
        key, visible_key_label = combo_key(combo)

        # Двухколоночные и не-Caps комбинации показываются только в таблицах.
        # Например: ; Ctrl + Alt + Q | Завершить работу скрипта
        belongs_to_keyboard = "Caps" in combo_parts and len(columns) == 3
        if not belongs_to_keyboard:
            entries.append(Entry(
                key=key,
                label="",
                group=current_group,
                combo=combo,
                action=description,
                keyboard=False,
            ))
            continue

        is_shift_layer = "Shift" in combo_parts
        has_note = short_label.startswith("*")
        marker = short_label.removeprefix("*").strip()
        clean_description = strip_marker_prefix(description, marker)

        # Два комментария — Caps и Caps+Shift — объединяются в одну Entry,
        # потому что визуально относятся к одной физической клавише.
        entry = next(
            (item for item in entries if item.keyboard and item.key == key),
            None,
        )
        if entry is None:
            entry = Entry(
                key=key,
                label=visible_key_label,
                group=current_group,
            )
            entries.append(entry)

        if is_shift_layer:
            entry.caps_shift = marker
            entry.caps_shift_label = marker
            entry.caps_shift_note = has_note
            entry.shift_description = clean_description
        else:
            entry.caps = marker
            entry.caps_label = marker
            entry.caps_note = has_note
            entry.description = clean_description

    if not entries:
        raise ValueError(
            "Не найдены строки шпаргалки вида: "
            "; Caps + D | *DT | *DT: Вставить дату"
        )

    return entries, config


# =============================================================================
# ОБЩИЙ СПИСОК КОМБИНАЦИЙ
# =============================================================================

def combinations(entries: Iterable[Entry]) -> list[tuple[str, str, str]]:
    """Создаёт плоский список для таблиц Markdown и HTML."""

    rows: list[tuple[str, str, str]] = []

    for entry in entries:
        shown_key = entry.label or entry.key

        if entry.combo:
            action = entry.action or entry.description or entry.caps
            rows.append((entry.combo, action, entry.group))
            continue

        if entry.caps:
            action = entry.description or f"Вставить: {entry.caps}"
            rows.append((f"Caps + {shown_key}", action, entry.group))

        if entry.caps_shift:
            action = entry.shift_description or f"Вставить: {entry.caps_shift}"
            rows.append((f"Caps + Shift + {shown_key}", action, entry.group))

    return rows


# =============================================================================
# SVG: НЕБОЛЬШИЕ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================================================================

def escape_svg(text: str) -> str:
    """Экранирует текст перед вставкой в SVG/XML."""

    return html.escape(text, quote=True)


def shorten(text: str, limit: int) -> str:
    """Укорачивает слишком длинное пояснение, добавляя многоточие."""

    return text if len(text) <= limit else text[: limit - 1] + "…"


def calculate_note_text_limit(
    note_width: float,
    settings: RenderSettings = RENDER,
) -> int:
    """md
    Оценивает число символов, помещающихся справа в карточке пояснения.

    SVG не предоставляет ширину текста во время построения строки, поэтому
    применяется средняя ширина символа. Расчёт учитывает реальные размеры
    карточки, внутренние отступы, область метки и промежуток перед описанием.
    """

    text_width = (
        note_width
        - settings.note_padding_x * 2
        - settings.note_marker_width
        - settings.note_content_gap
    )
    estimated_characters = int(text_width / settings.note_average_char_width)
    return max(settings.note_min_text_chars, estimated_characters)


def item_width(units: float, settings: RenderSettings = RENDER) -> float:
    """Переводит ширину из u в пиксели.

    Формула учитывает внутренние промежутки широкой клавиши. При ширине 1u
    результат равен ровно ``settings.unit`` — стандартная клавиша квадратная.
    """

    return settings.unit * units + settings.key_gap * max(0.0, units - 1.0)


def layout_width(
    layout: Sequence[Sequence[tuple[str, str, float]]],
    settings: RenderSettings = RENDER,
) -> int:
    """Находит ширину самой длинной строки клавиатуры."""

    row_widths = []
    for row in layout:
        width = sum(item_width(units, settings) + settings.key_gap for _, _, units in row)
        row_widths.append(width - settings.key_gap)

    return int(max(row_widths) + settings.margin_x * 2)


def keyboard_height(settings: RenderSettings = RENDER) -> int:
    """Возвращает высоту всех рядов вместе с вертикальными промежутками."""

    rows_height = len(LAYOUT) * settings.key_height
    regular_gaps = (len(LAYOUT) - 1) * settings.row_gap
    return rows_height + regular_gaps + settings.function_row_extra_gap


def svg_style(theme: Theme = THEME) -> str:
    """CSS, встроенный в SVG. Размеры шрифтов удобнее менять здесь."""

    return f"""
<style>
    text {{ font-family: "Segoe UI", Arial, sans-serif; }}
    .base {{ fill: {theme.key_bg}; stroke: {theme.key_border}; stroke-width: 1.2; }}
    .key-label {{ fill: {theme.key_text}; font-size: 12px; font-weight: 600; }}
    .value {{ fill: {theme.accent}; font-size: 14px; font-weight: 800; }}
    .title {{ fill: {theme.main_text}; font-size: 27px; font-weight: 700; }}
    .subtitle {{ fill: {theme.key_text}; font-size: 13px; }}
    .note-title {{ fill: {theme.main_text}; font-size: 13px; font-weight: 700; }}
    .note-text {{ fill: {theme.muted_text}; font-size: 12px; }}
</style>""".strip()


def render_text(
    x: float,
    y: float,
    text: str,
    css_class: str,
    *,
    anchor: str | None = None,
    extra: str = "",
) -> str:
    """Формирует один SVG-элемент ``text``."""

    anchor_attr = f' text-anchor="{anchor}"' if anchor else ""
    extra_attr = f" {extra.strip()}" if extra.strip() else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" class="{css_class}"'
        f'{anchor_attr}{extra_attr}>{escape_svg(text)}</text>'
    )


def duplicate_key_id(key_id: str) -> str:
    """Связывает нарисованные продолжения высоких клавиш с одной Entry."""

    if key_id == "NumpadAdd2":
        return "NumpadAdd"
    if key_id == "NumpadEnter2":
        return "NumpadEnter"
    return key_id


# =============================================================================
# SVG: ПОДГОТОВКА СЛОЁВ И ПОЯСНЕНИЙ
# =============================================================================

def prepare_map_data(
    entries: Iterable[Entry],
) -> tuple[dict[str, Entry], dict[tuple[str, str], str], list[tuple[Entry, str, str]]]:
    """Готовит три структуры для отрисовки.

    Возвращает:
    1. активные назначения по внутреннему имени клавиши;
    2. подпись каждого слоя (Caps или Caps+Shift);
    3. список пояснений для меток со звёздочкой.
    """

    active: dict[str, Entry] = {}
    labels: dict[tuple[str, str], str] = {}
    notes: list[tuple[Entry, str, str]] = []

    for entry in entries:
        if not entry.keyboard:
            continue

        active[entry.key] = entry

        layers = (
            ("caps", entry.caps, entry.caps_label, entry.caps_note, entry.description),
            (
                "shift",
                entry.caps_shift,
                entry.caps_shift_label,
                entry.caps_shift_note,
                entry.shift_description,
            ),
        )

        for layer, value, visible_label, wants_note, description in layers:
            if not value:
                continue

            labels[(entry.key, layer)] = visible_label or value
            if wants_note:
                notes.append((entry, layer, description or value))

    return active, labels, notes


# =============================================================================
# SVG: ОТРИСОВКА ОДНОЙ КЛАВИШИ
# =============================================================================

def render_inactive_key(
    x: float,
    y: float,
    width: float,
    label: str,
    settings: RenderSettings = RENDER,
) -> list[str]:
    """Рисует обычную серую клавишу без назначенного хоткея."""

    label_x = x + 8
    baseline_y = y + settings.key_height * 0.82
    return [render_text(label_x, baseline_y, label, "key-label", anchor="start")]

def render_active_key(
    x: float,
    y: float,
    width: float,
    default_label: str,
    entry: Entry,
    layer_labels: dict[tuple[str, str], str],
    settings: RenderSettings = RENDER,
    theme: Theme = THEME,
) -> list[str]:
    """Рисует содержимое активной клавиши.

    Вся клавиша уже имеет серый фон. Здесь она мысленно делится на две части:

    * слева остаётся исходная физическая клавиша;
    * справа показываются назначения слоя Caps;
    * если есть Caps+Shift, правая часть делится пополам по горизонтали;
    * цветной фон не используется — акцентным цветом окрашен только текст.
    """

    result: list[str] = []

    # На очень широкой клавише левая зона всё равно остаётся компактной.
    left_width = min(float(settings.active_key_label_width), width * 0.43)
    right_width = width - left_width
    right_center_x = x + left_width + right_width / 2

    # Для карты всегда берём короткую визуальную подпись из LAYOUT.
    # Например, комментарий содержит Numpad7, но на клавише рисуется «7».
    # Полное имя Numpad7 по-прежнему сохраняется в Markdown и HTML.
    physical_label = default_label
    physical_label_x = x + 8
    physical_baseline_y = y + settings.key_height * 0.82
    result.append(render_text(
        physical_label_x,
        physical_baseline_y,
        physical_label,
        "key-label",
        anchor="start",
    ))

    # Разделительную линию не рисуем: это сохраняет чистый вид клавиши.

    if entry.caps_shift:
        # Caps + Shift всегда находится на фиксированной верхней позиции.
        shift_label = layer_labels[(entry.key, "shift")]
        shift_baseline_y = y + settings.key_height * 0.34
        result.append(render_text(
            right_center_x,
            shift_baseline_y,
            shift_label,
            "value",
            anchor="middle",
        ))

    # Caps всегда находится на фиксированной нижней позиции — независимо
    # от наличия Shift-слоя. Поэтому подписи не «прыгают» между клавишами.
    caps_baseline_y = y + settings.key_height * 0.82

    if entry.caps:
        caps_label = layer_labels[(entry.key, "caps")]
        result.append(render_text(
            right_center_x,
            caps_baseline_y,
            caps_label,
            "value",
            anchor="middle",
        ))

    return result


def render_key(
    x: float,
    y: float,
    width: float,
    key_id: str,
    default_label: str,
    entry: Entry | None,
    layer_labels: dict[tuple[str, str], str],
    settings: RenderSettings = RENDER,
    theme: Theme = THEME,
) -> list[str]:
    """Рисует фон клавиши, а затем её активное или обычное содержимое.

    Высокие клавиши (двухрядные, например NumpadAdd и NumpadEnter) украшены
    прямоугольником на всю высоту, а содержимое выравнивается по центру.
    """

    row_span = TALL_KEYS.get(key_id, 1)
    height = (
        settings.key_height * row_span
        + settings.row_gap * (row_span - 1)
    )

    # Смещение, чтобы блок содержимого высотой в одну клавишу оказался
    # по центру прямоугольника высокой клавиши.
    content_y = y + (height - settings.key_height) / 2

    result = [
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" '
        f'height="{height:.1f}" rx="{settings.corner_radius}" class="base"/>'
    ]

    if entry is None:
        result.extend(render_inactive_key(x, content_y, width, default_label, settings))
    else:
        result.extend(render_active_key(
            x,
            content_y,
            width,
            default_label,
            entry,
            layer_labels,
            settings,
            theme,
        ))

    return result


# =============================================================================
# SVG: ОТРИСОВКА КЛАВИАТУРЫ И ПРИМЕЧАНИЙ
# =============================================================================

def render_keyboard(
    active: dict[str, Entry],
    layer_labels: dict[tuple[str, str], str],
    settings: RenderSettings = RENDER,
    theme: Theme = THEME,
) -> list[str]:
    """Проходит по LAYOUT слева направо сверху вниз."""

    result: list[str] = []
    y = float(settings.keyboard_top)

    for row_index, row in enumerate(LAYOUT):
        x = float(settings.margin_x)

        for key_id, default_label, units in row:
            width = item_width(units, settings)

            # GAP только сдвигает координату x. SVG-элемент для него не создаётся.
            if key_id == "GAP":
                x += width + settings.key_gap
                continue

            lookup_id = key_id
            entry = active.get(lookup_id)
            result.extend(render_key(
                x,
                y,
                width,
                key_id,
                default_label,
                entry,
                layer_labels,
                settings,
                theme,
            ))
            x += width + settings.key_gap

        # После F-ряда добавляется увеличенный вертикальный промежуток.
        y += settings.key_height + settings.row_gap
        if row_index == 0:
            y += settings.function_row_extra_gap

    return result


def note_detail(entry: Entry, layer: str, description: str) -> str:
    """Формирует текст пояснения без бессмысленного повторения значения."""

    value = entry.caps_shift if layer == "shift" else entry.caps
    if description == value or value in description:
        return description
    return f"{description}"


def render_notes(
    notes: Sequence[tuple[Entry, str, str]],
    layer_labels: dict[tuple[str, str], str],
    notes_top: float,
    canvas_width: int,
    settings: RenderSettings = RENDER,
    theme: Theme = THEME,
) -> list[str]:
    """Рисует сетку пояснений для меток, начинавшихся со звёздочки.

    Каждая карточка разделена на две области:

    * слева находится достаточно широкая фиксированная зона для DT/DTM/DTA;
    * справа находятся комбинация и полное описание;
    * длина описания вычисляется по фактической ширине правой области,
      а не ограничивается постоянным числом символов.
    """

    if not notes:
        return []

    result = [
        render_text(
            settings.margin_x,
            notes_top - 19,
            "Пояснения",
            "note-title",
        )
    ]

    # Вычисляем реальную ширину одной карточки с учётом количества колонок.
    available_width = canvas_width - settings.margin_x * 2
    all_column_gaps = settings.key_gap * (settings.notes_columns - 1)
    note_width = (available_width - all_column_gaps) / settings.notes_columns

    # Лимит зависит от пространства, которое осталось справа от метки.
    text_limit = calculate_note_text_limit(note_width, settings)

    for index, (entry, layer, description) in enumerate(notes):
        column = index % settings.notes_columns
        row = index // settings.notes_columns

        note_x = settings.margin_x + column * (note_width + settings.key_gap)
        note_y = notes_top + row * (settings.note_height + settings.note_gap)

        key_label = entry.label or entry.key
        combo = (
            f"Caps + Shift + {key_label}"
            if layer == "shift"
            else f"Caps + {key_label}"
        )

        marker = layer_labels[(entry.key, layer)]
        detail = shorten(note_detail(entry, layer, description), text_limit)

        # Левая зона начинается после внутреннего отступа карточки.
        marker_left = note_x + settings.note_padding_x
        marker_center_x = marker_left + settings.note_marker_width / 2

        # Правая текстовая область начинается после метки и промежутка.
        content_x = (
            marker_left
            + settings.note_marker_width
            + settings.note_content_gap
        )

        result.append(
            f'<rect x="{note_x:.1f}" y="{note_y:.1f}" '
            f'width="{note_width:.1f}" height="{settings.note_height}" '
            f'rx="8" fill="{theme.note_bg}" stroke="{theme.note_border}"/>'
        )

        result.append(render_text(
            marker_center_x,
            note_y + settings.note_height / 2 + 6,
            marker,
            "value",
            anchor="middle",
            extra='style="font-size:17px;font-weight:800"',
        ))
        result.append(render_text(
            content_x,
            note_y + 19,
            combo,
            "note-title",
            anchor="start",
        ))
        result.append(render_text(
            content_x,
            note_y + 39,
            detail,
            "note-text",
            anchor="start",
        ))

    return result

def calculate_canvas_height(
    note_count: int,
    settings: RenderSettings = RENDER,
) -> tuple[int, float]:
    """Возвращает высоту SVG и верхнюю координату блока пояснений."""

    keyboard_bottom = settings.keyboard_top + keyboard_height(settings)
    notes_top = keyboard_bottom + settings.notes_gap_top

    note_rows = (
        (note_count + settings.notes_columns - 1) // settings.notes_columns
        if note_count
        else 0
    )
    notes_height = note_rows * (settings.note_height + settings.note_gap)

    # При отсутствии пояснений не оставляем под клавиатурой большой пустой блок.
    if note_count:
        canvas_height = notes_top + notes_height + settings.bottom_padding
    else:
        canvas_height = keyboard_bottom + settings.bottom_padding

    return int(canvas_height), float(notes_top)


def generate_svg(
    entries: list[Entry],
    settings: RenderSettings = RENDER,
    theme: Theme = THEME,
) -> str:
    """Собирает итоговый SVG из заголовка, клавиатуры и пояснений."""

    active, layer_labels, notes = prepare_map_data(entries)
    canvas_width = layout_width(LAYOUT, settings)
    canvas_height, notes_top = calculate_canvas_height(len(notes), settings)

    # На карте всегда рисуется фиксированный заголовок, независимо от того,
    # какой заголовок документа указан в AHK-файле.
    map_title = "Карта клавиатуры"

    result = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_width}" '
        f'height="{canvas_height}" viewBox="0 0 {canvas_width} {canvas_height}">',
        svg_style(theme),
        f'<rect width="100%" height="100%" fill="{theme.page_bg}" rx="18"/>',
        render_text(settings.margin_x, settings.title_y, map_title, "title"),
        render_text(
            settings.margin_x,
            settings.subtitle_y,
            "Нижний правый символ — Caps · верхний правый — Caps + Shift",
            "subtitle",
        ),
    ]

    result.extend(render_keyboard(active, layer_labels, settings, theme))
    result.extend(render_notes(
        notes,
        layer_labels,
        notes_top,
        canvas_width,
        settings,
        theme,
    ))
    result.append("</svg>")

    return "\n".join(result)


# =============================================================================
# MARKDOWN И HTML
# =============================================================================

def group_combinations(
    entries: Iterable[Entry],
) -> list[tuple[str, list[tuple[str, str]]]]:
    """Группирует комбинации по разделам, сохраняя порядок следования."""

    groups: dict[str, list[tuple[str, str]]] = {}
    for combo, action, group in combinations(entries):
        groups.setdefault(group, []).append((combo, action))
    return list(groups.items())


def generate_markdown(entries: list[Entry], title: str, image_name: str) -> str:
    """Создаёт Markdown с картой и полным списком комбинаций по разделам."""

    lines = [
        f"# {title}",
        "",
        f"![{title}]({image_name})",
        "",
        "## Полный список комбинаций",
        "",
    ]

    for group, rows in group_combinations(entries):
        lines.extend([f"### {group}", ""])
        lines.extend(["| Комбинация | Действие |", "|---|---|"])
        for combo, action in rows:
            escape_cell = lambda value: value.replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| `{escape_cell(combo)}` | {escape_cell(action)} |"
            )
        lines.append("")

    lines.extend([
        f"_Сгенерировано: {datetime.now():%d.%m.%Y %H:%M}_",
        "",
    ])
    return "\n".join(lines)


def generate_html(entries: list[Entry], title: str, svg: str, light: bool = False) -> str:
    """Создаёт автономный HTML; SVG встраивается непосредственно в документ.

    Комбинации разбиты по разделам. ``light=True`` включает светлую тему
    для печати, соответствующую светлой версии SVG-карты.
    """

    sections: list[str] = []
    for group, rows in group_combinations(entries):
        rows_html = "".join(
            "<tr>"
            f"<td><kbd>{html.escape(combo)}</kbd></td>"
            f"<td>{html.escape(action)}</td>"
            "</tr>\n"
            for combo, action in rows
        )
        sections.append(
            f"    <section>\n"
            f"        <h3>{html.escape(group)}</h3>\n"
            f"        <table>\n"
            f"            <thead><tr><th>Комбинация</th><th>Действие</th></tr></thead>\n"
            f"            <tbody>{rows_html}</tbody>\n"
            f"        </table>\n"
            f"    </section>"
        )

    if light:
        page_bg, page_fg, table_bg, border, th, kbd_bg, kbd_border, kbd_fg, heading, small = (
            "#ffffff", "#1f1f28", "#f4f4f7", "#d7d7e0",
            "#9a3412", "#e6e6ee", "#c9c9d6", "#1f1f28", "#c4540f", "#6a6a76",
        )
    else:
        page_bg, page_fg, table_bg, border, th, kbd_bg, kbd_border, kbd_fg, heading, small = (
            "#11111b", "#cdd6f4", "#1e1e2e", "#45475a",
            "#f9e2af", "#313244", "#585b70", "#ffffff", "#89b4fa", "#a6adc8",
        )

    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
    body {{ margin: 0; background: {page_bg}; color: {page_fg}; font-family: "Segoe UI", Arial, sans-serif; }}
    main {{ max-width: 1540px; margin: auto; padding: 28px; }}
    h1 {{ color: {heading}; }}
    h3 {{ color: {heading}; margin: 26px 0 10px; }}
    .map {{ overflow: auto; border: 1px solid {border}; border-radius: 14px; background: {page_bg}; }}
    .map svg {{ display: block; max-width: 100%; height: auto; }}
    table {{ width: 100%; border-collapse: collapse; background: {table_bg}; border-radius: 12px; overflow: hidden; }}
    th, td {{ padding: 12px 15px; border-bottom: 1px solid {border}; text-align: left; }}
    th {{ color: {th}; }}
    kbd {{ background: {kbd_bg}; border: 1px solid {kbd_border}; border-radius: 5px; padding: 3px 7px; color: {kbd_fg}; }}
    small {{ color: {small}; }}
</style>
</head>
<body>
<main>
    <h1>{html.escape(title)}</h1>
    <div class="map">{svg}</div>
    <h2>Полный список комбинаций</h2>
{chr(10).join(sections)}
    <p><small>Сгенерировано: {datetime.now():%d.%m.%Y %H:%M}</small></p>
</main>
</body>
</html>'''


# =============================================================================
# СОХРАНЕНИЕ ФАЙЛОВ И CLI
# =============================================================================

def write_png(svg: str, path: Path) -> None:
    """Преобразует SVG в PNG. CairoSVG нужен только для этого режима."""

    try:
        import cairosvg  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Для PNG установите зависимость: pip install -q cairosvg"
        ) from exc

    cairosvg.svg2png(
        bytestring=svg.encode("utf-8"),
        write_to=str(path),
        output_width=2280,
    )


def build_argument_parser() -> argparse.ArgumentParser:
    """Описывает аргументы командной строки отдельно от основной логики."""

    parser = argparse.ArgumentParser(
        description="Генератор карты хоткеев из комментариев AHK"
    )
    parser.add_argument("source", type=Path, help="Исходный .ahk-файл")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("cheatsheet"),
        help="Каталог результата (по умолчанию: cheatsheet)",
    )
    parser.add_argument(
        "--mode",
        choices=("all", "markdown", "html", "image"),
        default="all",
        help="Какие документы создавать",
    )
    parser.add_argument(
        "--image-format",
        choices=("svg", "png", "both"),
        default="svg",
        help="Формат карты клавиатуры",
    )
    parser.add_argument(
        "--title",
        default="Карта горячих клавиш",
        help="Заголовок, если он не задан в AHK-файле",
    )
    parser.add_argument(
        "--theme",
        choices=("dark", "light", "both"),
        default="dark",
        help="Тема SVG-карты и HTML: тёмная, светлая (для печати) или обе",
    )
    return parser


def main() -> int:
    args = build_argument_parser().parse_args()

    try:
        entries, config = parse_source(args.source)
        title = str(config.get("title", args.title))
        args.output_dir.mkdir(parents=True, exist_ok=True)

        # Темы, которые нужно отрисовать. Тёмная сохраняется под исходными
        # именами, светлая получает суффикс ``_light``.
        theme_map = {"dark": (THEME, ""), "light": (LIGHT_THEME, "_light")}
        if args.theme == "both":
            render_themes = list(theme_map.values())
        else:
            render_themes = [theme_map[args.theme]]

        # Документам нужен файл SVG, даже если пользователь отдельно запросил PNG.
        documents_requested = args.mode in ("all", "markdown", "html")

        for theme, suffix in render_themes:
            svg = generate_svg(entries, theme=theme)
            svg_path = args.output_dir / f"keyboard_map{suffix}.svg"
            png_path = args.output_dir / f"keyboard_map{suffix}.png"

            if args.image_format in ("svg", "both") or documents_requested:
                svg_path.write_text(svg, encoding="utf-8")

            if args.image_format in ("png", "both"):
                write_png(svg, png_path)

            if args.mode in ("all", "html"):
                document = generate_html(entries, title, svg, light=(theme is LIGHT_THEME))
                doc_path = args.output_dir / f"cheatsheet{suffix}.html"
                doc_path.write_text(document, encoding="utf-8")

        # Markdown ссылается на PNG только в режиме чистого PNG.
        # В markdown подставляется карта той темы, которая реально создана.
        if args.theme == "light":
            image_name = "keyboard_map_light.png" if args.image_format == "png" else "keyboard_map_light.svg"
        else:
            image_name = "keyboard_map.png" if args.image_format == "png" else "keyboard_map.svg"

        if args.mode in ("all", "markdown"):
            markdown = generate_markdown(entries, title, image_name)
            (args.output_dir / "cheatsheet.md").write_text(markdown, encoding="utf-8")

        print(f"Готово: {args.output_dir.resolve()}")
        return 0

    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
