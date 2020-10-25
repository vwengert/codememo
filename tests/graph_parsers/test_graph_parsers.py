from subprocess import check_call
from pathlib import Path
import shlex

import pytest
from codememo.graph_parsers import get_graph_parser

THIS_DIR = Path(__file__).parent


@pytest.fixture(scope='module')
def call_graph_dot_file():
    fn_script = THIS_DIR.joinpath('script_for_call_graph.py')
    fn_dot_file = THIS_DIR.joinpath('call_graph.dot')
    cmd = (
        'pycallgraph graphviz '
        f'--output-format=dot --output-file={str(fn_dot_file)} '
        f'-- {str(fn_script)}'
    )
    result = check_call(shlex.split(cmd), cwd=THIS_DIR)
    return fn_script, fn_dot_file


class TestDotParser:
    def test_parse(self, call_graph_dot_file):
        _, fn_dot_file = call_graph_dot_file

        parser = get_graph_parser('.dot')
        node_collection = parser.parse(fn_dot_file)

        desired_node_names = [
            '__main__', '<module>', 'main', 'foo', 'bar', 'buzz', 'my_print',
            'my_print (0)', 'my_print (1)',
        ]
        desired_node_links = [
            ('__main__', '<module>'),
            ('<module>', 'main'),
            ('main', 'foo'),
            ('main', 'bar'),
            ('main', 'buzz'),
            ('foo', 'my_print'),
            ('bar', 'my_print'),
            ('buzz', 'my_print'),
        ]

        node_names = [v.snippet.name for v in node_collection]
        node_links = [
            (link.root.snippet.name, link.leaf.snippet.name.split(' ')[0])
            for link in node_collection.resolve_links()
        ]

        assert set(node_names) == set(desired_node_names)

        # Here we won't validate `root_slot` and `leaf_slot` of `NodeLink`s because
        # we cannot guarantee that order of leaf nodes generated by other tools will
        # always match to our implementation.
        assert set(node_links) == set(desired_node_links)
