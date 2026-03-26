import json

import botocore.session
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection
import pynvim


@pynvim.plugin
class OpenSearchPlugin(object):

    def __init__(self, nvim):
        self.nvim = nvim
        self._session = None
        self._opensearch = None
        self._profile = None

    @pynvim.function('TestFunction', sync=True)
    def testfunction(self, args):
        return 3

    @pynvim.command('SearchCommand', nargs='*', range='')
    def search(self, args, range):
        buffer_lines = [line for line in self.nvim.current.buffer[:] if len(line) != 0]
        if buffer_lines == []:
            return

        json_lines = '\n'.join(buffer_lines)

        data = json.loads(json_lines)
        index_name = data['index']
        profile = data['profile']
        query_body = data['query']

        response_lines = self._search(query_body, index_name, profile)

        self.nvim.command('new')
        self.nvim.command('set filetype=json')
        self.nvim.current.buffer.append(response_lines)


    """
    @pynvim.autocmd('BufEnter', pattern='*.py', eval='expand("<afile>")', sync=True)
    def on_bufenter(self, filename):
        self.nvim.out_write('testplugin is in ' + filename + '\n')
    """

    def _search(self, body: dict, index_name: str, profile: str) -> list[str]:
        self._setup(profile)
        response = self._opensearch.search(body=body, index=index_name)
        return json.dumps(response, indent=2).split('\n')

    def _setup(self, profile: str):
        self._setup_botocore_session(profile)
        self._setup_opensearch()


    def _setup_botocore_session(self, profile: str):
        if self._session is None or self._session.profile != profile:
            self._session = botocore.session.get_session()
            self._session.set_config_variable("profile", profile)

    def _setup_opensearch(self):
        if self._opensearch is None:
            credentials = self._session.get_credentials()
            region = 'eu-north-1'
            service = 'es'
            awsauth = AWS4Auth(credentials.access_key, credentials.secret_key,
                               region, service, session_token=credentials.token)

            self._opensearch = OpenSearch(
                hosts=[{'host': 'localhost', 'port': 8443}],
                http_auth=awsauth,
                use_ssl=True,
                verify_certs=False,
                connection_class=RequestsHttpConnection,
                timeout=300
            )
