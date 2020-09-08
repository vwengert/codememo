from pathlib import Path
import json
import pytest

from codememo.objects import (
    Snippet, Node, NodeLink, NodeIndexLink, NodeCollection
)


@pytest.fixture
def dummy_snippet_data():
    data = {
        'name': 'foo.py',
        'content': 'def foo():\n    print("foo")',
        'lang': 'python',
        'line_start': 5,
        'path': '~/data/foo.py',
        'url': 'https://foo.bar/snippet/foo.py',
    }
    return data


@pytest.fixture
def dummy_node_data():
    snippet_data = {
        'name': 'foo.py',
        'content': 'def foo():\n    print("foo")',
        'lang': 'python',
        'line_start': 5,
        'path': '~/data/foo.py',
        'url': 'https://foo.bar/snippet/foo.py',
    }
    node_data = {
        'uuid': '554baf0e-b43a-4a52-a384-161e1f196320',
        'snippet': snippet_data,
        'comment': 'just some comment...',
        'root': None,
        'leaves': [],
        'ref_info': None,
    }
    return node_data


@pytest.fixture
def dummy_node_collection_data():
    fn_data = Path(Path(__file__).parent, 'node_collection_data.json')
    with open(fn_data, 'r') as f:
        nodes_data = json.load(f)
    return nodes_data


@pytest.fixture
def dummy_nodes():
    data = [
        ('foo.py', 'def foo():\n    print("foo")', 'python'),
        ('bar.py', 'def bar():\n    print("bar")', 'python'),
        ('buzz.py', 'def buzz():\n    print("buzz")', 'python'),
        ('gin.py', 'def gin():\n    print("gin")', 'python'),
        ('fizz.py', 'def fizz():\n    print("fizz")', 'python'),
        ('greet.c', 'int main(void) {\n  printf("Hello world!\n");  \n return 0;\n}', 'c'),
    ]
    snippets = [Snippet(v[0], v[1], lang=v[2]) for v in data]
    return [Node(v) for v in snippets]


@pytest.fixture
def dummy_nodes_multiple_tree():
    data = [
        ('0_0', 'def foo():\n    print("foo")', 'python'),
        ('0_1', 'def bar():\n    print("bar")', 'python'),
        ('0_2', 'def buzz():\n    print("buzz")', 'python'),
        ('0_3', 'def gin():\n    print("gin")', 'python'),
        ('0_4', 'def fizz():\n    print("fizz")', 'python'),
        ('1_0', 'def foo():\n    print("foo")', 'python'),
        ('1_1', 'def bar():\n    print("bar")', 'python'),
        ('1_2', 'def buzz():\n    print("buzz")', 'python'),
        ('1_3', 'def gin():\n    print("gin")', 'python'),
        ('1_4', 'def fizz():\n    print("fizz")', 'python'),
    ]
    snippets = [Snippet(v[0], v[1], lang=v[2]) for v in data]
    nodes = [Node(v) for v in snippets]

    # Set dependencies
    nodes[0].add_leaf(nodes[1])
    nodes[0].add_leaf(nodes[2])
    nodes[2].add_leaf(nodes[3])
    nodes[5].add_leaf(nodes[6])
    nodes[6].add_leaf(nodes[7])
    nodes[6].add_leaf(nodes[8])
    nodes[7].add_leaf(nodes[9])
    return nodes


class TestSnippet:
    def test__to_dict(self, dummy_snippet_data):
        data = dummy_snippet_data
        snippet = Snippet(
            data['name'], data['content'], line_start=data.get('line_start'),
            lang=data.get('lang'), path=data.get('path'), url=data.get('url'),
        )
        assert snippet.to_dict() == data

    def test__from_dict(self, dummy_snippet_data):
        data = dummy_snippet_data
        snippet = Snippet.from_dict(data)
        assert snippet.to_dict() == data


class TestNode:
    def test__to_dict(self, dummy_node_data):
        data = dummy_node_data
        node = Node(
            Snippet.from_dict(data['snippet']), comment=data.get('comment'),
            uuid=data.get('uuid')
        )
        assert node.to_dict() == data

    def test__from_dict(self, dummy_node_data):
        data = dummy_node_data
        node = Node.from_dict(data)
        assert node.to_dict() == data

    def test__add_leaf__self_reference(self, dummy_nodes):
        A = dummy_nodes[0]
        with pytest.raises(ValueError, match='Self reference'):
            A.add_leaf(A)

    def test__add_leaf__circular_reference(self, dummy_nodes):
        A, B = dummy_nodes[0], dummy_nodes[1]
        A.add_leaf(B)
        with pytest.raises(ValueError, match='Circular reference'):
            B.add_leaf(A)

    def test__add_leaf__multiple_root(self, dummy_nodes):
        A, B, C = dummy_nodes[0], dummy_nodes[1], dummy_nodes[2]
        A.add_leaf(B)
        with pytest.raises(ValueError, match='Multiple root'):
            C.add_leaf(B)

    def test__add_leaf__exceed_range(self, dummy_nodes):
        A, B = dummy_nodes[0], dummy_nodes[1]
        n_lines = A.snippet.n_lines
        with pytest.raises(ValueError, match='should be in the range'):
            A.add_leaf(B, 0)
        with pytest.raises(ValueError, match='should be in the range'):
            A.add_leaf(B, n_lines + 1)


class TestNodeCollection:
    def test__to_dict(self, dummy_node_collection_data):
        data = dummy_node_collection_data
        node_collection = NodeCollection.from_dict(data)
        assert node_collection.to_dict() == data

    def test__resolve_link(self, dummy_nodes_multiple_tree):
        nodes = dummy_nodes_multiple_tree
        node_collection = NodeCollection(nodes)
        links = node_collection.resolve_links()
        desired_links = [
            NodeLink(nodes[0], 0, nodes[1], 0),
            NodeLink(nodes[0], 0, nodes[2], 1),
            NodeLink(nodes[2], 0, nodes[3], 0),
            NodeLink(nodes[5], 0, nodes[6], 0),
            NodeLink(nodes[6], 0, nodes[7], 0),
            NodeLink(nodes[6], 0, nodes[8], 1),
            NodeLink(nodes[7], 0, nodes[9], 0),
        ]
        assert len(links) == len(desired_links)
        assert links == desired_links

    def test__resolve_index_link(self, dummy_nodes_multiple_tree):
        nodes = dummy_nodes_multiple_tree
        node_collection = NodeCollection(nodes)
        links = node_collection.resolve_index_links()
        desired_links = [
            NodeIndexLink(0, 0, 1, 0),
            NodeIndexLink(0, 0, 2, 1),
            NodeIndexLink(2, 0, 3, 0),
            NodeIndexLink(5, 0, 6, 0),
            NodeIndexLink(6, 0, 7, 0),
            NodeIndexLink(6, 0, 8, 1),
            NodeIndexLink(7, 0, 9, 0),
        ]
        assert len(links) == len(desired_links)
        assert links == desired_links

    def test__resolve_tree(self, dummy_nodes_multiple_tree):
        nodes = dummy_nodes_multiple_tree
        node_collection = NodeCollection(nodes)
        layer_collection, orphans = node_collection.resolve_tree()
        desired_trees = [
            [[nodes[0]], [nodes[1], nodes[2]], [nodes[3]]],
            [[nodes[5]], [nodes[6]], [nodes[7], nodes[8]], [nodes[9]]],
        ]
        assert len(layer_collection) == len(desired_trees)
        assert orphans == [nodes[4]]
        for i, tree in enumerate(desired_trees):
            assert tree == layer_collection[i]
