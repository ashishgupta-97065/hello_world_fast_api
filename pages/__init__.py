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
# Batch 3
from pages.finance import render_finance
from pages.habits import render_habits
from pages.flashcards import render_flashcards
from pages.budget import render_budget
from pages.stopwatch import render_stopwatch
from pages.json_formatter import render_json_formatter
from pages.diff import render_diff
from pages.recipe import render_recipe
from pages.pomodoro_pro import render_pomodoro_pro
from pages.kanban import render_kanban

__all__ = [
    "render_menu",
    "render_todo", "render_pomodoro", "render_markdown", "render_palette",
    "render_bmi", "render_password", "render_word_counter",
    "render_unit_converter", "render_quote", "render_dice",
    "render_finance", "render_habits", "render_flashcards", "render_budget",
    "render_stopwatch", "render_json_formatter", "render_diff",
    "render_recipe", "render_pomodoro_pro", "render_kanban",
]
