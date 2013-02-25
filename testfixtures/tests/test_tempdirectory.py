# Copyright (c) 2008-2013 Simplistix Ltd
# See license.txt for license details.

import os

from doctest import DocTestSuite, ELLIPSIS
from mock import Mock, call
from shutil import rmtree
from tempfile import mkdtemp
from testfixtures import TempDirectory, Replacer, should_raise, compare
from unittest import TestCase, TestSuite, makeSuite

from logging import getLogger

from ..compat import Unicode
from .compat import catch_warnings

class DemoTempDirectory:

    def test_return_path(self): # pragma: no branch
        """
        If you want the path created when you use `write`, you
        can do:
        
        >>> temp_dir.write('filename','data',path=True)
        '...filename'
        """

    def test_ignore(self): # pragma: no branch
        """
        TempDirectories can also be set up to ignore certain files:
        
        >>> d = TempDirectory(ignore=('.svn',))
        >>> p = d.write('.svn','stuff')
        >>> temp_dir.listdir()
        No files or directories found.
        """
        
    def test_ignore_regex(self): # pragma: no branch
        """
        TempDirectories can also be set up to ignore certain files:
        
        >>> d = TempDirectory(ignore=('^\.svn$','.pyc$'))
        >>> p = d.write('.svn','stuff')
        >>> p = d.write('foo.svn','')
        >>> p = d.write('foo.pyc','')
        >>> p = d.write('bar.pyc','')
        >>> d.listdir()
        foo.svn
        """
        
class TestTempDirectory:

    def test_cleanup(self): # pragma: no branch
        """
        >>> d = TempDirectory()
        >>> p = d.path
        >>> os.path.exists(p)
        True
        >>> p = d.write('something','stuff')
        >>> d.cleanup()
        >>> os.path.exists(p)
        False
        """

    def test_cleanup_all(self): # pragma: no branch
        """
        If you create several TempDirecories during a doctest,
        or if exceptions occur while running them,
        it can create clutter on disk.
        For this reason, it's recommended to use the classmethod
        TempDirectory.cleanup_all() as a tearDown function
        to remove them all:

        >>> d1 = TempDirectory()
        >>> d2 = TempDirectory()

        Some sanity checks:

        >>> os.path.exists(d1.path)
        True
        >>> p1 = d1.path
        >>> os.path.exists(d2.path)
        True
        >>> p2 = d2.path

        Now we show the function in action:

        >>> TempDirectory.cleanup_all()

        >>> os.path.exists(p1)
        False
        >>> os.path.exists(p2)
        False
        """

    def test_with_statement(self): # pragma: no branch
        """
        >>> with TempDirectory() as d:
        ...    p = d.path
        ...    print(os.path.exists(p))
        ...    path = d.write('something','stuff')
        ...    os.listdir(p)
        ...    with open(os.path.join(p,'something')) as f:
        ...        print(repr(f.read()))
        True
        ['something']
        'stuff'
        >>> os.path.exists(p)
        False
        """

    def test_listdir_sort(self): # pragma: no branch
       """
        >>> with TempDirectory() as d:
        ...    p = d.write('ga','')
        ...    p = d.write('foo1','')
        ...    p = d.write('Foo2','')
        ...    p = d.write('g.o','')
        ...    d.listdir()
        Foo2
        foo1
        g.o
        ga
        """
