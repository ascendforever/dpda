#!/usr/bin/env python3



import abc
import collections
import io
import itertools
import re
import sys
import types



# for formatting
UTF8_BOX_DRAWING_CHARACTERS = dict(
    bar='│',
    bar_down='┬',
    bar_up='┴',
    bar_left='┤',
    bar_right='├',
    corner_bottom_left='└',
    corner_bottom_right='┘',
    corner_top_left='┌',
    corner_top_right='┐',
    cross='┼',
    hr='─',
)
ASCII_BOX_DRAWING_CHARACTERS = dict(
    bar='|',
    bar_down='+',
    bar_up='+',
    bar_left='+',
    bar_right='+',
    corner_bottom_left='+',
    corner_bottom_right='+',
    corner_top_left='+',
    corner_top_right='+',
    cross='+',
    hr='-',
)



class DPDA(abc.ABC):
    """
    Deterministic Push-Down Automata
    """


    # needs overwriting
    DELTA = ...
    START_STATE = ...
    END_STATE = ...

    def __init_subclass__(cls, **kwargs):
        """Set up variables that vary betweens DPDAs"""
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, 'DELTA'):
            raise TypeError("DELTA must be defined in subclass")
        for l in ('START', 'END'):
            if not hasattr(cls, f'{l}_STATE'):
                raise TypeError(f"{l}_STATE must be defined in subclass")
        cls.R_RULES = r_rules = frozenset(itertools.chain.from_iterable(
            (t[3] for t in d.values() if t[3])
            for d in cls.DELTA.values()
        ))
        cls.R_RULE_USED_FORMAT_WIDTH = max(len('R'), max(map(len, r_rules)))
        cls.DELTA_RULE_COUNT = drc = sum(map(len, cls.DELTA.values()))
        cls.DELTA_RULE_USED_FORMAT_WIDTH = max(len('Delta'), len(str(drc)))
        cls.STATES = states = frozenset(itertools.chain(
            (cls.START_STATE,cls.END_STATE),
            cls.DELTA.keys()
        ))
        cls.STATE_FORMAT_WIDTH = max(len('State'), max(map(len, states)))


    def __init__(self):
        self.reset()
    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}() "
            f"step={self.step} "
            f"state={self.state} "
            f"input={''.join(self.input)} "
            f"stack={''.join(self.stack)} "
            f"delta_rule_used={self.delta_rule_used!r} "
            f"r_rule_used={self.r_rule_used!r}>"
        )

    def reset(self) -> None:
        self.step:int = -1
        self.state = self.__class__.START_STATE
        self.input = None
        self.stack = None
        self.delta_rule_used = None
        self.r_rule_used = None


    @property
    def stack(self) -> collections.deque[str]:
        return self._stack
    @stack.setter
    def stack(self, value):
        self._stack = collections.deque(value) if value else collections.deque()

    @property
    def input(self) -> collections.deque[str]:
        return self._input
    @input.setter
    def input(self, value) -> None:
        self._input = value = collections.deque(value or ())
        self._stack_format_width = max(len('Stack'), round((len(value)-1)/2) + 2)
        self._input_format_width = max(len('Unread input'), len(value))

    @property
    def stack_format_width(self) -> int:
        return self._stack_format_width
    @property
    def input_format_width(self) -> int:
        return self._input_format_width
    @property
    def r_rule_used_format_width(self) -> int:
        return self.__class__.R_RULE_USED_FORMAT_WIDTH
    @property
    def delta_rule_used_format_width(self) -> int:
        return self.__class__.DELTA_RULE_USED_FORMAT_WIDTH
    @property
    def state_format_width(self) -> int:
        return self.__class__.STATE_FORMAT_WIDTH

    @property
    def state(self) -> str:
        return self._state
    @state.setter
    def state(self, value) -> None:
        if value not in self.__class__.STATES:
            raise ValueError(f"Invalid state: {value!r}; possible states: {', '.join(map(str, self.__class__.STATES))}")
        self._state = value

    @property
    def delta_rule_used(self) -> None|str:
        return self._delta_rule_used
    @delta_rule_used.setter
    def delta_rule_used(self, value) -> None:
        if value is not None and not 1 <= value <= self.__class__.DELTA_RULE_COUNT:
            raise ValueError(f"Invalid delta rule: {value!r}")
        self._delta_rule_used = value

    @property
    def r_rule_used(self) -> None|str:
        return self._r_rule_used
    @r_rule_used.setter
    def r_rule_used(self, value) -> None:
        if value is not None and value not in self.__class__.R_RULES:
            raise ValueError(f"Invalid r rule: {value!r}")
        self._r_rule_used = value


    def process(self,
        input:str,
        output_file:None|io.TextIOBase=None,
        *,
        box_drawing_characters=ASCII_BOX_DRAWING_CHARACTERS
    ) -> bool:
        """Returns success or failure"""
        self.input = collections.deque(input)
        self.step = -1
        bdc = box_drawing_characters

        result = None

        for i in itertools.count():
            self.step = i
            if output_file:
                if i == 0:
                    print(self.table_output_start(bdc), file=output_file)
                print(self.table_output_current_step(bdc), file=output_file)

            if self.state == self.__class__.END_STATE:
                result = True
                break

            # get current information
            input_front = self.input[0] if self.input else None
            stack_top = self.stack[0] if self.stack else None

            # determine what needs to be done
            for k, v in self.__class__.DELTA[self.state].items():
                take_input,take_stack = k
                new_state,add_to_stack,new_delta_rule_used,new_r_rule_used = v
                if (not take_input or take_input == input_front) and (not take_stack or take_stack == stack_top):
                    break # compatible choice
            else: # no match found
                result = False
                break

            # perform appropriate actions
            if take_input: self.input.popleft()
            if take_stack: self.stack.popleft()
            self.state = new_state
            self.delta_rule_used = new_delta_rule_used
            self.r_rule_used = new_r_rule_used
            if add_to_stack:
                self.stack.extendleft(reversed(add_to_stack))

        if output_file:
            print(self.table_output_end(bdc), file=output_file)
        return result


    # overly complex formatting but we need it to be nice for the presentation!
    def table_output_start(self, bdc=UTF8_BOX_DRAWING_CHARACTERS) -> str:
        table_title = self.fmt_step('Step', 'State', 'Unread input', 'Stack', 'Delta', 'R', bdc=bdc)
        len_left = table_title.find('Delta') - 3
        len_right = len(table_title) - table_title.find('Delta')
        title = f" {bdc['bar']} ".join((
            f"{bdc['bar']} {'DPDA Processing State':^{len_left-2}}",
            f"{'Rules used':^{len_right-2}} {bdc['bar']}",
        ))
        i = title[1:].find(bdc['bar'])+1 # this is where the divider line is for the left and right
        first_line  = self.fmt_step(join=bdc['hr'],       bdc=bdc, left=bdc['corner_top_left'], right=bdc['corner_top_right']).replace(' ', bdc['hr'])
        second_line = self.fmt_step(join=bdc['bar_down'], bdc=bdc, left=bdc['bar_right'],       right=bdc['bar_left']        ).replace(' ', bdc['hr'])
        first_line  =  first_line[:i] + bdc['bar_down'] +  first_line[i+1:]
        second_line = second_line[:i] + bdc['cross']    + second_line[i+1:]
        third_line  = second_line.replace(bdc['bar_down'], bdc['cross'])
        return '\n'.join((
            first_line,
            title,
            second_line,
            table_title,
            third_line
        ))
    def table_output_current_step(self, bdc=UTF8_BOX_DRAWING_CHARACTERS) -> str:
        return self.fmt_step(
            self.step, self.state,
            (''.join(self.input) or 'e'), (''.join(self.stack) or 'e'),
            (self.delta_rule_used or ''), (self.r_rule_used or ''),
            bdc=bdc
        )
    def table_output_end(self, bdc=UTF8_BOX_DRAWING_CHARACTERS) -> str:
        return self.fmt_step(
            join=bdc['bar_up'],
            bdc=bdc,
            left=bdc['corner_bottom_left'],
            right=bdc['corner_bottom_right']
        ).replace(' ', bdc['hr'])

    @property
    def table_output_width(self) -> int:
        try:
            return self._table_output_width
        except AttributeError:
            self._table_output_width = v = len(self.fmt_step())
            return v

    def fmt_step(self,
        step:str='', state:str='',
        input:str='', stack:str='',
        dru:str='', rru:str='',
        *, left:None|str=None, right:None|str=None,
        join:None|str=None, bdc=ASCII_BOX_DRAWING_CHARACTERS
    ) -> str:
        return (f" {bdc['bar'] if join is None else join} ").join((
            f"{left or bdc['bar']} {step:>4}",
            f"{state:<{self.state_format_width}}",
            f"{input:<{self.input_format_width}}",
            f"{stack:>{self.stack_format_width}}",
            f"{dru:>{self.delta_rule_used_format_width}}",
            f"{rru:<{self.r_rule_used_format_width}} {right or bdc['bar']}",
        ))



