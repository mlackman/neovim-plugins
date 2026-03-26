from typing import override
from unittest import TestCase

from ..aichat import BufferWriter


class BufferWriterTest(TestCase):
    # TODO: No first line

    @override
    def setUp(self):
        self.writer = BufferWriter(['first line'])


    def test_complex(self):
        self.writer.write("1 line")
        self.writer.write(" word\n\n2 line")
        self.writer.write(" word\n3 line")
        assert ['first line', '1 line word', '', '2 line word', '3 line'] == self.writer.buffer 

    def test_start_with_eol(self):
        self.writer.write('\na line')
        assert ['first line', '', 'a line'] == self.writer.buffer 

    def test_add_line_wihtout_eol(self):
        self.writer.write('a line')

        assert ['first line', 'a line'] == self.writer.buffer 

    def test_add_line_with_eol(self):
        self.writer.write('a line\n')

        assert ['first line', 'a line'] == self.writer.buffer


    def test_add_lines_with_eol(self):
        self.writer.write('a line\n')
        self.writer.write('a other line\n')

        assert ['first line', 'a line', 'a other line'] == self.writer.buffer


    def test_add_two_lines_last_line_without_eol(self):
        self.writer.write('a line\nother line')

        assert ['first line', 'a line', 'other line'] == self.writer.buffer 

    def test_add_three_lines_last_line_without_eol(self):
        self.writer.write('a line\nother line\nthird line')

        assert ['first line', 'a line', 'other line', 'third line'] == self.writer.buffer 


    def test_continue_writing_to_same_line(self):
        self.writer.write('a line')
        self.writer.write(' next word')

        assert ['first line', 'a line next word'] == self.writer.buffer 

    def test_continue_writing_to_same_line_long(self):
        self.writer.write('a line')
        self.writer.write(' next word\n')
        self.writer.write('new line')

        assert ['first line', 'a line next word', 'new line'] == self.writer.buffer

    def test_continue_writing_3(self):
        self.writer.write('a line')
        self.writer.write(' next word')
        self.writer.write(' yet another word')
        self.writer.write('\n')
        self.writer.write('new line')

        assert ['first line', 'a line next word yet another word', 'new line'] == self.writer.buffer
