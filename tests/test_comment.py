# coding: utf-8
#
# Copyright © 2013-2015 Ejwa Software. All rights reserved.
#
# This file is part of gitinspector.
#
# gitinspector is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gitinspector is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gitinspector. If not, see <http://www.gnu.org/licenses/>.

import os
import unittest
import gitinspector.comment


# Returns the number of lines in a given `commented_file` with
# extension `extension` that are comments.
def __test_extension__(commented_file, extension):
    base = os.path.dirname(os.path.realpath(__file__))
    tex_file = open(base + commented_file, "r", encoding="utf-8")
    tex = tex_file.readlines()
    tex_file.close()

    is_inside_comment = False
    comment_counter = 0
    for i in tex:
        (_, is_inside_comment) = gitinspector.comment.\
                                 handle_comment_block(is_inside_comment,
                                                      extension, i)
        if is_inside_comment or gitinspector.comment.is_comment(extension, i):
            comment_counter += 1

    return comment_counter


# Test the number of comments inside two different files inside the
# resources/ dir
class TexFileTest(unittest.TestCase):
    def test(self):
        comment_counter = __test_extension__("/resources/commented_file.tex", "tex")
        self.assertEqual(comment_counter, 39)


class CppFileTest(unittest.TestCase):
    def test(self):
        comment_counter = __test_extension__("/resources/commented_file.cpp", "cpp")
        self.assertEqual(comment_counter, 27)
