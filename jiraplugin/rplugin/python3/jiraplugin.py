import tomllib
import dataclasses

from atlassian import Jira as JiraClient
import pynvim


@pynvim.plugin
class Jira(object):

    def __init__(self, nvim: pynvim.Nvim):
        self.nvim = nvim

    @pynvim.command('Jiraticket', nargs='?')
    def show_ticket(self, args):
        config = config_from_lua('jiraplugin', self.nvim)
        filename = config['jira_config_file']
        with open(filename, 'rb') as f:
            jira_config = tomllib.load(f)
        assert jira_config is not None, f'Jira config not found: {filename}'

        self.jira = JiraClient(
            url=jira_config['JIRA_URL'],
            username=jira_config['USER_EMAIL'],
            password=jira_config['API_TOKEN'],
            cloud=True
        )

        jira_ticket = args[0] 

        ticket = self.get_ticket(jira_ticket)

        self.nvim.command('new')
        self.nvim.command('set filetype=md')
        self.nvim.current.buffer.append(ticket.splitlines())


    def get_ticket(self, issue_id: str) -> str:
        try:
            issue = self.jira.issue(issue_id)
            if issue is None:
                return f'Ticket {issue_id} not found'
            
            fields = issue.get('fields', {})

            title = fields.get('summary', 'No Title')
            description = fields.get('description', 'No Description')
            
            comments_data = self.jira.issue_get_comments(issue_id) or {}
            discussions = create_discussion(create_raw_comments(comments_data.get('comments', [])))

            discussion_text = ''
            for discussion in discussions:
                discussion_text = render_discussion(discussion, current_text=discussion_text)
                
            # TODO: Move to config
            sections = { 
                'customfield_10314': '# Feature description',
                'customfield_10312': '# Acceptance criterias',
                'customfield_10378': '# QA techinical notes'
            }
            for k, v in fields.items():
                if v is not None and k in sections.keys():
                    header = sections[k]
                    description = description + f'\n\n{header}\n\n'
                    description = description + v

            return f'#{title}\n# description\n\n{description}\n\n# Comments\n\n{discussion_text}'
        
        except Exception as e:
            return str(e)


def config_from_lua(plugin_name: str, nvim: pynvim.Nvim, default_config: dict[str, str] | None = None) -> dict[str, str]:
    default_config = default_config or {}

    # fetch lua config from lua/pynvimExample.lua
    # with this wrapper it's possible to configure this module
    # like a "native" lua module: require('module').setup(config_table)
    cfg = nvim.exec_lua(f'return require("{plugin_name}").getConfig()')

    default_config.update(cfg)
    return default_config


@dataclasses.dataclass
class RawComment:
    id: str
    parent_id: str | None
    author: str
    body: str

    def __post_init__(self):
        self.id = str(self.id)
        if self.parent_id is not None:
            self.parent_id = str(self.parent_id)

@dataclasses.dataclass
class Comment:
    author: str
    body: str
    answers: list['Comment']

    @staticmethod
    def create_from(c: RawComment, answers: list['Comment']) -> 'Comment':
        return Comment(author=c.author, body=c.body, answers=answers)

def create_raw_comments(data: list[dict]) -> list[RawComment]:
    return [RawComment(id=c['id'], parent_id=c.get('parentId'), author=c['author']['displayName'], body=c['body']) for c in data]

def create_discussion(comments: list[RawComment]) -> list[Comment]:
    roots = [c for c in comments if c.parent_id is None]
    discussions = []
    for root in roots:
        answers = create_answers_for(root.id, comments)
        discussions.append(Comment.create_from(root, answers))
    return discussions


def create_answers_for(root_id: str, comments: list[RawComment]) -> list[Comment]:
    return [Comment.create_from(c, create_answers_for(c.id, comments)) for c in comments if c.parent_id == root_id]


def render_discussion(discussion: Comment, indentation_level: int = 0, current_text: str | None = None) -> str:
    text = current_text or ''
    indentation = '\t' * indentation_level

    text = text + indentation + f'- [{discussion.author}]\n\n'
    lines = discussion.body.splitlines()
    for line in lines:
        text = text + indentation + '\t' + line + '\n' 
    text = text + '\n\n'
    text = render_answers(text, discussion.answers, indentation_level + 1)
    return text 
     

def render_answers(text: str, answers: list[Comment], indentation_level: int) -> str:
    for answer in answers:
        text = render_discussion(answer, indentation_level, text)
    return text
