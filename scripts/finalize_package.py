#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""finalize_package.py — merge cover+body PDF, rebuild ZIP deliverable."""
from pypdf import PdfWriter
import zipfile, os, datetime

F = '/home/z/my-project/registry_work/final'
D = '/home/z/my-project/download'

# 1) PDF merge
out_pdf = D + '/registry_verification_report_2026.pdf'
w = PdfWriter()
w.append(F + '/cover.pdf')
w.append(F + '/report_body.pdf')
w.write(out_pdf)
w.close()
print('pdf merged:', os.path.getsize(out_pdf), 'bytes')

# 2) ZIP rebuild
zip_path = D + '/global_video_platforms_registry_2026.zip'
files = ['global_video_platforms_registry_2026.csv',
         'global_video_platforms_registry_2026.json',
         'global_video_platforms_registry_2026.xlsx',
         'registry_verification_report_2026.pdf',
         'README.md', 'README_RU.md']
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in files:
        z.write(D + '/' + f, f)
print('zip rebuilt:', os.path.getsize(zip_path), 'bytes,', len(files), 'files')
