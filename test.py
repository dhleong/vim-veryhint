#!/usr/bin/env python

import sys
import unittest

sys.path.insert(0, './autoload')
from veryhint import VeryHint

class DummyBuffer(object):

    """Mock of a VimBuffer for unittesting"""

    def __init__(self, contents):
        """Create a new DummyBuffer with contents

        :contents: A string or a list of string

        """
        if type(contents) == list:
            self._contents = contents
        else:
            self._contents = contents.split("\n")
        self.number = 0

        self.edits = 0

        # Buffers don't have cursors, but we'll make
        #  it convenient to locate one.
        #  NB: Vim python cursor starts at (1, 0),
        #  but buffer lines index from zero. Sigh.
        self.cursor = (1, 0)
        for line in xrange(0, len(self._contents)):
            col = self[line].find("|")
            if col >= 0:
                self.cursor = (line + 1, col)
                self[line] = self[line][:col] + self[line][col+1:]
                self.edits = 0 # reset edits count
                break

    def __len__(self):
        return len(self._contents)

    def __getitem__(self, key):
        return self._contents[key]

    def __setitem__(self, key, val):
        self._contents[key] = val
        self.edits += 1

class VeryHintTests(unittest.TestCase):

    def setUp(self):
        self._originalFormat = VeryHint.FORMAT
        VeryHint.FORMAT = "{%s}" # braces represent syntax markers
        self.fooBuf = DummyBuffer("bars\nfoo(|")

    def tearDown(self):
        VeryHint.FORMAT = self._originalFormat
        VeryHint.cleanup()

    def test_findCursor(self):
        """Make sure our cursor init works"""
        buf = self.fooBuf
        self.assertTupleEqual(buf.cursor, (2, 4))

    def test_noRoom(self):
        """No room? Just show nothing; rare case anyway"""
        buf = DummyBuffer("foo(|)")
        VeryHint.forBuffer(buf).showHints(["biz, baz"], buf.cursor)
        self.assertEquals(buf[0], "foo()")
        self.assertEquals(buf.edits, 0)
        VeryHint.forBuffer(buf).hideHints()
        self.assertEquals(buf[0], "foo()")
        self.assertEquals(buf.edits, 0)

    def test_oneLine(self):
        buf = self.fooBuf
        VeryHint.forBuffer(buf).showHints(["biz, baz"], buf.cursor)
        self.assertEquals(buf[0], "bar{ biz, baz }")
        self.assertEquals(buf.edits, 1)
        VeryHint.forBuffer(buf).hideHints()
        self.assertEquals(buf[0], "bars")
        self.assertEquals(buf.edits, 2)

    def test_twoLines(self):
        line1 = 'Ship serenity = new Ship();'
        line2 = 'serenity.setName("Serenity").setType("Firefly");'
        line3 = 'serenity.addCrew(|'
        buf = DummyBuffer([
            line1,
            line2,
            line3
        ])

        VeryHint.forBuffer(buf).showHints(
                ["String name, Job job", "Crew crew"],
                buf.cursor)
        self.assertEquals(buf[0], "Ship serenity = { String name, Job job }")
        self.assertEquals(buf[1], 'serenity.setName{ Crew crew            }Firefly");')
        self.assertEquals(buf[2], line3[:-1]) # strip the "cursor"
        self.assertEquals(buf.edits, 2)
        VeryHint.forBuffer(buf).hideHints()
        self.assertEquals(buf[0], line1)
        self.assertEquals(buf[1], line2)
        self.assertEquals(buf[2], line3[:-1])
        self.assertEquals(buf.edits, 4)

    def test_noChangeNoEdits(self):
        line1 = 'Ship serenity = new Ship();'
        line2 = 'serenity.setName("Serenity").setType("Firefly");'
        line3 = 'serenity.addCrew(|'
        buf = DummyBuffer([
            line1,
            line2,
            line3
        ])

        VeryHint.forBuffer(buf).showHints(
                ["String name, Job job", "Crew crew"],
                buf.cursor)
        self.assertEquals(buf.edits, 2)

        # type something
        buf[2] = 'serenity.addCrew(C'
        self.assertEquals(buf.edits, 3)

        # re-show at same spot, no edits
        VeryHint.forBuffer(buf).showHints(
                ["String name, Job job", "Crew crew"],
                buf.cursor) # NB cursor hasn't changed
        self.assertEquals(buf.edits, 3) 

    def test_duck(self):
        buf = self.fooBuf
        VeryHint.forBuffer(buf).showHints(["biz, baz"], buf.cursor)
        self.assertEquals(buf[0], "bar{ biz, baz }")
        VeryHint.forBuffer(buf).duck()
        self.assertEquals(buf[0], "bars")
        VeryHint.forBuffer(buf).unduck()
        self.assertEquals(buf[0], "bar{ biz, baz }")
        VeryHint.forBuffer(buf).hideHints()
        self.assertEquals(buf[0], "bars")

    def test_redunDuck(self):
        buf = self.fooBuf
        VeryHint.forBuffer(buf).duck()
        self.assertEquals(buf[0], "bars") # no changes, no errors

        VeryHint.forBuffer(buf).showHints(["biz, baz"], buf.cursor)
        self.assertEquals(buf[0], "bar{ biz, baz }")

        VeryHint.forBuffer(buf).duck()
        self.assertEquals(buf[0], "bars")

        # still the same:
        VeryHint.forBuffer(buf).duck()
        self.assertEquals(buf[0], "bars")

        VeryHint.forBuffer(buf).unduck()
        self.assertEquals(buf[0], "bar{ biz, baz }")

        # no confusion please
        VeryHint.forBuffer(buf).unduck()
        self.assertEquals(buf[0], "bar{ biz, baz }")

        VeryHint.forBuffer(buf).hideHints()
        self.assertEquals(buf[0], "bars")

if __name__ == '__main__':
    unittest.main()
