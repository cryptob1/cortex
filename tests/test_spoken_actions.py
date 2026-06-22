"""Unit tests for spoken-action segmentation (say a command -> press a key)."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oflow import segment_spoken_actions, _KEY_ENTER, _KEY_TAB, _KEY_ESC, _tap


def kinds(segs):
    return [s[0] for s in segs]


def texts(segs):
    return [s[1] for s in segs if s[0] == "text"]


def keyseqs(segs):
    return [s[1] for s in segs if s[0] == "key"]


class TestNoActions:
    @pytest.mark.unit
    def test_plain_text_is_single_untouched_segment(self):
        text = "the quick brown fox jumps over the lazy dog"
        assert segment_spoken_actions(text) == [("text", text)]

    @pytest.mark.unit
    def test_empty_text(self):
        assert segment_spoken_actions("") == [("text", "")]

    @pytest.mark.unit
    def test_bare_enter_in_prose_is_not_a_command(self):
        # "press enter" is the command; a bare "enter" must stay literal text.
        text = "remember the data you enter is saved"
        assert segment_spoken_actions(text) == [("text", text)]

    @pytest.mark.unit
    def test_bare_tab_in_prose_is_not_a_command(self):
        text = "keep tabs on the budget"
        assert segment_spoken_actions(text) == [("text", text)]


class TestSingleActions:
    @pytest.mark.unit
    def test_new_line_alone(self):
        segs = segment_spoken_actions("new line")
        assert kinds(segs) == ["key"]
        assert keyseqs(segs)[0] == [_tap(_KEY_ENTER)]

    @pytest.mark.unit
    def test_press_enter_alone(self):
        segs = segment_spoken_actions("press enter")
        assert kinds(segs) == ["key"]
        assert keyseqs(segs)[0] == [_tap(_KEY_ENTER)]

    @pytest.mark.unit
    def test_new_paragraph_is_two_enter_taps(self):
        segs = segment_spoken_actions("new paragraph")
        assert keyseqs(segs)[0] == [_tap(_KEY_ENTER), _tap(_KEY_ENTER)]

    @pytest.mark.unit
    def test_press_tab(self):
        segs = segment_spoken_actions("press tab")
        assert keyseqs(segs)[0] == [_tap(_KEY_TAB)]

    @pytest.mark.unit
    def test_press_escape(self):
        segs = segment_spoken_actions("press escape")
        assert keyseqs(segs)[0] == [_tap(_KEY_ESC)]

    @pytest.mark.unit
    def test_case_insensitive(self):
        segs = segment_spoken_actions("New Line")
        assert kinds(segs) == ["key"]


class TestInterleaved:
    @pytest.mark.unit
    def test_action_between_text(self):
        segs = segment_spoken_actions("go to settings new line click save")
        assert kinds(segs) == ["text", "key", "text"]
        assert texts(segs) == ["go to settings", "click save"]
        assert keyseqs(segs)[0] == [_tap(_KEY_ENTER)]

    @pytest.mark.unit
    def test_trailing_command_trims_space(self):
        segs = segment_spoken_actions("save the file press enter")
        assert kinds(segs) == ["text", "key"]
        assert texts(segs) == ["save the file"]  # no trailing space

    @pytest.mark.unit
    def test_orphan_punctuation_after_command_is_dropped(self):
        # Cleanup LLM often appends a period: "...do it. Press enter."
        segs = segment_spoken_actions("do it press enter.")
        assert kinds(segs) == ["text", "key"]
        assert texts(segs) == ["do it"]

    @pytest.mark.unit
    def test_multiple_actions(self):
        segs = segment_spoken_actions("first line new line second line new line third")
        assert kinds(segs) == ["text", "key", "text", "key", "text"]
        assert texts(segs) == ["first line", "second line", "third"]

    @pytest.mark.unit
    def test_leading_command(self):
        segs = segment_spoken_actions("press tab username")
        assert kinds(segs) == ["key", "text"]
        assert texts(segs) == ["username"]


from oflow import should_skip_cleanup, DEFAULT_FAST_MODE_MAX_WORDS


class TestFastModeCleanupSkip:
    @pytest.mark.unit
    def test_short_text_skips(self):
        assert should_skip_cleanup("open the pull request", 8) is True

    @pytest.mark.unit
    def test_exactly_threshold_skips(self):
        assert should_skip_cleanup("one two three four five six seven eight", 8) is True

    @pytest.mark.unit
    def test_over_threshold_cleans(self):
        assert should_skip_cleanup("one two three four five six seven eight nine", 8) is False

    @pytest.mark.unit
    def test_zero_disables_fast_mode(self):
        assert should_skip_cleanup("hi", 0) is False

    @pytest.mark.unit
    def test_negative_disables_fast_mode(self):
        assert should_skip_cleanup("hi", -1) is False

    @pytest.mark.unit
    def test_empty_text_skips(self):
        assert should_skip_cleanup("", 8) is True

    @pytest.mark.unit
    def test_default_threshold_is_sane(self):
        assert DEFAULT_FAST_MODE_MAX_WORDS == 8
