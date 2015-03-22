import re

class VeryHint(object):

    """Manages hints in a buffer"""

    FORMAT = "{<VeryHint{<%s>}>}"

    INSTANCES = {}

    _RE_STRIP = re.compile(r'["\'(]')

    def __init__(self, buf):
        """Initialize VeryHint for a buffer

        :buf: TODO

        """
        self._buf = buf
        self._saved = None

        self._hints = None
        self._atCursor = None

        self._duckHints = None
        self._duckCursor = None

    def hideHints(self):
        """Hide any hints being shown"""
        self._hints = None

        if self._saved:
            for lineNo, line in self._saved.iteritems():
                self._buf[lineNo] = line

            # TODO delete the backed-up lines at the bottom

        self._saved = None

    def showHints(self, hints, atCursor):
        """Show the hints

        :hints: Array of strings
        :atCursor: Tuple of (line, col)

        """

        # first, make sure there was a change before
        #  we bother
        if self._hints == hints and self._atCursor == atCursor:
            # nothing to see here...
            return

        # hide any existing and save new
        self.hideHints()
        self._hints = hints
        self._atCursor = atCursor

        if hints is None or not len(hints):
            # nothing to do!
            return

        # find the longest hint; all hints should be
        #  rendered with same width for consistent UI
        longest = 0
        for hint in self._hints:
            longest = max(longest, len(hint))

        # now, record the lines to be replaced
        cursorLine, cursorCol = atCursor

        # vim's python cursor line starts at 1, but python
        #   buffer lines index at 0. :/
        #   at least columns are sane...?
        cursorLine -= 1

        self._saved = {}
        for i in xrange(1, len(hints) + 1):
            lineNo = cursorLine - i
            if lineNo >= 0:
                self._saved[lineNo] = self._buf[lineNo]
                # TODO backup lines at the bottom, in case of crash?

        # replace lines with hints
        i = 0
        for lineNo, line in self._saved.iteritems():
            hint = hints[i]
            remaining = longest - len(hint)

            # always pad the end
            hint = '%s ' % (hint + ' ' * remaining)            
            hintStart = cursorCol
            hintEnd = cursorCol + longest + 1

            if cursorCol > 0:
                # pad the beginning if we're not there
                # (this is just in case; otherwise should be impossible)
                hint = ' %s' % hint
                hintStart -= 1

            renderedHint = VeryHint.FORMAT % (hint)
            renderedLine = self._strip(line[:hintStart]) + renderedHint + line[hintEnd:]
            self._buf[lineNo] = renderedLine

            i += 1

    def duck(self):
        """Temporarily hide hints (if any)"""
        if self._hints:
            self._duckHints = self._hints
            self._duckCursor = self._atCursor
            self.hideHints()
        
    def unduck(self):
        """Restore temporarily hidden hints (if any)"""
        if self._duckHints and self._duckCursor:
            self.showHints(self._duckHints, self._duckCursor)
            self._duckHints = None
            self._duckCursor = None

    def _strip(self, text):
        """Clean syntax-breaking characters from text

        :text: The text from which to strip
        :returns: A new string with the characters "cleaned"

        """
        return VeryHint._RE_STRIP.sub(" ", text)
        
    @classmethod
    def forBuffer(cls, buf):
        """Get the VeryHint instance for the buffer

        :buf: Vim buffer object
        :returns: A VeryHint instance

        """
        # NB: We can't directly store this instance
        #  in the buffer vars, so we'll keep track
        #  in python by buffer number
        if cls.INSTANCES.has_key(buf.number):
            return cls.INSTANCES[buf.number]

        newInstance = VeryHint(buf)
        cls.INSTANCES[buf.number] = newInstance
        return newInstance

    @classmethod
    def cleanup(cls, bufNo=None):
        """Call when a buffer is destroyed. Different from
        simply calling hideHints() in that the VeryHint instance
        is also cleared to save memory. Not sure if GC is a big
        concern with pythin in vim, but just in case we try to
        only allocate one instance per buffer, so do your share
        and cleanup().

        :buf: (optional) The NUMBER of the buffer that was
              destroyed. If not provided, ALL instances are destroyed
        :returns: TODO

        """
        if bufNo and cls.INSTANCES.has_key(bufNo):
            # try to hide before destroying, just in case
            cls.INSTANCES[bufNo].hideHints()
            del cls.INSTANCES[bufNo]
        elif bufNo is None:
            for instance in cls.INSTANCES.itervalues():
                instance.hideHints()

            cls.INSTANCES.clear()
