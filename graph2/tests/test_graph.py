import graph, v3
import unittest, types


class Base(unittest.TestCase):
    def assert_nodelist_len(self, node_list, count):
        self.assertIsInstance(node_list, graph.NodeList)
        self.assertLen(node_list, count)

    def assertLen(self, iterable, count):
        return self.assertEqual(len(iterable), count)


class TestGraph(Base):

    def test_get(self):
        g = v3.functions()
        r = g.get('fa')

        assert callable(r)
        self.assertIsInstance(r, types.FunctionType)

        # self.assertEqual('foo'.upper(), 'FOO')
        # self.assertTrue('FOO'.isupper())
        # self.assertFalse('Foo'.isupper())

    def test_start_node(self):
        g = v3.functions()
        start_node = g.get_start_node()
        node_list = start_node.next

        self.assertIsInstance(start_node, graph.ExitNode)
        self.assert_nodelist_len(node_list, 6)

    def test_get_node_next_nodelist(self):
        g = v3.functions()
        node_list = g.get_node('fa').next
        self.assert_nodelist_len(node_list, 3)


    def test_get_node_is_valid(self):
        """get_node() function is_valid()"""
        g = v3.alphabet(print_table=False)

        self.assertTrue(g.get_node('D').is_valid())
        self.assertFalse(g.get_node('ef').is_valid())

    def test_get_node_values(self):
        """get_node() function is_valid()"""
        g = v3.alphabet(print_table=False)
        nv = g.get('A')
        n = g.get_node(nv)
        nl = n.next

        self.assertEqual(nv, 'A')
        self.assertListEqual(list(nl.values()), ['B', 'N', 'P'])

    def test_deterministic_summation(self):
        """Iterate all callers and sum the `int` returns"""
        g = v3.functions()
        c = g.get_chain()
        v = ()
        for f in range(len(c)):
            ev = enumerate(c[f].values())
            r = sum([x(i) or 0 for i,x  in ev if callable(x)])
            v += (r,)

        expected = (26, 26, 26, 15, 20, 8, 26, 25, 18, 18, 18,
            33, 9, 11, 11, 11, 22, 15, 33, 32, 11, 10)

        self.assertTupleEqual(v,expected)
