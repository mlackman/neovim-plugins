from typing import Protocol

import os 
import datetime 
import asyncio
import traceback
import pathlib

import pynvim
from yaar import agent
from pydantic_ai import Agent
from pydantic_ai import Agent
from pydantic_ai import (
    FunctionToolCallEvent,
    FinalResultEvent,
    FunctionToolResultEvent,
    PartDeltaEvent,
    PartStartEvent,
    TextPartDelta,
    ThinkingPartDelta,
    ToolCallPartDelta,
)

@pynvim.plugin
class AiChat(object):

    def __init__(self, nvim: pynvim.Nvim):
        self.nvim = nvim
        api_key = os.getenv('API_KEY')
        assert api_key is not None, 'ChatGPT API_KEY not found from env vars' 
        self._api_key = api_key

    @pynvim.command('Query', nargs='?')
    def query(self, args):
        self._last_line_no = len(self.nvim.current.buffer) 

        previous_session = args[0] if len(args) > 0 else None

        system_prompt = """
    - Always begin by rephrasing the user's goal in a friendly, clear, and concise manner, before calling any tools.
    - Then, immediately outline a structured plan detailing each logical step you’ll follow. - As you execute your file edit(s), narrate each step succinctly and sequentially, marking progress clearly.
    - Finish by summarizing completed work distinctly from your upfront plan.
        """
        current_buffer = self.nvim.current.buffer
        monitor_buffer = self.nvim.api.create_buf(False, True) ## Not listed scratch buffer
        self.nvim.api.open_win(monitor_buffer.number, False, {'split': 'below'})#, 'row': 3, 'col': 3, 'width': 12, 'height': 3})

        session = agent.Session.create_main_session(
            agent_name='vim-agent',
            path = pathlib.Path('./.session'),
            logging_factory=lambda session: VimLogging(session, BufferWriter(current_buffer), BufferWriter(monitor_buffer), self.nvim)
        )
        prompt = '\n'.join(self.nvim.current.buffer[:])

        asyncio.ensure_future(
            agent.start_agent_with_session(
                prompt=prompt,
                agent_name='generic-ai',
                agent_system_prompt=system_prompt,
                mcps=agent.create_mcps(),
                api_key=self._api_key,
                session=session,
                previous_session=previous_session
            )
        )

class Buffer(Protocol):
    def __setitem__(self, *args, **kwargs) -> None:  
        ...

    def append(self, *args, **kwargs) -> None:
        ...

class BufferWriter:

    def __init__(self, buffer: Buffer) -> None:
        self.buffer = buffer
        self._current_line: str | None = None

    def write(self, text: str): 
        if text == '':
            return

        lines = text.splitlines()
        lines_with_endings = text.splitlines(keepends=True)
        last_line_idx = len(lines) - 1
        last_line_has_line_ending = not self._line_ends_without_eol(lines_with_endings[-1])

        for i, line in enumerate(lines):
            is_last_line = i == last_line_idx  # last line might or might not contain end of line

            if self._current_line is None and is_last_line and not last_line_has_line_ending:
                self._current_line = line
                self.buffer.append(self._current_line)

            elif self._current_line is not None and not is_last_line:
                # Always ending with the eol, because not last line and lines were created using splitlines
                self._current_line += line
                self.buffer[-1] = self._current_line
                self._current_line = None

            elif self._current_line is not None and is_last_line and not last_line_has_line_ending:
                self._current_line += line
                self.buffer[-1] = self._current_line

            elif self._current_line is not None and is_last_line and last_line_has_line_ending:
                self.buffer[-1] = self._current_line + line
                self._current_line = None

            else:
                self.buffer.append(line)

    def _line_ends_without_eol(self, line: str) -> bool:
        line = line + 'w\nw'
        return len(line.splitlines()) == 2


class VimLogging(agent.Logging):
    def __init__(self, session: agent.Session, output_writer: BufferWriter, debug_writer: BufferWriter, nvim: pynvim.Nvim):
        super().__init__(session)
        self._output_writer = output_writer
        self._debug_writer = debug_writer 
        self._nvim = nvim

    def output(self, s: str) -> None:
        super().output(s)
        self._nvim.async_call(lambda txt: self._output_writer.write(txt), s)

    def debug(self, s: str) -> None:
        super().output(s)
        self._nvim.async_call(lambda txt: self._debug_writer.write(txt + '\n'), s)
