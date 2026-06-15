from typing import Protocol

import os 
import asyncio
import pathlib

import pynvim
from pydantic_ai.mcp import MCPServerStdio 
from yaar.models import Agent, Model, Session, Logging
from yaar.tools import all_tools
from yaar.agent import start_agent_with_session

codebase_memory_prompt = '''
<!-- codebase-memory-mcp:start -->
# Codebase Knowledge Graph (codebase-memory-mcp)

This project uses codebase-memory-mcp to maintain a knowledge graph of the codebase.
ALWAYS prefer MCP graph tools over grep/glob/file-search for code discovery.

## Priority Order
1. `search_graph` — find functions, classes, routes, variables by pattern
2. `trace_path` — trace who calls a function or what it calls
3. `get_code_snippet` — read specific function/class source code
4. `query_graph` — run Cypher queries for complex patterns
5. `get_architecture` — high-level project summary

## When to fall back to grep/glob
- Searching for string literals, error messages, config values
- Searching non-code files (Dockerfiles, shell scripts, configs)
- When MCP tools return insufficient results

## Examples
- Find a handler: `search_graph(name_pattern=".*OrderHandler.*")`
- Who calls it: `trace_path(function_name="OrderHandler", direction="inbound")`
- Read source: `get_code_snippet(qualified_name="pkg/orders.OrderHandler")`
<!-- codebase-memory-mcp:end -->
'''




@pynvim.plugin
class AiChat(object):

    def __init__(self, nvim: pynvim.Nvim):
        self.nvim = nvim
        api_key = os.getenv('API_KEY')
        assert api_key is not None, 'ChatGPT API_KEY not found from env vars' 
        self._api_key = api_key
        self._current_session: Session | None = None
        self._current_session_future: asyncio.futures.Future | None = None

    @property
    def ai_working_currently(self) -> bool:
        return self._current_session_future != None and not self._current_session_future.done()

    @pynvim.command('AItest')
    def test(self):
        self.nvim.api.out_write("Hello from !\n")

    @pynvim.command('AISessionls')
    def show_sessions(self):
        session_text = self._current_session.session_id if self._current_session is not None else 'No session'
        session_buffer = self.nvim.api.create_buf(False, True) ## Not listed scratch buffer
        session_buffer[0] = session_text
        config = {'relative': 'win', 'row': 10, 'col':10, 'width': 25, 'height': 2, 'border': ["╔", "═" ,"╗", "║", "╝", "═", "╚", "║"]}
        self.nvim.api.open_win(session_buffer.number, True, config)

    @pynvim.command('AIKill')
    def kill_current_session(self):
        if self.ai_working_currently:
            self._current_session_future.cancel()

    @pynvim.command('Query', nargs='?')
    def query(self, args):
        current_buffer = self.nvim.current.buffer
        if current_buffer.name != '':
            self.nvim.api.out_write('Current buffer is not new Buffer!\n')
            return

        if self.ai_working_currently:
            self.nvim.api.out_write('AI working at the moment!\n')
            return

        previous_session = args[0] if len(args) > 0 else None

        system_prompt = f"""
{codebase_memory_prompt}

# Project
    - root {os.getcwd()}
    - Always begin by rephrasing the user's goal in a friendly, clear, and concise manner, before calling any tools.
    - Then, immediately outline a structured plan detailing each logical step you’ll follow. - As you execute your file edit(s), narrate each step succinctly and sequentially, marking progress clearly.
    - Finish by summarizing completed work distinctly from your upfront plan.
        """

        monitor_buffer = self.nvim.api.create_buf(False, True) ## Not listed scratch buffer
        self.nvim.api.open_win(monitor_buffer.number, False, {'split': 'below'})#, 'row': 3, 'col': 3, 'width': 12, 'height': 3})

        code_memory = MCPServerStdio(
            timeout=10,
            command="/Users/mlackman/.local/bin/codebase-memory-mcp",
            args=[],
            tool_prefix="",
            allow_sampling=False,
        )
     
        main_agent = Agent(
            name='Generic-ai',
            model=Model.GPT_55,
            system_prompt=system_prompt,
            description='generic llm ai',
            toolsets=[code_memory, *all_tools()],
            api_key=self._api_key
        )

        self._current_session = Session.create_main_session(
            session_name='vim-agent',
            path = pathlib.Path('./.session'),
            logging_factory=lambda session: VimLogging(session, BufferWriter(current_buffer), BufferWriter(monitor_buffer), self.nvim)
        )
        prompt = '\n'.join(self.nvim.current.buffer[:])
        current_buffer.name = self._current_session.session_id

        self._current_session_future = asyncio.ensure_future(
            start_agent_with_session(
                prompt=prompt,
                agent=main_agent,
                sub_agents=[],
                session=self._current_session,
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


class VimLogging(Logging):
    def __init__(self, session: Session, output_writer: BufferWriter, debug_writer: BufferWriter, nvim: pynvim.Nvim):
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