class ProjectDPDA(DPDA):
    """
    Deterministic pushdown automata accepting L = { a^nb^n | n >= 1 }
    """

    # Structure:
    # {
    #     state: {
    #         (take_input, take_stack): (new_state, push_stack, delta_rule_number, r_rule_used)
    #     }
    # }
    DELTA = {
        'p': {
            (None, None): ('q' , 'S'  , 1, None),
        },
        'q': {
            ('a' , None): ('qa', None , 2, None),
            ('b' , None): ('qb', None , 4, None),
            ('$' , None): ('q$', None , 6, None),
        },
        'qa': {
            (None, 'a' ): ('q' , None , 3, None),
            (None, 'S' ): ('qa', 'aSb', 7, 'S -> aSb'),
        },
        'qb': {
            (None, 'b' ): ('q' , None , 5, None),
            (None, 'S' ): ('qb', None , 8, 'S -> e'),
        },
    }
    START_STATE:str = 'p'
    END_STATE:str = 'q$'



def main() -> int:
    args = sys.argv[1:]
    if not args or any(v in ('-h', '--help') for v in args):
        import textwrap
        import os
        file = os.path.basename(__file__)
        print(textwrap.dedent(
            f"""
            Process an input of language L = {{ a^nb^n$ | n >= 0 }} by deterministic pushdown automata

            Usage: {file} [input]

            Arguments:
                -h / --help : Help message
                --ascii : Disable utf-8 table formatting
                input : Input string or a value for n
                    For example: `{file} aaabbb$` is the same as `{file} 3`
            """
        ).strip())
        return 0

    ascii = False
    for v in args:
        if v == '--ascii':
            ascii = True
            break
    if ascii:
        args.remove('--ascii')

    s = args[0]

    try:
        n = int(s)
    except ValueError:
        pass
    else:
        s = 'a'*n + 'b'*n + '$'

    print(f"Processing {s}")
    result = ProjectDPDA().process(
        s,
        sys.stdout,
        box_drawing_characters=ASCII_BOX_DRAWING_CHARACTERS if ascii else UTF8_BOX_DRAWING_CHARACTERS
    )
    if result:
        print("Success")
        return 0
    else:
        print("Failure")
        return 1



if __name__ == '__main__':
    ec = main() or 0
    if not ec:
        sys.exit(ec)
