"""Public surface of the pages package."""
from pages._shell import render_menu
from pages.todo import render_todo
from pages.pomodoro import render_pomodoro
from pages.markdown import render_markdown
from pages.palette import render_palette
from pages.bmi import render_bmi
from pages.password import render_password
from pages.word_counter import render_word_counter
from pages.unit_converter import render_unit_converter
from pages.quote import render_quote
from pages.dice import render_dice

__all__ = [
    "render_menu",
    "render_todo", "render_pomodoro", "render_markdown", "render_palette",
    "render_bmi", "render_password", "render_word_counter",
    "render_unit_converter", "render_quote", "render_dice",
]
