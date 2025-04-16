from flask import Flask, flash, redirect, render_template, request, session
from pypdf import PdfReader as read
import re
import os
import fitz
from whoosh import index as indexx
from whoosh.qparser import MultifieldParser
import traceback
import string

app = Flask(__name__)
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")
@app.route("/results", methods=["GET", "POST"])
def results():
    # try:
    for file in os.listdir("static/images"):
        os.remove(f"static/images/{file}")
    subject = request.args.get("subject")
    unit = re.sub("Unit ", "", request.args.get("unit"))
    if subject != "Physics" and subject != "Chemistry":
        subject = "Maths"
        module = request.args.get("subject")
    else:
        module = "None"
    search = request.args.get("search").lower()
    resultss = []
    ix = indexx.open_dir("static/Index")
    with ix.searcher() as searcher:
        parser = MultifieldParser(["subject", "unit", "module", "content"], schema=ix.schema)
        if subject == "Maths":
            if search[0] == '"' and search[len(search)-1]=='"' and len(search.split()) != 1:
                Search = search.split()
                searchh = ""
                for word in Search:
                    word = re.sub(f"[{re.escape(string.punctuation)}]", "", word)
                    searchh = searchh + f"content:{word} OR "
                print(searchh)
                query = parser.parse(f'subject:"{subject}" AND unit:"Unit {unit}" AND module:"{module}" AND ({searchh})') # Turning into a query object
                results = searcher.search(query, limit=40)
                print(query)
                print(f"{len(results)} found")
                hits = len(results)
                for result in results:
                    print(result["year"], result.score)
                    pdf_path = f'static/Papers/{result["subject"]}/{result["unit"]}/{result["year"]}.txt'
                    QP = open(pdf_path, "r", encoding="utf-8")
                    content = QP.read()    
                    content = re.sub(" ", "", content)
                    search = re.sub(" ", "", search)
                    search = re.sub('"',"", search)
                    if content.lower().find(search) != -1:
                        for index in range(content.lower().find(search), len(content)):
                            if content[index: index + 15] == "-----EndofPage:":
                                page = content[index + 15]
                                if content[index + 16] != "-":
                                    page = page + content[index + 16]
                                    break
                                else:
                                    break
                        page = int(page) + 1
                        doc = fitz.open(re.sub(".txt",".pdf",pdf_path))
                        Page = doc.load_page(page-1)
                        pix = Page.get_pixmap(dpi=160)
                        pix.save(f'static/images/{result["year"]} pg{page}.png')
                        resultss.append([result["year"], page, f'static/images/{result["year"]} pg{page}.png', re.sub(".txt",".pdf",pdf_path), re.sub(".txt", " MS.pdf", pdf_path)])
                    else:
                        hits = hits-1
                        continue
            else:
                query = parser.parse(f'subject:"{subject}" AND unit:"{module}" AND module:"Unit {unit}" AND content:"{search}"') # Turning into a query object
                results = searcher.search(query, limit=40)
                hits = len(results)
                print(f"len(results) found")
                for result in results:
                    pdf_path = f'static/Papers/{result["subject"]}/{result["unit"]}/{result["module"]}/{result["year"]}.txt'
                    QP = open(pdf_path, "r", encoding="utf-8")
                    content = QP.read()    
                    content = re.sub(" ", "", content)
                    search = re.sub(" ", "", search)
                    if content.lower().find(search) != -1:
                        for index in range(content.lower().find(search), len(content)):
                            if content[index: index + 15] == "-----EndofPage:":
                                page = content[index + 15]
                                if content[index + 16] != "-":
                                    page = page + content[index + 16]
                                    break
                                else:
                                    break                   
                    page = int(page) + 1
                    doc = fitz.open(re.sub(".txt",".pdf",pdf_path))
                    Page = doc.load_page(page-1)
                    pix = Page.get_pixmap(dpi=160)
                    pix.save(f'static/images/{result["year"]} pg{page}.png')
                    resultss.append([result["year"], page, f'static/images/{result["year"]} pg{page}.png', re.sub(".txt",".pdf",pdf_path), re.sub(".txt", " MS.pdf", pdf_path)])
        else:
            if search[0] == '"' and search[len(search)-1]=='"' and len(search.split()) != 1:
                Search = search.split()
                searchh = ""
                for word in Search:
                    word = re.sub(f"[{re.escape(string.punctuation)}]", "", word)
                    searchh = searchh + f"content:{word} OR "
                print(searchh)
                query = parser.parse(f'subject:"{subject}" AND unit:"Unit {unit}" AND module:"{module}" AND ({searchh})') # Turning into a query object
                results = searcher.search(query, limit=40)
                print(query)
                print(f"{len(results)} found")
                hits = len(results)
                for result in results:
                    print(result["year"], result.score)
                    pdf_path = f'static/Papers/{result["subject"]}/{result["unit"]}/{result["year"]}.txt'
                    QP = open(pdf_path, "r", encoding="utf-8")
                    content = QP.read()    
                    content = re.sub(" ", "", content)
                    search = re.sub(" ", "", search)
                    search = re.sub('"',"", search)
                    if content.lower().find(search) != -1:
                        for index in range(content.lower().find(search), len(content)):
                            if content[index: index + 15] == "-----EndofPage:":
                                page = content[index + 15]
                                if content[index + 16] != "-":
                                    page = page + content[index + 16]
                                    break
                                else:
                                    break
                        if result["year"] == "Sample Assessment":
                            page = int(page) + 2
                        else:
                            page = int(page) + 1
                        doc = fitz.open(re.sub(".txt",".pdf",pdf_path))
                        Page = doc.load_page(page-1)
                        pix = Page.get_pixmap(dpi=160)
                        pix.save(f'static/images/{result["year"]} pg{page}.png')
                        resultss.append([result["year"], page, f'static/images/{result["year"]} pg{page}.png', re.sub(".txt",".pdf",pdf_path), re.sub(".txt", " MS.pdf", pdf_path)])        
                    else:
                        hits = hits-1
                        continue
            else:
                query = parser.parse(f'subject:"{subject}" AND unit:"Unit {unit}" AND module:"{module}" AND content:"{search}"') # Turning into a query object
                results = searcher.search(query, limit=40)
                hits = len(results)
                print(f"{len(results)} found")
                for result in results:
                    print(result["year"], result.score)
                    pdf_path = f'static/Papers/{result["subject"]}/{result["unit"]}/{result["year"]}.txt'
                    QP = open(pdf_path, "r", encoding="utf-8")
                    content = QP.read()    
                    content = re.sub(" ", "", content)
                    search = re.sub(" ", "", search)
                    if content.lower().find(search) != -1:
                        for index in range(content.lower().find(search), len(content)):
                            if content[index: index + 15] == "-----EndofPage:":
                                page = content[index + 15]
                                if content[index + 16] != "-":
                                    page = page + content[index + 16]
                                    break
                                else:
                                    break
                        if result["year"] == "Sample Assessment":
                            page = int(page) + 2
                        else:
                            page = int(page) + 1
                    doc = fitz.open(re.sub(".txt",".pdf",pdf_path))
                    Page = doc.load_page(page-1)
                    pix = Page.get_pixmap(dpi=160)
                    pix.save(f'static/images/{result["year"]} pg{page}.png')
                    resultss.append([result["year"], page, f'static/images/{result["year"]} pg{page}.png', re.sub(".txt",".pdf",pdf_path), re.sub(".txt", " MS.pdf", pdf_path)])
        return render_template("results.html", results = resultss, hits = hits)
@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", error=str(traceback.format_exc())), 500
if __name__ == '__main__':  
   app.run()
