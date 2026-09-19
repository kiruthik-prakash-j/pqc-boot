#!/usr/bin/env python3
"""
Academic Mid-Semester Report Generator (MS Word .docx)
Course: BITS ZG628T Dissertation | BITS Pilani
Author: Kiruthik Prakash J (2024HT01586)

Strict Academic Formatting Rules:
  - Single Title/Cover Page (Page 1) with official BITS Pilani seal/logo.
  - Certificate (Page 2) with formal supervisor and candidate signature blocks.
  - Table of Contents (Page 3) with dynamic Word TOC field and updated page numbers.
  - Lists of Figures & Tables (Page 3) with right-aligned margin tab stops.
  - Main headings (x.) start on a FRESH PAGE.
  - Subheadings (x.x) flow naturally on the SAME PAGE within their section.
  - Font Size: Strict minimum of 12 pt across all body text, tables, captions, TOC, and lists.
  - Section 3: Table 1 placed cleanly under heading to fit entire 14-row table on Page 10.
  - Section 5.2: Dissertation Plan of Work table placed cleanly on Page 15 without awkward breaks.
  - Robust XML tables: cantSplit, tblHeader, padded cell margins.
"""

import os
import sys
import io
import base64
import html
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BITS_LOGO_BASE64 = "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"

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=70, bottom=70, left=100, right=100):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f"""
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    """)
    tcPr.append(tcMar)

def set_table_borders(table, color="B0B0B0", sz="4", val="single"):
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(f"""
            <w:tblBorders {nsdecls("w")}>
                <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            </w:tblBorders>
        """)
        tblPr[0].append(borders)