class TempDirectoryTests(TestCase):

    def test_write_with_slash_at_start(self):
        with TempDirectory() as d:
            write = should_raise(d.write,ValueError(
                    'Attempt to read or write outside the temporary Directory'
                    ))
            write('/some/folder','stuff')

    def test_makedir_with_slash_at_start(self):
        with TempDirectory() as d:
            makedir = should_raise(d.makedir,ValueError(
                    'Attempt to read or write outside the temporary Directory'
                    ))
            makedir('/some/folder','stuff')

    def test_read_with_slash_at_start(self):
        with TempDirectory() as d:
            read = should_raise(d.read,ValueError(
                    'Attempt to read or write outside the temporary Directory'
                    ))
            read('/some/folder')

    def test_listdir_with_slash_at_start(self):
        with TempDirectory() as d:
            listdir = should_raise(d.listdir,ValueError(
                    'Attempt to read or write outside the temporary Directory'
                    ))
            listdir('/some/folder','stuff')

    def test_check_dir_with_slash_at_start(self):
        with TempDirectory() as d:
            checkdir = should_raise(d.check_dir,ValueError(
                    'Attempt to read or write outside the temporary Directory'
                    ))
            checkdir('/some/folder','stuff')

    def test_check_all_with_slash_at_start(self):
        with TempDirectory() as d:
            checkall = should_raise(d.check_all,ValueError(
                    'Attempt to read or write outside the temporary Directory'
                    ))
            checkall('/some/folder','stuff')

    def test_dont_cleanup_with_path(self):
        d = mkdtemp()
        fp = os.path.join(d,'test')
        with open(fp,'w') as f:
            f.write('foo')
        try:
            td = TempDirectory(path=d)
            self.assertEqual(d,td.path)
            td.cleanup()
            # checks
            self.assertEqual(os.listdir(d),['test'])
            with open(fp) as f:
                self.assertEqual(f.read(),'foo')
        finally:
            rmtree(d)
        
    def test_dont_create_with_path(self):
        d = mkdtemp()
        rmtree(d)
        td = TempDirectory(path=d)
        self.assertEqual(d,td.path)
        self.failIf(os.path.exists(d))


    def test_check_sort(self):
        with TempDirectory() as d:
            d.write('ga','')
            d.write('foo1','')
            d.write('Foo2','')
            d.write('g.o','')
            d.check(
                'Foo2','foo1','g.o','ga'
                )

    def test_check_dir_sort(self):
        with TempDirectory() as d:
            d.write('foo/ga','')
            d.write('foo/foo1','')
            d.write('foo/Foo2','')
            d.write('foo/g.o','')
            d.check_dir('foo',
                'Foo2','foo1','g.o','ga'
                )

    def test_check_all_sort(self):
        with TempDirectory() as d:
            d.write('ga','')
            d.write('foo1','')
            d.write('Foo2','')
            d.write('g.o','')
            d.check_all('',
                'Foo2','foo1','g.o','ga'
                )
        
    def test_check_all_tuple(self):
        with TempDirectory() as d:
            d.write('a/b/c','')
            d.check_all(('a','b'),
                'c'
                )
        
    def test_recursive_ignore(self):
        with TempDirectory(ignore=['.svn']) as d:
            d.write('.svn/rubbish','')
            d.write('a/.svn/rubbish','')
            d.write('a/b/.svn','')
            d.write('a/b/c','')
            d.write('a/d/.svn/rubbish','')
            d.check_all('',
                'a/',
                'a/b/',
                'a/b/c',
                'a/d/',
                )

    def test_path(self):
        with TempDirectory() as d:
            expected1 = d.makedir('foo',path=True)
            expected2 = d.write('baz/bob','',path=True)
            expected3 = d.getpath('a/b/c')

            actual1 = d.getpath('foo')
            actual2 = d.getpath('baz/bob')
            actual3 = d.getpath(('a','b','c'))

        self.assertEqual(expected1,actual1)
        self.assertEqual(expected2,actual2)
        self.assertEqual(expected3,actual3)
        
    def test_atexit(self):
        m = Mock()
        with Replacer() as r:
            # make sure the marker is false, other tests will
            # probably have set it
            r.replace('testfixtures.TempDirectory.atexit_setup', False)
            r.replace('atexit.register', m.register)

            d = TempDirectory()

            expected = [call.register(d.atexit)]

            compare(expected, m.mock_calls)

            with catch_warnings(record=True) as w:
                d.atexit()
                self.assertTrue(len(w), 1)
                compare(str(w[0].message), ( # pragma: no branch
                    "TempDirectory instances not cleaned up by shutdown:\n" +
                    d.path
                    ))
                
            d.cleanup()

            compare(set(), TempDirectory.instances)
            
            # check re-running has no ill effects
            d.atexit()
        
# using a set up and teardown function
# gets rid of the need for the imports in
# doc tests

def setUp(test):
    test.globs['temp_dir']=TempDirectory()

def tearDown(test):
    TempDirectory.cleanup_all()
    
def test_suite():
    return TestSuite((
        DocTestSuite(setUp=setUp,tearDown=tearDown,
                     optionflags=ELLIPSIS),
        makeSuite(TempDirectoryTests),        
        ))
