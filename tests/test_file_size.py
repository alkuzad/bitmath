# -*- coding: utf-8 -*-
# The MIT License (MIT)
#
# Copyright © 2014 Tim Bielawa <timbielawa@gmail.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""
Tests to verify that string representations are accurate
"""

from . import TestCase
import bitmath
import os

class TestFileSize(TestCase):
    # expected sizes are given in bytes
    def setUp(self):
        self.byte_file = './tests/file_sizes/bytes.test'
        self.kibibyte_file = './tests/file_sizes/kbytes.test'

    #*****************************************************************
    # getsize
    #*****************************************************************

    ##################################################################
    # NIST tests
    def test_getsize_byte_system_NIST(self):
        """NIST: getsize reports the correct type and size for byte sized files"""
        expected = bitmath.Byte(bytes=38)
        result = bitmath.getsize(self.byte_file, system=bitmath.NIST)
        self.assertEqual(result, expected)
        self.assertIs(type(result), bitmath.Byte)

    def test_getsize_kibibyte_system_NIST(self):
        """NIST: getsize reports the correct type and size for kibibyte sized files"""
        expected = bitmath.KiB(bytes=1024)
        result = bitmath.getsize(self.kibibyte_file, system=bitmath.NIST)
        self.assertEqual(result, expected)
        self.assertIs(type(result), bitmath.KiB)

    ##################################################################
    # SI tests
    def test_getsize_byte_system_SI(self):
        """SI: getsize reports the correct type and size for byte sized files"""
        expected = bitmath.Byte(bytes=38)
        result = bitmath.getsize(self.byte_file, system=bitmath.SI)
        self.assertEqual(result, expected)
        self.assertIs(type(result), bitmath.Byte)

    def test_getsize_kibibyte_system_SI(self):
        """SI: getsize reports the correct type and size for kibibyte sized files"""
        expected = bitmath.kB(bytes=1024)
        result = bitmath.getsize(self.kibibyte_file, system=bitmath.SI)
        self.assertEqual(result, expected)
        self.assertIs(type(result), bitmath.kB)

    #*****************************************************************
    # listdir
    #*****************************************************************
    def test_listdir_nosymlinks(self):
        """listdir: no symbolic links in tree measures right

Assume a directory tree where no sub-directories are symbolic links::

    $ tree ./tests/listdir_nosymlinks
    ./tests/listdir_nosymlinks
    `-- depth1
        `-- depth2
            |-- 1024_byte_file
            `-- 10_byte_file

    2 directories, 2 files

And the files, ``tests/listdir_nosymlinks/depth1/depth2/10_byte_file``
and ``tests/listdir_nosymlinks/depth1/depth2/1024_byte_file`` are 10
Bytes and 1024 Bytes in size, respectively.

Then:

    >>> for f in bitmath.listdir('./tests/listdir_nosymlinks'):
    ...     print f

Would yield 2-tuple's of:

    ('/path/tests/listdir_nosymlinks/depth1/depth2/10_byte_file', Byte(10.0))
    ('/path/tests/listdir_nosymlinks/depth1/depth2/1024_byte_file', KiB(1.0))
        """
        # Call with relpath=True so the paths are easier to verify
        contents = list(bitmath.listdir('./tests/listdir_nosymlinks/', relpath=True))

        # There should only be two files discovered.
        self.assertEqual(len(contents), int(2))

        # Ensure the returned paths match the expected paths
        self.assertEqual(contents[0][0],
                         'tests/listdir_nosymlinks/depth1/depth2/10_byte_file')
        self.assertEqual(contents[1][0],
                         'tests/listdir_nosymlinks/depth1/depth2/1024_byte_file')

        # Ensure the measured sizes are what we expect
        self.assertEqual(contents[0][1], bitmath.Byte(10.0))
        self.assertEqual(contents[1][1], bitmath.KiB(1.0))

    def test_listdir_symlinks_nofollow(self):
        """listdir: symbolic links in tree not followed

Similar assumptions as in test_listdir_nosymlinks, except the
directory structure looks like this:

    $ tree tests/listdir_symlinks
    tests/listdir_symlinks
    |-- 10_byte_file_link -> ../listdir/10_byte_file
    `-- depth1
        `-- depth2
            `-- 10_byte_file

    2 directories, 2 files

        """
        # Call with relpath=True so the paths are easier to verify
        contents = list(bitmath.listdir('./tests/listdir_symlinks/', relpath=True))

        # There should only be one file discovered. The symlink isn't
        # dereferenced
        self.assertEqual(len(contents), int(1))

        # Ensure the returned path matches the expected path
        self.assertEqual(contents[0][0], 'tests/listdir_symlinks/depth1/depth2/10_byte_file')

        # Ensure the measured size is what we expect
        self.assertEqual(contents[0][1], bitmath.Byte(10.0))

    def test_listdir_symlinks_follow(self):
        """listdir: symbolic links in tree are followed

Same assumptions as in test_listdir_symlinks_nofollow.
        """
        # Call with relpath=True so the paths are easier to verify
        contents = list(bitmath.listdir('./tests/listdir_symlinks/',
                                        followlinks=True,
                                        relpath=True))

        # There should two files discovered
        self.assertEqual(len(contents), int(2))

        # Ensure the returned path matches the expected path
        self.assertEqual(contents[0][0], 'tests/listdir_symlinks/10_byte_file_link')
        self.assertEqual(contents[1][0], 'tests/listdir_symlinks/depth1/depth2/10_byte_file')

        # Ensure the measured size is what we expect
        self.assertEqual(contents[0][1], bitmath.Byte(10.0))
        self.assertEqual(contents[1][1], bitmath.Byte(10.0))

    def test_listdir_symlinks_follow_relpath_false(self):
        """listdir: symlinks followed, absolute paths are returned

Same assumptions as in test_listdir_symlinks_follow. Difference is
that the 0th item of the tuple returns a fully qualified path.
        """
        # Call with relpath=True so the paths are easier to verify
        contents = list(bitmath.listdir('./tests/listdir_symlinks/',
                                        followlinks=True))

        # There should two files discovered
        self.assertEqual(len(contents), int(2))

        # Ensure the returned path matches the expected path and
        # begins with the present working directory
        pwd = os.path.realpath('.')
        self.assertEqual(contents[0][0], os.path.join(pwd, contents[0][0]))
        self.assertEqual(contents[1][0], os.path.join(pwd, contents[1][0]))

        # Ensure the measured size is what we expect
        self.assertEqual(contents[0][1], bitmath.Byte(10.0))
        self.assertEqual(contents[1][1], bitmath.Byte(10.0))