def make_table_robust(table):
    for i, row in enumerate(table.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        if i == 0:
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

def add_fld_page_number(run):
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

def add_list_toc_line(p, title, page_num):
    p.paragraph_format.space_before = Pt(1.5)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15

    pPr = p._element.get_or_add_pPr()
    tabs = parse_xml(r'''
        <w:tabs %s>
            <w:tab w:val="right" w:leader="none" w:pos="8640"/>
        </w:tabs>
    ''' % nsdecls('w'))
    pPr.append(tabs)

    run_t = p.add_run(title)
    run_t.font.name = 'Arial'
    run_t.font.size = Pt(12)

    run_tab = p.add_run('\t')
    run_tab.font.name = 'Arial'
    run_tab.font.size = Pt(12)

    run_p = p.add_run(str(page_num))
    run_p.font.name = 'Arial'
    run_p.font.size = Pt(12)

def generate_toc_sdt(entries):
    paragraphs = []
    for i, (title, page, is_major, indent) in enumerate(entries):
        fld_begin = ""
        fld_end = ""
        if i == 0:
            fld_begin = '<w:r><w:fldChar w:fldCharType="begin"/><w:instrText xml:space="preserve"> TOC \\h \\u \\z \\t "Heading 1,1,Heading 2,2,Heading 3,3,Heading 4,4,Heading 5,5,Heading 6,6,"</w:instrText><w:fldChar w:fldCharType="separate"/></w:r>'
        if i == len(entries) - 1:
            fld_end = '<w:r><w:fldChar w:fldCharType="end"/></w:r>'

        ind_attr = ' w:left="360" w:firstLine="0"' if indent > 0 else ''
        ind_tag = f'<w:ind{ind_attr}/>' if ind_attr else ''
        anchor = "_heading=h.l52iw1m1m2iu" if i == 0 else "_heading="
        b_val = "1" if is_major else "0"
        escaped_title = html.escape(title)

        p_xml = f"""<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:pPr>
                <w:widowControl w:val="0"/>
                <w:tabs><w:tab w:val="right" w:leader="none" w:pos="12000"/></w:tabs>
                <w:spacing w:after="0" w:before="60" w:line="240" w:lineRule="auto"/>
                {ind_tag}
                <w:rPr>
                    <w:b w:val="{b_val}"/>
                    <w:bCs w:val="{b_val}"/>
                    <w:color w:val="000000"/>
                    <w:u w:val="none"/>
                </w:rPr>
            </w:pPr>
            {fld_begin}
            <w:hyperlink w:anchor="{anchor}">
                <w:r>
                    <w:rPr>
                        <w:rFonts w:ascii="Arial" w:cs="Arial" w:eastAsia="Arial" w:hAnsi="Arial"/>
                        <w:b w:val="{b_val}"/>
                        <w:bCs w:val="{b_val}"/>
                        <w:color w:val="000000"/>
                        <w:sz w:val="24"/>
                        <w:szCs w:val="24"/>
                        <w:u w:val="none"/>
                    </w:rPr>
                    <w:t xml:space="preserve">{escaped_title}</w:t>
                    <w:tab/>
                    <w:t xml:space="preserve">{page}</w:t>
                </w:r>
            </w:hyperlink>
            {fld_end}
        </w:p>"""
        paragraphs.append(p_xml)

    sdt_xml = f"""<w:sdt xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
        <w:sdtPr>
            <w:id w:val="-368827121"/>
            <w:docPartObj>
                <w:docPartGallery w:val="Table of Contents"/>
                <w:docPartUnique w:val="1"/>
            </w:docPartObj>
        </w:sdtPr>
        <w:sdtContent>
            {"".join(paragraphs)}
        </w:sdtContent>
    </w:sdt>"""
    return parse_xml(sdt_xml)

def build_midsem_report(output_path=None):
    if output_path is None:
        output_path = "submission-docs/midsem-report/Midsem_Report_ESZG628T_2024HT01586.docx"

    doc = Document()

    # Page setup - A4 Portrait with 1.25" binding left margin
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1.0)

        # Footer: Centered Page Number (12 pt)
        footer = section.footer
        p_footer = footer.paragraphs[0]
        p_footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_footer.paragraph_format.space_before = Pt(0)
        p_footer.paragraph_format.space_after = Pt(0)
        run_f = p_footer.add_run()
        run_f.font.name = 'Arial'
        run_f.font.size = Pt(12)
        add_fld_page_number(run_f)

    # Global Style Configurations
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Arial'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0x20, 0x21, 0x24)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # Heading 1 Style (Main headings x.)
    h1_style = doc.styles['Heading 1']
    h1_style.font.name = 'Arial'
    h1_style.font.size = Pt(16)
    h1_style.font.bold = True
    h1_style.font.color.rgb = RGBColor(0x11, 0x18, 0x27)
    h1_style.paragraph_format.space_before = Pt(18)
    h1_style.paragraph_format.space_after = Pt(6)
    h1_style.paragraph_format.keep_with_next = True

    # Heading 2 Style (Subheadings x.x)
    h2_style = doc.styles['Heading 2']
    h2_style.font.name = 'Arial'
    h2_style.font.size = Pt(14)
    h2_style.font.bold = True
    h2_style.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)
    h2_style.paragraph_format.space_before = Pt(14)
    h2_style.paragraph_format.space_after = Pt(4)
    h2_style.paragraph_format.keep_with_next = True

    def add_heading_1(text):
        p = doc.add_paragraph(style='Heading 1')
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(16)
        run.font.bold = True
        return p

    def add_heading_2(text):
        p = doc.add_paragraph(style='Heading 2')
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(14)
        run.font.bold = True
        return p

    # ==========================================
    # 1. TITLE / COVER PAGE (Page 1 - Single Unified Cover with BITS Seal)
    # ==========================================
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(36)
    p.paragraph_format.space_after = Pt(20)
    run = p.add_run("POST-QUANTUM FIRMWARE AUTHENTICATION: DESIGN AND IMPLEMENTATION OF A QUANTUM-RESISTANT SECURE BOOT MECHANISM\n")
    run.font.name = 'Arial'
    run.font.size = Pt(18)
    run.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(24)
    r1 = p.add_run("BITS ZG628T: Dissertation\n")
    r1.font.name = 'Arial'
    r1.font.size = Pt(14)
    r1.font.bold = True

    r2 = p.add_run("by\n\n")
    r2.font.name = 'Arial'
    r2.font.size = Pt(12)
    r2.font.italic = True

    r3 = p.add_run("Kiruthik Prakash J\n")
    r3.font.name = 'Arial'
    r3.font.size = Pt(14)
    r3.font.bold = True

    r4 = p.add_run("2024HT01586\n")
    r4.font.name = 'Arial'
    r4.font.size = Pt(12)
    r4.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(20)
    r_work = p.add_run("Dissertation work carried out at\n")
    r_work.font.name = 'Arial'
    r_work.font.size = Pt(12)
    r_work.font.italic = True

    r_org = p.add_run("Qualcomm India Private Limited, Hyderabad\n")
    r_org.font.name = 'Arial'
    r_org.font.size = Pt(13)
    r_org.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(20)
    r_sub = p.add_run("Submitted in partial fulfilment of M.Tech in Embedded Systems\ndegree programme\n\n")
    r_sub.font.name = 'Arial'
    r_sub.font.size = Pt(12)

    r_sup_lbl = p.add_run("Under the Supervision of\n\n")
    r_sup_lbl.font.name = 'Arial'
    r_sup_lbl.font.size = Pt(12)
    r_sup_lbl.font.italic = True

    r_sup = p.add_run("Deepak Kumar\nSenior Lead Software Engineer\n")
    r_sup.font.name = 'Arial'
    r_sup.font.size = Pt(13)
    r_sup.font.bold = True

    # Anchored BITS Pilani Seal Logo
    logo_data = base64.b64decode(BITS_LOGO_BASE64)
    logo_stream = io.BytesIO(logo_data)
    run_logo = p.add_run()
    run_logo.font.name = 'Arial'
    run_logo.font.size = Pt(13)
    run_logo.font.bold = True

    pic = run_logo.add_picture(logo_stream, width=Inches(1.0718), height=Inches(1.0341))
    inline = pic._inline
    r_id = inline.xpath('.//a:blip/@r:embed')[0]
    anchor_xml = f'''
    <wp:anchor {nsdecls("wp", "a", "pic", "r")} allowOverlap="1" behindDoc="0" distB="0" distT="0" distL="0" distR="0" hidden="0" layoutInCell="1" locked="0" relativeHeight="0" simplePos="0">
      <wp:simplePos x="0" y="0"/>
      <wp:positionH relativeFrom="page"><wp:posOffset>3403763</wp:posOffset></wp:positionH>
      <wp:positionV relativeFrom="page"><wp:posOffset>7380945</wp:posOffset></wp:positionV>
      <wp:extent cx="980121" cy="945641"/>
      <wp:effectExtent b="0" l="0" r="0" t="0"/>
      <wp:wrapTopAndBottom distB="0" distT="0"/>
      <wp:docPr id="3" name="image1.jpg"/>
      <a:graphic>
        <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
          <pic:pic>
            <pic:nvPicPr>
              <pic:cNvPr id="0" name="image1.jpg"/>
              <pic:cNvPicPr preferRelativeResize="0"/>
            </pic:nvPicPr>
            <pic:blipFill>
              <a:blip r:embed="{r_id}"/>
              <a:srcRect b="0" l="0" r="0" t="0"/>
              <a:stretch><a:fillRect/></a:stretch>
            </pic:blipFill>
            <pic:spPr>
              <a:xfrm><a:off x="0" y="0"/><a:ext cx="980121" cy="945641"/></a:xfrm>
              <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
              <a:ln/>
            </pic:spPr>
          </pic:pic>
        </a:graphicData>
      </a:graphic>
    </wp:anchor>
    '''
    anchor_elem = parse_xml(anchor_xml)
    drawing = inline.getparent()
    drawing.remove(inline)
    drawing.append(anchor_elem)

    r_co = p.add_run("Qualcomm India Private Limited, Hyderabad")
    r_co.font.name = 'Arial'
    r_co.font.size = Pt(13)
    r_co.font.bold = True

    # Spacing paragraph
    p_sp = doc.add_paragraph()
    p_sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sp.paragraph_format.space_after = Pt(20)

    # University and date paragraph
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(20)
    run_uni = p.add_run("BIRLA INSTITUTE OF TECHNOLOGY & SCIENCE\nPILANI (RAJASTHAN)\n")
    run_uni.font.name = 'Arial'
    run_uni.font.size = Pt(13)
    run_uni.font.bold = True

    run_date = p.add_run("SEPTEMBER 2026")
    run_date.font.name = 'Arial'
    run_date.font.size = Pt(12)
    run_date.font.bold = True

    # ==========================================
    # 2. CERTIFICATE PAGE (Page 2 - Fresh Page)
    # ==========================================
    p_cert = doc.add_paragraph()
    p_cert.paragraph_format.keep_with_next = True
    r_br = p_cert.add_run()
    r_br.add_break(WD_BREAK.PAGE)
    r_cert_title = p_cert.add_run("CERTIFICATE")
    r_cert_title.font.name = 'Arial'
    r_cert_title.font.size = Pt(16)
    r_cert_title.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("This is to certify that the dissertation entitled ")
    r_title = p.add_run("“Post-Quantum Firmware Authentication: Design and Implementation of a Quantum-Resistant Secure Boot Mechanism”")
    r_title.bold = True
    p.add_run(" and submitted by ")
    r_name = p.add_run("Kiruthik Prakash J (ID: 2024HT01586)")
    r_name.bold = True
    p.add_run(" in partial fulfilment of the requirement of ")
    r_deg = p.add_run("M.Tech in Embedded Systems")
    r_deg.bold = True
    p.add_run(" of BITS Pilani, embodies the work done by him under my supervision at ")
    r_org = p.add_run("Qualcomm India Private Limited, Hyderabad")
    r_org.bold = True
    p.add_run(".")

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(40)

    sig_table = doc.add_table(rows=4, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for row in sig_table.rows:
        for cell in row.cells:
            cell.width = Inches(3.0)
            set_cell_margins(cell, 40, 40, 60, 60)

    # Formal electronic signature blocks
    r_sig0_0 = sig_table.rows[0].cells[0].paragraphs[0].add_run("_/s/ Deepak Kumar____________")
    r_sig0_0.font.name = 'Arial'
    r_sig0_0.font.size = Pt(12)
    r_sig0_0.font.bold = True

    r_sig0_1 = sig_table.rows[0].cells[1].paragraphs[0].add_run("_/s/ Kiruthik Prakash J______")
    r_sig0_1.font.name = 'Arial'
    r_sig0_1.font.size = Pt(12)
    r_sig0_1.font.bold = True

    r_sig1 = sig_table.rows[1].cells[0].paragraphs[0].add_run("Deepak Kumar\nSupervisor\nSenior Lead Software Engineer\nQualcomm India Private Limited")
    r_sig1.font.bold = True
    r_sig1.font.size = Pt(12)

    r_sig2 = sig_table.rows[1].cells[1].paragraphs[0].add_run("Kiruthik Prakash J\nID: 2024HT01586\nM.Tech Embedded Systems\nBITS Pilani")
    r_sig2.font.bold = True
    r_sig2.font.size = Pt(12)

    sig_table.rows[3].cells[0].paragraphs[0].add_run("Date: 19/09/2026\nPlace: Hyderabad").font.size = Pt(12)
    sig_table.rows[3].cells[1].paragraphs[0].add_run("Date: 19/09/2026\nPlace: Hyderabad").font.size = Pt(12)

    # ==========================================
    # 3. TABLE OF CONTENTS & LISTS PAGE (Page 3 - Fresh Page)
    # ==========================================
    doc.add_page_break()
    add_heading_1("TABLE OF CONTENTS")

    doc.add_paragraph()  # Empty paragraph before TOC field

    toc_entries = [
        ("1. MODULES IN POST-QUANTUM SECURE BOOT SYSTEM", 3, True, 0),
        ("1.1 Core Cryptographic Verification Engine", 4, False, 0.25),
        ("1.2 IoT & Microcontroller Target: MCUboot Bootloader Module", 5, False, 0.25),
        ("1.3 Embedded Linux Target: Das U-Boot FIT Verification Module", 5, False, 0.25),
        ("1.4 Enterprise / Server Target: EDKII UEFI SecurityPkg Module", 6, False, 0.25),
        ("1.5 Hardware Root-of-Trust (RoT) & eFuse Key Binding Module", 6, False, 0.25),
        ("1.6 Offline Firmware Signing & Container Tooling Module", 6, False, 0.25),
        ("1.7 Multi-Target Emulation & Automated Verification Harness", 7, False, 0.25),
        ("2. FUNCTIONAL BLOCK DIAGRAM & ARCHITECTURAL DESCRIPTION", 8, True, 0),
        ("2.1 System Architecture Overview", 8, False, 0.25),
        ("2.2 Secure Boot Execution Sequence & Cryptographic Flow", 9, False, 0.25),
        ("3. MAJOR TECHNICAL SPECIFICATIONS OF PQC SECURE BOOT", 10, True, 0),
        ("4.1 Zero Dynamic Memory Allocation (Zero-Malloc Policy)", 11, False, 0.25),
        ("4.2 Strict Static SRAM Budgeting (< 4 KB ROM Bounds)", 11, False, 0.25),
        ("4.3 Hardware Root-of-Trust Key Hash Binding & eFuse Storage", 11, False, 0.25),
        ("4.4 Tamper Robustness & Non-Negotiable Fault Rejection", 11, False, 0.25),
        ("4.5 Constant-Time Cryptographic Execution & Side-Channel Mitigation", 12, False, 0.25),
        ("5. EMPIRICAL BENCHMARKING, PROFILING & FUTURE PLAN", 13, True, 0),
        ("5.1 MCUboot on ARM Cortex-M4 Trade-Off Benchmark & Stack Profiling", 13, False, 0.25),
        ("5.2 Mid-Semester Progress Status (Plan of Work)", 15, False, 0.25),
        ("5.3 Remaining Tasks & Deliverables for Final Dissertation", 16, False, 0.25),
        ("6. ABBREVIATIONS", 17, True, 0),
        ("7. REFERENCES & LITERATURE REVIEW", 19, True, 0),
    ]

    sdt_elem = generate_toc_sdt(toc_entries)
    doc._body._element.append(sdt_elem)

    doc.add_paragraph()  # Empty paragraph after TOC

    p_lf = doc.add_paragraph()
    r_lf = p_lf.add_run("List of Figures")
    r_lf.font.name = 'Arial'
    r_lf.font.size = Pt(14)
    r_lf.font.bold = True

    figs = [
        ("Figure 1: Modular Architecture of Post-Quantum Secure Boot System", 8),
        ("Figure 2: Functional Block Diagram & Secure Boot Execution Flow", 9)
    ]
    for title, page in figs:
        p = doc.add_paragraph()
        add_list_toc_line(p, title, page)

    doc.add_paragraph()  # Empty paragraph between lists

    p_lt = doc.add_paragraph()
    r_lt = p_lt.add_run("List of Tables")
    r_lt.font.name = 'Arial'
    r_lt.font.size = Pt(14)
    r_lt.font.bold = True

    tbls = [
        ("Table 1: Technical Specifications & Cryptographic Parameters", 10),
        ("Table 2: MCUboot ARM Cortex-M4 Trade-Off Benchmark (Classical vs PQC)", 13),
        ("Table 3: Dissertation Plan of Work & Mid-Semester Status", 15),
        ("Table 4: Table of Abbreviations & Acronyms", 17)
    ]
    for title, page in tbls:
        p = doc.add_paragraph()
        add_list_toc_line(p, title, page)

    # ==========================================
    # 4. SECTION 1: MODULES IN PQC SECURE BOOT (Page 4 - Fresh Page)
    # ==========================================
    p_h1 = doc.add_paragraph(style='Heading 1')
    p_h1.paragraph_format.keep_with_next = True
    bm_start = parse_xml(r'<w:bookmarkStart %s w:id="0" w:name="_heading=h.l52iw1m1m2iu" w:colFirst="0" w:colLast="0"/>' % nsdecls('w'))
    bm_end = parse_xml(r'<w:bookmarkEnd %s w:id="0"/>' % nsdecls('w'))
    p_h1._p.append(bm_start)
    p_h1._p.append(bm_end)
    r_br = p_h1.add_run()
    r_br.add_break(WD_BREAK.PAGE)
    r_h1 = p_h1.add_run("1. MODULES IN POST-QUANTUM SECURE BOOT SYSTEM")
    r_h1.font.name = 'Arial'
    r_h1.font.size = Pt(16)
    r_h1.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("The Post-Quantum Cryptography (PQC) Secure Boot infrastructure (pqc-boot) is architected as a modular, hardware-agnostic, and zero-dynamic-memory framework designed to authenticate bare-metal firmware across the complete embedded spectrum—from resource-constrained microcontrollers to enterprise multi-core servers. The complete system consists of seven primary functional modules:")

    modules_list = [
        ("(a) Core Cryptographic Verification Engine (pqc_crypto, ml_dsa, sphincs_plus, lms, sha256, shake256)"),
        ("(b) IoT & Microcontroller Bootloader Module (MCUboot with PQC TLV tags on ARM Cortex-M4)"),
        ("(c) Embedded Linux Bootloader Module (Das U-Boot with FIT Device Tree Blob on RISC-V 64-bit)"),
        ("(d) Enterprise / Server Firmware Module (EDKII / UEFI SecurityPkg DxeImageVerificationLib on Cortex-A57 SMP)"),
        ("(e) Hardware Root-of-Trust (RoT) & eFuse Key Binding Module (rot_key)"),
        ("(f) Offline Firmware Signing & Container Tooling Module (imgtool, mkimage, sign_firmware.py)"),
        ("(g) Multi-Target Emulation & Automated Verification Harness (tests, QEMU platform runners)")
    ]
    for m in modules_list:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_after = Pt(2.5)
        r = p.add_run(m)
        r.font.name = 'Arial'
        r.font.size = Pt(12)
        r.font.bold = True

    # 1.1 Flows on same page
    add_heading_2("1.1 Core Cryptographic Verification Engine")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("The core cryptographic engine (located in the firmware module firmware/src/pqc_crypto.c) serves as the centralized, static-memory cryptographic service layer. It encapsulates NIST-standardized and RFC-specified post-quantum signature schemes alongside required symmetric primitives:")

    crypto_sub = [
        ("ML-DSA-44 (NIST FIPS 204)", "Module-Lattice-Based Digital Signature Algorithm (formerly Dilithium2). Operates over polynomial rings R_q = Z_q[X]/(X^256 + 1) with modulus q = 8,380,417. The engine defines public key structures (1,312 bytes), private key structures (2,560 bytes), and signature structures (2,420 bytes). Forward and inverse Number Theoretic Transforms (NTT), Montgomery modular reductions, and uniform polynomial sampling routines are implemented."),
        ("SPHINCS+ / SLH-DSA (NIST FIPS 205)", "Stateless Hash-Based Digital Signature Algorithm (SLH-DSA-128f parameter set). Relies solely on the collision resistance of cryptographic hash functions without algebraic lattice assumptions. Utilizes Winternitz One-Time Signatures (WOTS+) and Forest of Random Subsets (FORS) multi-layer hypertree constructions with a compact 32-byte public key (PK.seed || PK.root) and an allocated signature buffer of up to 18,000 bytes."),
        ("LMS / LMOTS (RFC 8554 / RFC 8708)", "Leighton-Micali Stateful Hash-Based Signature scheme using LMOTS-SHA256_N32_W4 one-time signatures and LMS_SHA256_M32_H10 Merkle trees. Features a 56-byte public key containing the tree type, LMOTS type, 16-byte identifier I, and 32-byte root node K."),
        ("Symmetric Hashing Primitives", "Implements zero-heap SHA-256 (FIPS 180-4) and SHAKE-256 Keccak extensible-output functions (FIPS 202). In the current milestone, signature authentication combines pre-hashing (mu = SHA256(PK || msg)), challenge seed derivation (c_tilde = SHAKE256(mu, 32)), and active polynomial NTT arithmetic.")
    ]
    for name, desc in crypto_sub:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_after = Pt(3)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_b = p.add_run(f"• {name}: ")
        r_b.font.bold = True
        r_b.font.size = Pt(12)
        r_d = p.add_run(desc)
        r_d.font.size = Pt(12)

    # 1.2 Flows on same page
    add_heading_2("1.2 IoT & Microcontroller Target: MCUboot Bootloader Module")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("The MCUboot module (real_world/mcuboot/) integrates post-quantum firmware validation into the leading open-source 32-bit microcontroller secure bootloader:")

    mcuboot_items = [
        ("PQC Type-Length-Value (TLV) Header Extensions", "Defined custom TLV record identifiers in boot/bootutil/include/bootutil/image.h: IMAGE_TLV_ML_DSA_44 (0x80), IMAGE_TLV_SPHINCS_PLUS (0x81), IMAGE_TLV_LMS (0x82), and IMAGE_TLV_PQC_PUBKEY (0x88)."),
        ("Zero-Allocation Verification Hook", "Implemented bootutil_pqc.c, hooking bootutil_pqc_verify_ml_dsa_44() directly into bootutil_img_validate(). The routine traverses image TLVs, extracts public key digests, verifies RoT bindings, and authenticates image payloads without heap usage."),
        ("Host Signing Utility (imgtool)", "Extended scripts/imgtool/main.py and keys/pqc.py to support the command imgtool keygen -k keys/ml_dsa_key.json -t ml-dsa-44 and automated trailer encapsulation during imgtool sign.")
    ]
    for name, desc in mcuboot_items:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_after = Pt(3)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_b = p.add_run(f"• {name}: ")
        r_b.font.bold = True
        r_b.font.size = Pt(12)
        r_d = p.add_run(desc)
        r_d.font.size = Pt(12)

    # 1.3 Flows naturally
    add_heading_2("1.3 Embedded Linux Target: Das U-Boot FIT Verification Module")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("The Das U-Boot integration module (real_world/uboot/) incorporates PQC verification into the standard Flattened Image Tree (FIT) mechanism used across ARM and RISC-V embedded Linux deployments:")

    uboot_items = [
        ("Crypto Dispatcher Registration", "Registered post-quantum signature handlers in boot/image-sig.c using the U-Boot driver macro U_BOOT_CRYPTO_ALGO(ml_dsa_44), U_BOOT_CRYPTO_ALGO(sphincs_plus), and U_BOOT_CRYPTO_ALGO(lms)."),
        ("FIT Signature Verification Engine", "Created lib/pqc/pqc_fit_verify.c and lib/pqc/pqc-verify.c. The verification driver extracts image nodes from device tree blobs (.itb), validates the property algo = \"sha256,ml-dsa-44\", fetches public keys referenced by key-name-hint, and executes verification."),
        ("Host mkimage Tool Integration", "Updated tools/Makefile and image-sig-host.c to compile PQC verification and signing engines directly into the host mkimage utility binary, enabling automated FIT image compilation via .its scripts.")
    ]
    for name, desc in uboot_items:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_after = Pt(3)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_b = p.add_run(f"• {name}: ")
        r_b.font.bold = True
        r_b.font.size = Pt(12)
        r_d = p.add_run(desc)
        r_d.font.size = Pt(12)

    # 1.4 Flows naturally
    add_heading_2("1.4 Enterprise / Server Target: EDKII UEFI SecurityPkg Module")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("The EDKII / UEFI module (real_world/edk2/) addresses enterprise server architectures running 64-bit multi-core processors. Firmware authentication occurs during the Driver Execution Environment (DXE) phase of UEFI Secure Boot:")

    edk2_items = [
        ("Post-Quantum Object Identifiers (OIDs)", "Defined ASN.1 Object Identifiers in SecurityPkg/Include/Library/PqcVerify.h: OID_ML_DSA_44 (2.16.840.1.101.3.4.3.17), OID_SPHINCS_PLUS (2.16.840.1.101.3.4.3.20), and OID_LMS_HASH (1.2.840.113549.1.9.16.3.17)."),
        ("PKCS#7 Verification Integration", "Implemented Pkcs7VerifyPqc.c and integrated it into DxeImageVerificationLib. The module parses PE/COFF certificate tables, decodes Authenticode digital signatures, and authenticates .efi OS loader binaries against Root-of-Trust keys stored in UEFI Authenticated Variables (db)."),
        ("Multi-Core SMP Reentrancy", "Eliminated static mutable globals from the DXE verification path, guaranteeing thread safety and reentrancy across multi-core symmetric multiprocessing (SMP) server nodes.")
    ]
    for name, desc in edk2_items:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_after = Pt(3)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_b = p.add_run(f"• {name}: ")
        r_b.font.bold = True
        r_b.font.size = Pt(12)
        r_d = p.add_run(desc)
        r_d.font.size = Pt(12)

    # 1.5 Flows naturally
    add_heading_2("1.5 Hardware Root-of-Trust (RoT) & eFuse Key Binding Module")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("Because post-quantum public keys are significantly larger than classical keys (e.g., 1,312 bytes for ML-DSA-44 vs. 32 bytes for ECDSA P-256), physical on-chip One-Time Programmable (OTP) eFuse arrays cannot store raw PQC public keys directly. The RoT module (firmware/src/rot_key.c) addresses this physical constraint through a two-stage binding model:")

    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.space_after = Pt(3)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r1 = p.add_run("1. Hardware eFuse Hash Commitment: ")
    r1.font.bold = True
    r1.font.size = Pt(12)
    p.add_run("A 256-bit SHA-256 hash of the authorized Root Public Key is burned into OTP eFuse storage or immutable Boot ROM constants.")

    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.space_after = Pt(3)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r2 = p.add_run("2. Header Public Key Verification: ")
    r2.font.bold = True
    r2.font.size = Pt(12)
    p.add_run("During boot, the bootloader reads the full public key embedded in the firmware header, computes its SHA-256 digest, and executes rot_key_verify_hash(). Verification aborts immediately upon hash mismatch, preventing unauthorized key injection.")

    # 1.6 Flows naturally
    add_heading_2("1.6 Offline Firmware Signing & Container Tooling Module")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("The offline tooling suite (firmware/scripts/sign_firmware.py, mcuboot/scripts/imgtool, uboot/tools/mkimage) automates cryptographic keypair generation, firmware binary digest computation, signature generation, and binary image container packaging. It encapsulates the binary with the unified pqc_image_header_t containing the magic number 0x50514342 ('PQCB'), header version, payload length, execution entry point, algorithm ID, RoT key ID, 32-byte public key hash, signature length, and signature payload.")

    # 1.7 Flows naturally
    add_heading_2("1.7 Multi-Target Emulation & Automated Verification Harness")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("To validate firmware execution under real-world machine constraints without requiring custom silicon fabrication, QEMU system emulation environments were configured for three diverse instruction set architectures (ISAs):")

    emu_targets = [
        ("ARM Cortex-M4", "Emulated via qemu-system-arm -M mps2-an385, validating bare-metal Cortex-M memory maps and UART console output."),
        ("RISC-V 64-bit", "Emulated via qemu-system-riscv64 -M virt -cpu rv64, validating Machine and Supervisor mode handoff and OpenSBI compatibility."),
        ("ARM Cortex-A57 4-Core SMP", "Emulated via qemu-system-aarch64 -M virt -cpu cortex-a57 -smp 4, validating multi-core thread safety and reentrancy.")
    ]
    for target, desc in emu_targets:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_after = Pt(3)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_b = p.add_run(f"• {target}: ")
        r_b.font.bold = True
        r_b.font.size = Pt(12)
        r_d = p.add_run(desc)
        r_d.font.size = Pt(12)

    # ==========================================
    # 5. SECTION 2: FUNCTIONAL BLOCK DIAGRAM (Page 8 - Fresh Page)
    # ==========================================
    doc.add_page_break()
    add_heading_1("2. FUNCTIONAL BLOCK DIAGRAM & ARCHITECTURAL DESCRIPTION")

    add_heading_2("2.1 System Architecture Overview")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("The complete system architecture operates across four distinct hierarchical tiers: (1) Offline Signing and Tooling, (2) Real-World Target Bootloader Integrations, (3) Core Zero-Malloc Cryptographic Verification and Hardware Root of Trust, and (4) Heterogeneous Emulated Hardware Execution Platforms. Figure 1 illustrates this multi-tier architectural layout.")

    fig1_path = "submission-docs/midsem-report/figure1_architecture.png"
    if os.path.exists(fig1_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(fig1_path, width=Inches(5.8))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(8)
        r_cap = p_cap.add_run("Figure 1: Modular Architecture of Post-Quantum Secure Boot System")
        r_cap.font.name = 'Arial'
        r_cap.font.size = Pt(12)
        r_cap.font.bold = True

    # 2.2 Flows to Figure 2 page break to keep image full-sized and pristine
    doc.add_page_break()
    add_heading_2("2.2 Secure Boot Execution Sequence & Cryptographic Flow")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("The secure bootloader execution sequence is designed as a fail-closed, deterministic verification pipeline. At every phase, failures result in immediate panic and execution halt, preventing any execution of unauthorized, tampered, or improperly signed firmware binaries. Figure 2 illustrates the functional sequence from power-on reset to payload handoff.")

    fig2_path = "submission-docs/midsem-report/figure2_functional_flow.png"
    if os.path.exists(fig2_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(fig2_path, width=Inches(5.8))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(8)
        r_cap = p_cap.add_run("Figure 2: Functional Block Diagram & Secure Boot Execution Flow")
        r_cap.font.name = 'Arial'
        r_cap.font.size = Pt(12)
        r_cap.font.bold = True

    # ==========================================
    # 6. SECTION 3: TECHNICAL SPECIFICATIONS (Page 10 - Fresh Page)
    # ==========================================
    doc.add_page_break()
    add_heading_1("3. MAJOR TECHNICAL SPECIFICATIONS OF PQC SECURE BOOT")

    # Followed directly by Table 1 so the complete 14-row table fits cleanly on Page 10
    doc.add_paragraph()

    t1_data = [
        ("Parameter / Metric", "ML-DSA-44 (Lattice-Based)", "SPHINCS+ (Stateless Hash)", "LMS (Stateful Hash)"),
        ("Standard Specification", "NIST FIPS 204 (Dilithium2)", "NIST FIPS 205 (SLH-DSA-128f)", "RFC 8554 / RFC 8708"),
        ("Underlying Hard Problem", "Module-LWE / Module-SIS", "Hash Collision Resistance", "One-Time Sig / Merkle Tree"),
        ("Quantum Security Level", "Category 1 (128-bit quantum)", "Category 1 (128-bit quantum)", "Category 1 (128-bit quantum)"),
        ("Public Key Size", "1,312 bytes", "32 bytes", "56 bytes"),
        ("Signature Size", "2,420 bytes", "16,032 bytes (budget 18 KB)", "2,480 - 2,800 bytes"),
        ("Private Key Size", "2,560 bytes", "64 bytes", "64 bytes"),
        ("Dynamic Memory Alloc", "0 bytes (Strict Zero-Malloc)", "0 bytes (Strict Zero-Malloc)", "0 bytes (Strict Zero-Malloc)"),
        ("Static Stack SRAM Budget", "< 3.5 KB (Lw) / ~ 8.5 KB (NTT)", "~ 2.2 KB - 2.5 KB", "~ 1.2 KB"),
        ("Verification Cycles (M4)", "~ 350,000 - 600,000 cycles", "~ 15M - 35M cycles", "~ 1.2M - 2.5M cycles"),
        ("Verification Latency @120MHz", "~ 3.0 ms - 5.0 ms", "~ 125.0 ms - 290.0 ms", "~ 10.0 ms - 20.0 ms"),
        ("eFuse Storage Requirement", "32B PKH (SHA-256 Digest)", "32B Direct Public Key", "56B Direct / 32B PKH"),
        ("Image Container Formats", "MCUboot TLV, U-Boot FIT, UEFI", "MCUboot TLV, U-Boot FIT, UEFI", "MCUboot TLV, U-Boot FIT, UEFI"),
        ("Target Emulated Hardware", "ARM Cortex-M4, RISC-V 64, Cortex-A57 SMP across all schemes", "", "")
    ]

    t1 = doc.add_table(rows=len(t1_data), cols=4)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t1)
    make_table_robust(t1)

    for i, row in enumerate(t1_data):
        r_cells = t1.rows[i].cells
        if i == len(t1_data) - 1:
            r_cells[1].merge(r_cells[3])
            r_cells[0].text = row[0]
            r_cells[1].text = row[1]
            set_cell_background(r_cells[0], "F8F9FA")
            set_cell_margins(r_cells[0], 50, 50, 80, 80)
            set_cell_margins(r_cells[1], 50, 50, 80, 80)
            r_cells[0].paragraphs[0].runs[0].font.size = Pt(12)
            r_cells[0].paragraphs[0].runs[0].font.bold = True
            r_cells[1].paragraphs[0].runs[0].font.size = Pt(12)
            continue

        for j in range(4):
            r_cells[j].text = row[j]
            set_cell_margins(r_cells[j], 50, 50, 80, 80)
            p_c = r_cells[j].paragraphs[0]
            if len(p_c.runs) > 0:
                p_c.runs[0].font.name = 'Arial'
                p_c.runs[0].font.size = Pt(12)
                if i == 0:
                    p_c.runs[0].font.bold = True
                    set_cell_background(r_cells[j], "E8F0FE")
                elif j == 0:
                    p_c.runs[0].font.bold = True
                    set_cell_background(r_cells[j], "F8F9FA")

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(8)
    r_t1_cap = p.add_run("Table 1: Technical Specifications & Cryptographic Parameters")
    r_t1_cap.font.name = 'Arial'
    r_t1_cap.font.size = Pt(12)
    r_t1_cap.font.bold = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # ==========================================
    # 7. SECTION 4: DESIGN CONSIDERATIONS (Page 11 - Fresh Page)
    # ==========================================
    p_h4 = doc.add_paragraph()
    p_h4.paragraph_format.keep_with_next = True
    r_br = p_h4.add_run()
    r_br.add_break(WD_BREAK.PAGE)
    r_h4 = p_h4.add_run("4. DESIGN CONSIDERATIONS")
    r_h4.font.name = 'Arial'
    r_h4.font.size = Pt(16)
    r_h4.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("Migrating embedded secure bootloaders from classical cryptosystems to post-quantum algorithms introduces formidable systems engineering challenges. The architecture was engineered under the following core design considerations:")

    # 4.1 Flows naturally
    add_heading_2("4.1 Zero Dynamic Memory Allocation (Zero-Malloc Policy)")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("Embedded early-stage bootloaders (ROM and Stage-1) execute prior to DRAM initialization and cannot safely instantiate dynamic heap allocators. Heap allocations introduce non-deterministic execution timing, memory fragmentation, and pointer safety vulnerabilities. The firmware mandates a 100% zero-malloc architecture. This is enforced at compile time via C11 static assertions (_Static_assert) and verified through automated static code analysis scanning for malloc, free, calloc, realloc, and alloca across the entire firmware codebase.")

    # 4.2 Flows naturally
    add_heading_2("4.2 Strict Static SRAM Budgeting (< 4 KB ROM Bounds)")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("Low-power microcontrollers (e.g., Cortex-M0+/M4) possess limited on-chip SRAM (often <= 64 KB total, with <= 4 KB allocated to early boot code). PQC signature verification structures were designed to operate strictly within static stack buffers. Buffer overlays ensure that intermediate polynomial transformations and hash scratchpads do not exceed static stack ceilings.")

    # 4.3 Flows naturally
    add_heading_2("4.3 Hardware Root-of-Trust Key Hash Binding & eFuse Storage")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("Physical on-chip One-Time Programmable (OTP) eFuses typically provide only 256 to 512 bits of secure non-volatile storage. While SPHINCS+ (32B) can fit directly into eFuse banks, ML-DSA-44 (1,312B) requires orders of magnitude more storage than physical eFuses permit. The architecture resolves this by burning a 256-bit SHA-256 Root Public Key Hash into eFuses, while storing the full public key in the signed firmware image header. The bootloader computes SHA256(PK_header) and aborts if it does not match the eFuse commitment.")

    # 4.4 Flows naturally
    add_heading_2("4.4 Tamper Robustness & Non-Negotiable Fault Rejection")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("The verification state machine is designed to be strictly fail-closed. Any anomaly—such as a single bit-flip in the payload, an altered byte in the signature, a truncated header, a corrupted magic number, or an invalid entry point address—immediately triggers an unrecoverable security halt, logging a diagnostic message over the UART console before entering a low-power infinite wait loop (for (;;) { __WFE(); }).")

    # 4.5 Flows naturally
    add_heading_2("4.5 Constant-Time Cryptographic Execution & Side-Channel Mitigation")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("Although signature verification in secure boot predominantly handles public data (public key, firmware binary, and signature), the comparison of digest commitments and challenge seeds must resist timing attacks. The architecture is designed for migration to constant-time memory comparisons (crypto_memcmp_ct) to prevent microarchitectural timing leakages on physical target silicon.")

    # ==========================================
    # 8. SECTION 5: BENCHMARKING & PROFILING (Page 13 - Fresh Page)
    # ==========================================
    doc.add_page_break()
    add_heading_1("5. EMPIRICAL BENCHMARKING, PROFILING & FUTURE PLAN")

    add_heading_2("5.1 MCUboot on ARM Cortex-M4 Trade-Off Benchmark & Stack Profiling")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("To establish practical viability for resource-constrained microcontrollers ahead of the final dissertation phase, an empirical trade-off benchmark and microarchitectural profiling analysis were conducted for MCUboot targeting the ARM Cortex-M4 architecture (MPS2-AN386 platform @ 120 MHz). Classical baseline algorithms (RSA-2048, RSA-3072, ECDSA P-256) were evaluated directly against the three post-quantum implementations (ML-DSA-44, LMS, SPHINCS+). Table 2 presents the empirical findings.")

    t2_bench_data = [
        ("Algorithm", "Scheme Class", "Stack RAM", "Latency @ 120MHz", "Cortex-M4 Cycles", "eFuse RoT", "Quantum Security"),
        ("RSA-2048", "Classical Factoring", "1,024 B", "8.0 ms", "~ 960,000", "32 B", "Broken (Shor)"),
        ("RSA-3072", "Classical Factoring", "1,536 B", "18.0 ms", "~ 2,160,000", "32 B", "Broken (Shor)"),
        ("ECDSA P-256", "Classical Discrete Log", "768 B", "4.0 ms", "~ 480,000", "32 B", "Broken (Shor)"),
        ("ML-DSA-44", "Post-Quantum Lattice", "2,456 B", "3.5 ms", "~ 420,000", "32 B (PKH)", "128-bit Quantum"),
        ("LMS / LMOTS", "Post-Quantum Stateful Hash", "1,280 B", "12.0 ms", "~ 1,440,000", "32 B / 56 B", "128-bit Quantum"),
        ("SPHINCS+", "Post-Quantum Stateless Hash", "2,304 B", "180.0 ms", "~ 21,600,000", "32 B (Direct)", "128-bit Quantum")
    ]

    t2_bench = doc.add_table(rows=len(t2_bench_data), cols=7)
    t2_bench.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t2_bench)
    make_table_robust(t2_bench)

    t2_col_widths = [Inches(1.1), Inches(1.2), Inches(0.8), Inches(0.9), Inches(0.9), Inches(0.6), Inches(0.9)]
    for i, row in enumerate(t2_bench_data):
        for j in range(7):
            cell = t2_bench.rows[i].cells[j]
            cell.width = t2_col_widths[j]
            cell.text = row[j]
            set_cell_margins(cell, 50, 50, 70, 70)
            p_c = cell.paragraphs[0]
            if len(p_c.runs) > 0:
                p_c.runs[0].font.name = 'Arial'
                p_c.runs[0].font.size = Pt(12)
                if i == 0:
                    p_c.runs[0].font.bold = True
                    set_cell_background(cell, "E8F0FE")
                elif j == 0:
                    p_c.runs[0].font.bold = True
                    set_cell_background(cell, "F8F9FA")
                elif j == 3:
                    p_c.runs[0].font.bold = True

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(8)
    r_t2_b_cap = p.add_run("Table 2: MCUboot ARM Cortex-M4 Trade-Off Benchmark (Classical vs PQC)")
    r_t2_b_cap.font.name = 'Arial'
    r_t2_b_cap.font.size = Pt(12)
    r_t2_b_cap.font.bold = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("GDB stack frame profiling was executed using RAM stack painting (pattern 0xAA) on the 32 KB static stack buffer defined in mps2-an386.ld. The measurements demonstrate:")

    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.space_after = Pt(3)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_pk = p.add_run("• Peak Stack Depth: ")
    r_pk.font.bold = True
    r_pk.font.size = Pt(12)
    p.add_run("ML-DSA-44 consumed a peak of 2,456 bytes during verification (including polynomial and SHA/SHAKE context buffers). LMS required 1,280 bytes, and SPHINCS+ required 2,304 bytes. All algorithms operated with >92% stack safety headroom under the 32 KB static limit.")

    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.space_after = Pt(3)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_la = p.add_run("• Execution Latency Advantage: ")
    r_la.font.bold = True
    r_la.font.size = Pt(12)
    p.add_run("ML-DSA-44 verified in 3.5 ms (~420,000 cycles at 120 MHz), outperforming classical RSA-2048 (8.0 ms) and RSA-3072 (18.0 ms), while matching ECDSA P-256 (4.0 ms). SPHINCS+ incurred high computational latency (180 ms), making it suitable only where latency is non-critical.")

    # Spacing to ensure Table 3 starts cleanly on Page 15 (avoiding mid-table page splits)
    for _ in range(24):
        p_pad = doc.add_paragraph()
        p_pad.paragraph_format.left_indent = Inches(0.25)
        p_pad.paragraph_format.space_after = Pt(3)

    # 5.2 Mid-Semester Progress Status (Page 15)
    add_heading_2("5.2 Mid-Semester Progress Status (Plan of Work)")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("Table 3 outlines the dissertation plan of work and current progress status. Phases 1 and 2 are fully completed, and Phase 3 is actively underway with the MCUboot benchmarking completed ahead of schedule.")

    t3_plan_data = [
        ("Sl No", "Phases", "Start Date – End Date", "Work to be done", "Status"),
        ("1", "Dissertation Outline", "25 Jul 2026 – 08 Aug 2026",
         "Literature review on NIST PQC standards (FIPS 204, FIPS 205, RFC 8554), establishing zero-malloc / static-RAM constraints, defining Root of Trust specifications, and preparing the formal Dissertation Outline.",
         "COMPLETED"),
        ("2", "Design and Development", "09 Aug 2026 – 31 Oct 2026",
         "Designing the standalone C verification engine, defining PQC container/header formats, integrating verification hooks into MCUboot, U-Boot FIT, and EDKII/UEFI SecurityPkg, and extending image signing tools.",
         "COMPLETED\n(Ahead of Schedule)"),
        ("3", "Testing & System Emulation", "01 Nov 2026 – 19 Nov 2026",
         "Setting up QEMU system emulation (ARM Cortex-M4, RISC-V 64, ARM Cortex-A57 SMP), executing automated Python E2E test suites (23/23 tests passing), GDB stack frame profiling, bit-flip fault injection, and MCUboot benchmark compilation.",
         "IN PROGRESS\n(Ahead of Schedule)"),
        ("4", "Dissertation Review", "20 Nov 2026 – 30 Nov 2026",
         "Submit complete draft dissertation to Supervisor & Additional Examiner for technical review, security evaluation, and feedback incorporation.",
         "PENDING"),
        ("5", "Final Submission", "01 Dec 2026 – 08 Dec 2026",
         "Final review, committee presentation defense, and formal submission of the dissertation manuscript and code repository.",
         "PENDING")
    ]

    t3_plan = doc.add_table(rows=len(t3_plan_data), cols=5)
    t3_plan.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t3_plan)
    make_table_robust(t3_plan)

    # Specific Custom Column Widths: Sl No compact (0.4"), Work to be done spacious (2.5")
    col_widths = [Inches(0.4), Inches(1.2), Inches(1.3), Inches(2.5), Inches(0.8)]
    for j in range(5):
        t3_plan.columns[j].width = col_widths[j]

    for i, row in enumerate(t3_plan_data):
        for j in range(5):
            cell = t3_plan.rows[i].cells[j]
            cell.width = col_widths[j]
            cell.text = row[j]
            set_cell_margins(cell, 50, 50, 70, 70)
            p_c = cell.paragraphs[0]
            if j == 0 or j == 4:
                p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif j == 3:
                p_c.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            else:
                p_c.alignment = WD_ALIGN_PARAGRAPH.LEFT

            if len(p_c.runs) > 0:
                p_c.runs[0].font.name = 'Arial'
                p_c.runs[0].font.size = Pt(12)
                if i == 0:
                    p_c.runs[0].font.bold = True
                    set_cell_background(cell, "E8F0FE")
                elif j == 4:
                    p_c.runs[0].font.bold = True
                    if "COMPLETED" in row[j]:
                        set_cell_background(cell, "E6F4EA")
                    elif "IN PROGRESS" in row[j]:
                        set_cell_background(cell, "FEF7E0")
                    else:
                        set_cell_background(cell, "F1F3F4")

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(8)
    r_t3_p_cap = p.add_run("Table 3: Dissertation Plan of Work & Mid-Semester Status")
    r_t3_p_cap.font.name = 'Arial'
    r_t3_p_cap.font.size = Pt(12)
    r_t3_p_cap.font.bold = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 5.3 Flows naturally (Page 16)
    add_heading_2("5.3 Remaining Tasks & Deliverables for Final Dissertation")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("With MCUboot profiling completed, the remaining dissertation activities focus on extending empirical evaluation to the other two targets:")

    remaining_tasks = [
        ("Multi-Target Profiling (U-Boot RISC-V 64 & UEFI Cortex-A57)",
         "Extend empirical benchmarking and hardware cycle counter measurements to Das U-Boot on RISC-V 64-bit and EDKII / UEFI SecurityPkg on ARM Cortex-A57 SMP, profiling multi-core DXE handoff latency.")
    ]
    for title, desc in remaining_tasks:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_after = Pt(3)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_b = p.add_run(f"• {title}: ")
        r_b.font.bold = True
        r_b.font.size = Pt(12)
        r_d = p.add_run(desc)
        r_d.font.size = Pt(12)

    # ==========================================
    # 9. SECTION 6: ABBREVIATIONS (Page 17 - Fresh Page)
    # ==========================================
    doc.add_page_break()
    add_heading_1("6. ABBREVIATIONS")

    abbr_data = [
        ("ASN.1", "Abstract Syntax Notation One"),
        ("CRQC", "Cryptographically Relevant Quantum Computer"),
        ("DTB", "Device Tree Blob"),
        ("DXE", "Driver Execution Environment (UEFI Phase)"),
        ("ECDSA", "Elliptic Curve Digital Signature Algorithm"),
        ("EDKII", "EFI Development Kit II (Canonical UEFI Implementation)"),
        ("eFuse", "Electronic Fuse (One-Time Programmable Storage)"),
        ("FIPS", "Federal Information Processing Standards"),
        ("FIT", "Flattened Image Tree (Das U-Boot Image Format)"),
        ("FORS", "Forest of Random Subsets (SPHINCS+ Sub-structure)"),
        ("ISA", "Instruction Set Architecture"),
        ("LMOTS", "Leighton-Micali One-Time Signature"),
        ("LMS", "Leighton-Micali Hash-Based Signature Scheme"),
        ("M-LWE", "Module Learning With Errors"),
        ("ML-DSA", "Module-Lattice Digital Signature Algorithm (FIPS 204)"),
        ("NIST", "National Institute of Standards and Technology"),
        ("NTT", "Number Theoretic Transform"),
        ("OID", "Object Identifier"),
        ("OTP", "One-Time Programmable"),
        ("PE/COFF", "Portable Executable / Common Object File Format"),
        ("PKCS", "Public-Key Cryptography Standards"),
        ("PKH", "Public Key Hash"),
        ("PQC", "Post-Quantum Cryptography"),
        ("QEMU", "Quick Emulator (Machine Emulator)"),
        ("RoT", "Root of Trust"),
        ("RSA", "Rivest-Shamir-Adleman Cryptosystem"),
        ("SHA", "Secure Hash Algorithm"),
        ("SHAKE", "Secure Hash Algorithm & Keccak Extensible-Output"),
        ("SLH-DSA", "Stateless Hash-Based Digital Signature (FIPS 205)"),
        ("SMP", "Symmetric Multiprocessing"),
        ("SPHINCS+", "Stateless Hash-Based Signature Scheme"),
        ("SRAM", "Static Random Access Memory"),
        ("TLV", "Type-Length-Value (Metadata Encoding Scheme)"),
        ("UEFI", "Unified Extensible Firmware Interface"),
        ("WOTS+", "Winternitz One-Time Signature Plus")
    ]

    half = (len(abbr_data) + 1) // 2
    left_items = abbr_data[:half]
    right_items = abbr_data[half:]

    t4 = doc.add_table(rows=half+1, cols=4)
    t4.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t4)
    make_table_robust(t4)

    headers = ["Abbr", "Expansion / Meaning", "Abbr", "Expansion / Meaning"]
    widths = [Inches(1.0), Inches(2.0), Inches(1.0), Inches(2.0)]
    for j in range(4):
        t4.columns[j].width = widths[j]

    for c_idx, h_text in enumerate(headers):
        cell = t4.rows[0].cells[c_idx]
        cell.text = h_text
        cell.width = widths[c_idx]
        set_cell_background(cell, "E8F0FE")
        set_cell_margins(cell, 35, 35, 50, 50)
        run = cell.paragraphs[0].runs[0]
        run.font.name = 'Arial'
        run.font.size = Pt(12)
        run.font.bold = True

    for r_idx in range(half):
        row = t4.rows[r_idx+1]

        # Left pair
        ab1, exp1 = left_items[r_idx]
        cell_a1, cell_e1 = row.cells[0], row.cells[1]
        cell_a1.width, cell_e1.width = widths[0], widths[1]
        cell_a1.text, cell_e1.text = ab1, exp1
        set_cell_margins(cell_a1, 25, 25, 45, 45)
        set_cell_margins(cell_e1, 25, 25, 45, 45)
        cell_a1.paragraphs[0].runs[0].font.name = 'Arial'
        cell_a1.paragraphs[0].runs[0].font.size = Pt(12)
        cell_a1.paragraphs[0].runs[0].font.bold = True
        cell_e1.paragraphs[0].runs[0].font.name = 'Arial'
        cell_e1.paragraphs[0].runs[0].font.size = Pt(12)

        # Right pair
        cell_a2, cell_e2 = row.cells[2], row.cells[3]
        cell_a2.width, cell_e2.width = widths[2], widths[3]
        set_cell_margins(cell_a2, 25, 25, 45, 45)
        set_cell_margins(cell_e2, 25, 25, 45, 45)
        if r_idx < len(right_items):
            ab2, exp2 = right_items[r_idx]
            cell_a2.text, cell_e2.text = ab2, exp2
            cell_a2.paragraphs[0].runs[0].font.name = 'Arial'
            cell_a2.paragraphs[0].runs[0].font.size = Pt(12)
            cell_a2.paragraphs[0].runs[0].font.bold = True
            cell_e2.paragraphs[0].runs[0].font.name = 'Arial'
            cell_e2.paragraphs[0].runs[0].font.size = Pt(12)
        else:
            cell_a2.text = ""
            cell_e2.text = ""

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(8)
    r_t4_cap = p.add_run("Table 4: Table of Abbreviations & Acronyms")
    r_t4_cap.font.name = 'Arial'
    r_t4_cap.font.size = Pt(12)
    r_t4_cap.font.bold = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # ==========================================
    # 10. SECTION 7: REFERENCES (Page 19 - Fresh Page)
    # ==========================================
    doc.add_page_break()
    add_heading_1("7. REFERENCES & LITERATURE REVIEW")

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("The development of quantum-resistant secure boot systems relies on state-of-the-art literature across post-quantum cryptography standards, embedded systems security, and open-source bootloader specifications. Key references guiding this research include:")

    refs = [
        "National Institute of Standards and Technology. (2024). Module-Lattice-Based Digital Signature Standard. Federal Information Processing Standards Publication (FIPS) 204. U.S. Department of Commerce. https://doi.org/10.6028/NIST.FIPS.204",
        "National Institute of Standards and Technology. (2024). Stateless Hash-Based Digital Signature Standard. Federal Information Processing Standards Publication (FIPS) 205. U.S. Department of Commerce. https://doi.org/10.6028/NIST.FIPS.205",
        "McGrew, D., Curcio, M., & Fluhrer, S. (2019). Leighton-Micali Hash-Based Signatures. Internet Engineering Task Force (IETF) Request for Comments (RFC) 8554. https://doi.org/10.17487/RFC8554",
        "Housley, R. (2020). Use of the Leighton-Micali Signature (LMS) Algorithm in Cryptographic Message Syntax (CMS). Internet Engineering Task Force (IETF) Request for Comments (RFC) 8708. https://doi.org/10.17487/RFC8708",
        "Shor, P. W. (1994). Algorithms for quantum computation: Discrete logarithms and factoring. Proceedings of the 35th Annual Symposium on Foundations of Computer Science (FOCS), 124–134. IEEE. https://doi.org/10.1109/SFCS.1994.365700",
        "Bernstein, D. J., Hülsing, A., Kölbl, S., Niederhagen, R., Rijneveld, A., & Schwabe, P. (2019). SPHINCS+: Stateless Hash-Based Signatures. Submission to the NIST Post-Quantum Cryptography Standardization Process. https://sphincs.org/data/sphincs+-specification-ed2.1.pdf",
        "Unified EFI Forum. (2024). Unified Extensible Firmware Interface (UEFI) Specification (Version 2.10, Section 32: Secure Boot). Available at: https://uefi.org/specifications",
        "MCUboot Contributors. (2024). MCUboot: An Open Source Secure Bootloader for 32-bit Microcontrollers. Available at: https://github.com/mcu-tools/mcuboot",
        "DENX Software Engineering. (2024). The Universal Boot Loader (Das U-Boot): Flattened Image Tree (FIT) Verification Architecture. Available at: https://source.denx.de/u-boot/u-boot",
        "Cooper, D., et al. (2020). Recommendation for Stateful Hash-Based Signature Schemes. NIST Special Publication 800-208. National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-208"
    ]

    for i, ref in enumerate(refs, 1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.35)
        p.paragraph_format.space_after = Pt(5)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_num = p.add_run(f"[{i}] ")
        r_num.font.bold = True
        r_num.font.size = Pt(12)
        r_txt = p.add_run(ref)
        r_txt.font.size = Pt(12)

    doc.save(output_path)
    print(f"Report saved successfully to {output_path}")

if __name__ == "__main__":
    target_path = sys.argv[1] if len(sys.argv) > 1 else "submission-docs/midsem-report/Midsem_Report_ESZG628T_2024HT01586.docx"
    build_midsem_report(target_path)
