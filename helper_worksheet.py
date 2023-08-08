import openpyxl

def prepare_worksheet_erros():
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet['A1'] = 'Page URL'
    worksheet['B1'] = 'Error Message'

    return (workbook, worksheet)

def prepare_worksheet_pagedata(url, page_title, meta_description, meta_og_title, meta_og_description):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active

    worksheet['A1'] = 'URL:'
    worksheet['B1'] = url
    worksheet['A2'] = 'Title:'
    worksheet['B2'] = page_title
    worksheet['A3'] = 'Meta Description:'
    worksheet['B3'] = meta_description
    worksheet['A4'] = 'Meta OG Title:'
    worksheet['B4'] = meta_og_title
    worksheet['A5'] = 'Meta OG Description:'
    worksheet['B5'] = meta_og_description

    worksheet['A6'] = 'Tag'
    worksheet['B6'] = 'Content'
    worksheet['C6'] = 'Filename'
    worksheet['D6'] = 'Alt Text'

    return (workbook, worksheet)

def write_worksheet_pagedata(worksheet, tag_name, content, file_name, alt_text):
    next_row = len(worksheet['A']) + 1

    worksheet.cell(row=next_row, column=1, value=tag_name)
    worksheet.cell(row=next_row, column=2, value=content)
    worksheet.cell(row=next_row, column=3, value=file_name)
    worksheet.cell(row=next_row, column=4, value=alt_text)
