#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

import sys
import os

from urllib.parse import unquote
from urllib.parse import urlsplit

ASCII_CHARS   = set(chr(x) for x in range(128))
URL_SAFE      = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    'abcdefghijklmnopqrstuvwxyz'
                    '0123456789' '#' '_.-/~')
IRI_UNSAFE = ASCII_CHARS - URL_SAFE

# returns a quoted IRI (not a URI)                                                                                     
def quoteurl(href):
    if isinstance(href,bytes):
        href = href.decode('utf-8')
    (scheme, netloc, path, query, fragment) = urlsplit(href, scheme="", allow_fragments=True)
    if scheme != "":
        scheme += "://"
        href = href[len(scheme):]
    result = []
    for char in href:
        if char in IRI_UNSAFE:
            char = "%%%02x" % ord(char)
        result.append(char)
    return scheme + ''.join(result)

# unquotes url/iri                                                                                                     
def unquoteurl(href):
    if isinstance(href,bytes):
        href = href.decode('utf-8')
    href = unquote(href)
    return href


def relativePath(to_bkpath, start_dir):
    # remove any trailing path separators from both paths
    dsegs = to_bkpath.rstrip('/').split('/')
    ssegs = start_dir.rstrip('/').split('/')
    if dsegs == ['']: dsegs=[]
    if ssegs == ['']: ssegs=[]
    res = []
    i = 0
    for s1, s2 in zip(dsegs, ssegs):
        if s1 != s2: break
        i+=1
    for p in range(i, len(ssegs),1): res.append('..')
    for p in range(i, len(dsegs),1): res.append(dsegs[p])
    return '/'.join(res)


def resolveRelativeSegmentsInFilePath(file_path):
    res = []
    segs = file_path.split('/')
    for i in range(len(segs)):
        if segs[i] == '.': continue
        if segs[i] == '..':
            if res:
                res.pop()
            else:
                print("Error resolving relative path segments")
        else:
            res.append(segs[i])
    return '/'.join(res)


def buildRelativePath(from_bkpath, to_bkpath):
    if from_bkpath == to_bkpath: return ""
    return relativePath(to_bkpath, startingDir(from_bkpath))


def buildBookPath(dest_relpath, start_folder):
    if start_folder == "" or start_folder.strip() == "": 
        return dest_relpath;
    bookpath = start_folder.rstrip('/') + '/' + dest_relpath
    return resolveRelativeSegmentsInFilePath(bookpath)


def startingDir(file_path):
    ssegs = file_path.split('/')
    ssegs.pop()
    return '/'.join(ssegs)

    
def longestCommonPath(bookpaths):
    # handle special cases
    if len(bookpaths) == 0: return ""
    if len(bookpaths) == 1: return startingDir(bookpaths[0]) + '/'
    # split all paths into segment lists
    fpaths = []
    seglen = []
    for bookpath in bookpaths:
        segs = bookpath.split('/')
        seglen.append(len(segs))
        fpaths.append(segs)
    minlen = min(seglen)
    res = []
    numpaths = len(fpaths)
    # build up list of common path segments in res
    for i in range(minlen):
        amatch = True
        aseg = fpaths[0][i]
        j = 1;
        while(amatch and j < numpaths):
            amatch = aseg == fpaths[j][i]
            j += 1
        if amatch:
            res.append(fpaths[0][i])
        else: 
            break
    if not res or len(res) == 0:
        return ""
    return '/'.join(res) + '/'


def main():
    argv = sys.argv
    p1 = 'This/is/the/../../end.txt'
    print('Testing resolveRelativeSegmentsInFilePath(file_path)')
    print('    file_path: ', p1)
    print(resolveRelativeSegmentsInFilePath(p1))
    print('    ')

    p1 = 'hello.txt'
    p2 = 'goodbye.txt'
    print('Testing buildRelativePath(from_bkpath,to_bkpath')
    print('    from_bkpath: ',p1)
    print('    to_bkpath:   ',p2)
    print(buildRelativePath(p1, p2))
    print('    ')

    p1 = 'OEBPS/Text/book1/chapter1.xhtml'
    p2 = 'OEBPS/Text/book2/chapter1.xhtml'
    print('Testing buildRelativePath(from_bkpath,to_bkpath)')
    print('    from_bkpath: ',p1)
    print('    to_bkpath:   ',p2)
    print(buildRelativePath(p1, p2))
    print('    ')
    
    p1 = 'OEBPS/package.opf'
    p2 = 'OEBPS/Text/book1/chapter1.xhtml'
    print('Testing buildRelativePath(from_bkpath, to_bkpath)')
    print('    from_bkpath: ',p1)
    print('    to_bkpath:   ',p2)
    print(buildRelativePath(p1,p2))
    print('    ')

    p1 = '../../Images/image.png'
    p2 = 'OEBPS/Text/book1/'
    print('Testing buildBookPath(destination_href, start_dir)')
    print('    destination_href: ',p1)
    print('    starting_dir:     ',p2)
    print(buildBookPath(p1, p2))
    print('    ')

    p1 = 'image.png'
    p2 = ''
    print('Testing buildBookPath(destination_href, start_dir)')
    print('    destination_href: ',p1)
    print('    starting_dir:     ',p2)
    print(buildBookPath(p1, p2))
    print('    ')

    p1 = 'content.opf'
    print('Testing startingDir(bookpath')
    print('    bookpath: ',p1)
    print('"'+ startingDir(p1)+'"')
    print('    ')

    bookpaths = []
    bookpaths.append('OEBPS/book1/text/chapter1.xhtml')
    bookpaths.append('OEBPS/book1/html/chapter2.xhtml')
    bookpaths.append('OEBPS/book2/text/chapter3.xhtml')
    print('Testing longestCommonPath(bookpaths)')
    print('    bookpaths: ',bookpaths)
    print('"'+ longestCommonPath(bookpaths)+'"')
    print('    ')

    return 0


if __name__ == '__main__':
    sys.exit(main())
