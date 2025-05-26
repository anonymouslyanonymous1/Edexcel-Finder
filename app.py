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

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        pass
def clear():
    shutil.rmtree(f"static/images/{user_id}")


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
        if module == "WDM" and choice=="new":
            unit = "WDM11"
        elif module == "WDM" and choice=="old":
            unit = "WDM01"
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
    ensure_directory(f"static/images/{user_id}")
    if folder:
        for one in folder:
            ix = indexx.open_dir(f"static/Index/{one[1]}/{unit}")
            qp = QueryParser("content", schema=ix.schema)
            query = qp.parse(target) 
            with ix.searcher() as searcher:
                results = searcher.search(query, limit=None)
                for result in results:
                    if result["year"] != "Sample Assessment":
                        response = requests.get(result["qp_link"])
                        if response.status_code != 200:
                            continue
                        else:
                            pdf = open(f"static/QP.pdf", "wb")
                            pdf.write(response.content)
                            page = result["page"]
                            try:
                                pdf = fitz.open(f"static/QP.pdf")
                                # print(f"{result['year']} {result['qp_link']}#page={page}")
                                Page = pdf.load_page(page)
                                pix = Page.get_pixmap(dpi=160)
                                ensure_directory(f'static/images/{user_id}/{one[0]}')
                                pix.save(f'static/images/{user_id}/{one[0]}/{result["year"]} pg{page}.png')
                                send.append([result["year"], page+1, f'static/images/{user_id}/{one[0]}/{result["year"]} pg{page}.png', result["qp_link"], result["ms_link"] ])
                            except:
                                webhook_url = ""

                                data = {
                                    "content": f'# Data Omitted \n > {result["year"]} {subject} {module} \n - Question Paper: {result["qp_link"]}#page={result["page"]} \n - Search Term: {target}'
                                }

                                response = requests.post(webhook_url, json=data)

                                if response.status_code == 204:
                                    print("Message sent successfully!")
                                else:
                                    print(f"Failed to send message: {response.status_code}")
                                send.append([result["year"], page+1, f'static/404.png', result["qp_link"], result["ms_link"] ])
                    else:
                        page = result["page"]
                        pdf = fitz.open(f"{result['qp_link']}")
                        Page = pdf.load_page(page)
                        pix = Page.get_pixmap(dpi=160)
                        ensure_directory(f'static/images/{user_id}/{one[0]}')
                        pix.save(f'static/images/{user_id}/{one[0]}/{result["year"]} pg{page}.png')
                        send.append([result["year"], page+1, f'static/images/{user_id}/{one[0]}/{result["year"]} pg{page}.png', result["qp_link"], result["ms_link"] ])
            total = total + len(results)
            if one[1] == old:
                old_count = len(results)
            else:
                new_count = len(results)
        hits = f"{total} [Old: {old_count}, New: {new_count}]"
        run_time = datetime.now() + timedelta(seconds=400)
        scheduler.add_job(clear, 'date', run_date=run_time)
        return render_template("results.html", results = send, hits = hits)
    else:
        ix = indexx.open_dir(f"static/Index/{todo}/{unit}")
        qp = QueryParser("content", schema=ix.schema)
        query = qp.parse(target) 
        with ix.searcher() as searcher:
            results = searcher.search(query, limit=None)
            for result in results:
                if result["year"] != "Sample Assessment":
                    response = requests.get(result["qp_link"])
                    if response.status_code != 200:
                        continue
                    else:
                        pdf = open(f"static/QP.pdf", "wb")
                        pdf.write(response.content)
                        page = result["page"]
                        try:
                            pdf = fitz.open(f"static/QP.pdf")
                            # print(f"{result['year']} {result['qp_link']}#page={page}")
                            Page = pdf.load_page(page)
                            pix = Page.get_pixmap(dpi=160)
                            ensure_directory(f'static/images/{user_id}/{todo}')
                            pix.save(f'static/images/{user_id}/{todo}/{result["year"]} pg{page}.png')
                            send.append([result["year"], page+1, f'static/images/{user_id}/{todo}/{result["year"]} pg{page}.png', result["qp_link"], result["ms_link"] ])
                        except:
                            webhook_url = ""

                            data = {
                                "content": f'# Data Omitted \n > {result["year"]} {subject} {module} \n - Question Paper: {result["qp_link"]}#page={result["page"]+1} \n - Search Term: {target}'
                            }

                            response = requests.post(webhook_url, json=data)

                            if response.status_code == 204:
                                print("Message sent successfully!")
                            else:
                                print(f"Failed to send message: {response.status_code}")
                            send.append([result["year"], page+1, f'static/404.png', result["qp_link"], result["ms_link"] ])
                else:
                    page = result["page"]
                    pdf = fitz.open(f"{result['qp_link']}")
                    Page = pdf.load_page(page)
                    pix = Page.get_pixmap(dpi=160)
                    ensure_directory(f'static/images/{user_id}/{todo}')
                    pix.save(f'static/images/{user_id}/{todo}/{result["year"]} pg{page}.png')
                    send.append([result["year"], page+1, f'static/images/{user_id}/{todo}/{result["year"]} pg{page}.png', result["qp_link"], result["ms_link"] ])
        total = len(results)
        hits = total
        run_time = datetime.now() + timedelta(seconds=400)
        scheduler.add_job(clear, 'date', run_date=run_time)
        return render_template("results.html", results = send, hits = hits)
@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", error=str(traceback.format_exc())), 500
if __name__ == '__main__':  
   app.run()
