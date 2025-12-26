from flask import Flask, render_template, request, session
import re
import os
import fitz
from whoosh import index as indexx
from whoosh.qparser import QueryParser
import traceback
import shutil
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import time
import uuid
import json

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        pass
def clear(user_id):
    path = f"./static/images/{user_id}"
    if os.path.exists(path):
        shutil.rmtree(path)

app = Flask(__name__)
app.secret_key = 'edexcel_finder_anonymouslyanonymous'
scheduler = BackgroundScheduler()
scheduler.start()

@app.route("/", methods=["GET", "POST"])
def index():
    global user_id
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    user_id = session['user_id']
    # print(f"user ID: {user_id}")
    return render_template("index.html")
@app.route("/results", methods=["GET", "POST"])
def results():
    global user_id
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    user_id = session['user_id']
    send = []
    subject = request.args.get("subject")
    unit = request.args.get("unit")
    choice = request.args.get("choice")
    if subject != "Physics" and subject != "Chemistry"  and subject != "Biology":
        subject = "Mathematics"
        unit = re.sub("Unit ", "", request.args.get("unit"))
        module = request.args.get("subject")
        if (module == "WDM" or module == "WMA") and choice=="new":
            match module:
                case "WDM":
                    unit = "WDM11"
                case "WMA":
                    unit = f"WMA1{unit}"
        elif (module == "WDM" or module == "WMA") and choice=="old":
            match module:
                case "WDM":
                    unit = "WDM11"
                case "WMA":
                    if unit == "4":
                        unit = "2"
                    else:
                        unit = "1"
                    unit = f"WMA0{unit}"
        else:
            unit = f"{module}{unit}"
    else:
        module = "None"
    target = request.args.get("search").lower()
    folder = []
    if choice == "both":
            old = f"Old {subject}"
            folder.append(["Old Specification", old])
            new = f"{subject} (2018)"
            folder.append(["New Specification", new])
    elif choice == "new":
        todo = f"{subject} (2018)"
    else:
        todo = f"Old {subject}"
    total = 0
    old_count = 0
    new_count = 0
    ensure_directory(f"./static/images/{user_id}")
    if folder:
        for one in folder:
            ix = indexx.open_dir(f"./static/Index/{one[1]}/{unit}")
            qp = QueryParser("content", schema=ix.schema)
            query = qp.parse(target) 
            with ix.searcher() as searcher:
                results = searcher.search(query, limit=None)
                for result in results:
                    if result["year"] != "Sample Assessment":
                        response = requests.get(result["qp_link"])
                        if response.status_code != 200 or response.url == 'https://qualifications.pearson.com/en/campaigns/404.html':
                            continue
                        else:
                            with open(f"./static/QP{user_id}.pdf", "wb") as f:
                                f.write(response.content)
                            page = result["page"]
                            pdf = fitz.open(f"./static/QP{user_id}.pdf")
                            # print(f"{result['year']} {result['qp_link']}#page={page}")
                            Page = pdf.load_page(page)
                            pix = Page.get_pixmap(dpi=160)
                            ensure_directory(f'./static/images/{user_id}/{one[0]}')
                            pix.save(f'./static/images/{user_id}/{one[0]}/{result["unit_code"]} {result["year"]} pg{page}.png')
                            pdf.close()
                            os.remove(f"./static/QP{user_id}.pdf")
                            send.append([result["year"], page+1, f'./static/images/{user_id}/{one[0]}/{result["unit_code"]} {result["year"]} pg{page}.png', result["qp_link"], result["ms_link"], result["unit_code"] ])
                            # send.append([result["year"], page+1, f'./static/404.png', result["qp_link"], result["ms_link"] ])
                    else:
                        page = result["page"]
                        pdf = fitz.open(f"{result['qp_link']}")
                        Page = pdf.load_page(page)
                        pix = Page.get_pixmap(dpi=160)
                        ensure_directory(f'./static/images/{user_id}/{one[0]}')
                        pix.save(f'./static/images/{user_id}/{one[0]}/{result["unit_code"]} {result["year"]} pg{page}.png')
                        pdf.close()
                        send.append([result["year"], page+1, f'./static/images/{user_id}/{one[0]}/{result["unit_code"]} {result["year"]} pg{page}.png', result["qp_link"], result["ms_link"], result["unit_code"] ])
            total = total + len(results)
            if one[1] == old:
                old_count = len(results)
            else:
                new_count = len(results)
        hits = f"{total} [Old: {old_count}, New: {new_count}]"
        run_time = datetime.now() + timedelta(seconds=400)
        scheduler.add_job(clear, 'date', run_date=run_time, args=[user_id], misfire_grace_time=60)
        send.sort(key=lambda x: datetime.strptime("June 2019", "%B %Y") if x[0] == "Sample Assessment" else datetime.strptime(re.sub(r"^Unused ", "", x[0]), "%B %Y") if x[0].startswith("Unused ") else datetime.strptime(x[0], "%B %Y"))
        return render_template("baseResults.html", results = send, hits = hits)
    else:
        ix = indexx.open_dir(f"./static/Index/{todo}/{unit}")
        qp = QueryParser("content", schema=ix.schema)
        query = qp.parse(target) 
        with ix.searcher() as searcher:
            results = searcher.search(query, limit=None)
            for result in results:
                if result["year"] != "Sample Assessment":
                    response = requests.get(result["qp_link"])
                    if response.status_code != 200 or response.url == 'https://qualifications.pearson.com/en/campaigns/404.html' or response.url == 'https://qualifications.pearson.com/en/campaigns/404.html':
                        continue
                    else:
                        with open(f"./static/QP{user_id}.pdf", "wb") as f:
                            f.write(response.content)
                        page = result["page"]
                        pdf = fitz.open(f"./static/QP{user_id}.pdf")
                        # print(f"{result['year']} {result['qp_link']}#page={page}")
                        Page = pdf.load_page(page)
                        pix = Page.get_pixmap(dpi=160)
                        ensure_directory(f'./static/images/{user_id}/{todo}')
                        pix.save(f'./static/images/{user_id}/{todo}/{result["unit_code"]} {result["year"]} pg{page}.png')
                        pdf.close()
                        os.remove(f"./static/QP{user_id}.pdf")
                        send.append([result["year"], page+1, f'./static/images/{user_id}/{todo}/{result["unit_code"]} {result["year"]} pg{page}.png', result["qp_link"], result["ms_link"], result["unit_code"] ])
                        # send.append([result["year"], page+1, f'./static/404.png', result["qp_link"], result["ms_link"], result["unit_code"] ])
                else:
                    page = result["page"]
                    pdf = fitz.open(f"{result['qp_link']}")
                    Page = pdf.load_page(page)
                    pix = Page.get_pixmap(dpi=160)
                    ensure_directory(f'./static/images/{user_id}/{todo}')
                    pix.save(f'./static/images/{user_id}/{todo}/{result["unit_code"]} {result["year"]} pg{page}.png')
                    pdf.close()
                    send.append([result["year"], page+1, f'./static/images/{user_id}/{todo}/{result["unit_code"]} {result["year"]} pg{page}.png', result["qp_link"], result["ms_link"], result["unit_code"] ])
        total = len(results)
        hits = total
        run_time = datetime.now() + timedelta(seconds=400)
        scheduler.add_job(clear, 'date', run_date=run_time, args=[user_id], misfire_grace_time=60)
        send.sort(key=lambda x: datetime.strptime("June 2019", "%B %Y") if x[0] == "Sample Assessment" else datetime.strptime(re.sub(r"^Unused ", "", x[0]), "%B %Y") if x[0].startswith("Unused ") else datetime.strptime(x[0], "%B %Y"))
        return render_template("baseResults.html", results = send, hits = hits)
