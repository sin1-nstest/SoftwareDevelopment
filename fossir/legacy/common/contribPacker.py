# This file is part of fossir.
# Copyright (C) 2002 - 2017 European Organization for Nuclear Research (CERN).
#
# fossir is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# fossir is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with fossir; if not, see <http://www.gnu.org/licenses/>.

import os
import string
import tempfile
import zipfile

from fossir.core.config import config
from fossir.legacy.common.utils import utf8rep


class ZIPFileHandler:
    def __init__(self):
        fh, name = tempfile.mkstemp(prefix="fossir", dir=config.TEMP_DIR)
        os.fdopen(fh).close()
        try:
            self._file = zipfile.ZipFile(name, "w", zipfile.ZIP_DEFLATED, allowZip64=True)
        except RuntimeError:
            self._file = zipfile.ZipFile(name, "w", allowZip64=True)
        self._name = name

    def _normalisePath(self, path):
        forbiddenChars = string.maketrans(" :()*?<>|\"", "__________")
        path = path.translate(forbiddenChars)
        return path

    def add(self, name, path):
        name = utf8rep(name)
        self._file.write(str(path), self._normalisePath(name))

    def addNewFile(self, name, bytes):
        if not self.hasFile(name):
            name = utf8rep(name)
            self._file.writestr(name, bytes)

    def addDir(self, path):
        normalized_path = os.path.join(self._normalisePath(path), "fossir_file.dat")
        if not self.hasFile(normalized_path):
            self.addNewFile(normalized_path, "# fossir File")

    def close(self):
        self._file.close()

    def getPath(self):
        return self._name

    def hasFile(self, fileName):
        for zfile in self._file.infolist():
            if zfile.filename == fileName:
                return True
        return False