@app.route("/SixMark", methods=["GET", "POST"])
def SixMark():
    global user_id
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    user_id = session['user_id']
    # print(f"user ID: {user_id}")
    return render_template("SixMark.html")
@app.route("/SixMarkresults", methods=["GET", "POST"])
def SixMarkresults():
    send = []
    subject = request.args.get("subject")
    unit = request.args.get("unit")
    choice = request.args.get("choice")
    folder = []
    if choice == "both":
            old = f"Old {subject}"
            folder.append(["Old Specification", old])
            new = f"{subject} (2018)"
            folder.append(["New Specification", new])
    elif choice == "new":
        todo = f"{subject} (2018)"
    else:
        todo = f"Old {subject}"
    total = 0
    old_count = 0
    new_count = 0
    if folder:
        for one in folder:
            for file in os.listdir(f"./static/SixMark/Data/{one[1]}/{unit}"):
                data = open(f"./static/SixMark/Data/{one[1]}/{unit}/{file}", "r", encoding="utf-8")
                data = json.load(data)
                for row in data:
                    send.append([row["Title"], row["Page"]+1, row["Image_Link"], row["QP_Link"], row["MS_Link"], row["Unit_Code"]])
                    total = total + 1
                    if one[1] == old:
                        old_count = old_count + 1
                    else:
                        new_count = new_count + 1
        hits = f"{total} [Old: {old_count}, New: {new_count}]"                        
        send.sort(key=lambda x: datetime.strptime("June 2019", "%B %Y") if x[0] == "Sample Assessment" else datetime.strptime(re.sub(r"^Unused ", "", x[0]), "%B %Y") if x[0].startswith("Unused ") else datetime.strptime(x[0], "%B %Y"))
    else:
        for file in os.listdir(f"./static/SixMark/Data/{todo}/{unit}"):
            data = open(f"./static/SixMark/Data/{todo}/{unit}/{file}", "r", encoding="utf-8")
            data = json.load(data)
            for row in data:
                send.append([row["Title"], row["Page"]+1, row["Image_Link"], row["QP_Link"], row["MS_Link"], row["Unit_Code"]])
                total = total + 1
        hits = total
        send.sort(key=lambda x: datetime.strptime("June 2019", "%B %Y") if x[0] == "Sample Assessment" else datetime.strptime(re.sub(r"^Unused ", "", x[0]), "%B %Y") if x[0].startswith("Unused ") else datetime.strptime(x[0], "%B %Y"))
    return render_template("baseResults.html", results = send, hits = hits)
@app.route("/SixMarkSearch", methods=["GET", "POST"])
def SixMarkSearch():
    global user_id
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    user_id = session['user_id']
    # print(f"user ID: {user_id}")
    return render_template("SixMarkSearch.html")
@app.route("/SixMarkSearchresults", methods=["GET", "POST"])
def SixMarkSearchresults():
    send = []
    subject = request.args.get("subject")
    unit = request.args.get("unit")
    choice = request.args.get("choice")
    target = request.args.get("search").lower()
    folder = []
    if choice == "both":
            old = f"Old {subject}"
            folder.append(["Old Specification", old])
            new = f"{subject} (2018)"
            folder.append(["New Specification", new])
    elif choice == "new":
        todo = f"{subject} (2018)"
    else:
        todo = f"Old {subject}"
    total = 0
    old_count = 0
    new_count = 0
    if folder:
        for one in folder:
            ix = indexx.open_dir(f"./static/SixMark/Index/{one[1]}/{unit}")
            qp = QueryParser("content", schema=ix.schema)
            query = qp.parse(target) 
            with ix.searcher() as searcher:
                results = searcher.search(query, limit=None)
                for result in results:
                    send.append([result["year"], result["page"]+1, result["image_link"], result["qp_link"], result["ms_link"], result["unit_code"]])
            total = total + len(results)
            if one[1] == old:
                old_count = len(results)
            else:
                new_count = len(results)
        hits = f"{total} [Old: {old_count}, New: {new_count}]"
        send.sort(key=lambda x: datetime.strptime("June 2019", "%B %Y") if x[0] == "Sample Assessment" else datetime.strptime(re.sub(r"^Unused ", "", x[0]), "%B %Y") if x[0].startswith("Unused ") else datetime.strptime(x[0], "%B %Y"))
        return render_template("baseResults.html", results = send, hits = hits)
    else:
        ix = indexx.open_dir(f"./static/SixMark/Index/{todo}/{unit}")
        qp = QueryParser("content", schema=ix.schema)
        query = qp.parse(target) 
        with ix.searcher() as searcher:
            results = searcher.search(query, limit=None)
            print(results)
            for result in results:
                send.append([result["year"], result["page"]+1, result["image_link"], result["qp_link"], result["ms_link"], result["unit_code"]])
        total = len(results)
        hits = total
        send.sort(key=lambda x: datetime.strptime("June 2019", "%B %Y") if x[0] == "Sample Assessment" else datetime.strptime(re.sub(r"^Unused ", "", x[0]), "%B %Y") if x[0].startswith("Unused ") else datetime.strptime(x[0], "%B %Y"))
        return render_template("baseResults.html", results = send, hits = hits)
@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", error=str(traceback.format_exc())), 500
if __name__ == '__main__':  
   app.run()
