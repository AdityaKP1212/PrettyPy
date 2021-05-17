from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_pymongo import PyMongo
from datetime import datetime, timedelta
from uuid import UUID
from werkzeug.wrappers import Response
from io import StringIO
import csv

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/NewRelicData"
mongo = PyMongo(app)

def getBasicStartEndDates(argStart, argEnd):
    today = datetime.utcnow()
    startDate = datetime(today.year, 1, 1)
    endDate = datetime(today.year, today.month + 1, 1)

    if argStart != None and argEnd != None:
        startDate = datetime.strptime(argStart, "%Y-%m-%d")
        endDate = datetime.strptime(argEnd, "%Y-%m-%d") + timedelta(days=1)
    
    return (startDate, endDate)

def getMinMaxDates():
    today = datetime.utcnow()
    minDate = (today - timedelta(days = 180)).strftime("%Y-%m-%d")
    return (minDate, today.strftime("%Y-%m-%d"))

def mapMerchantMongoCursorToDict(merchantmongoData):
    merchantData = {}
    for doc in merchantmongoData:
        if "merchantId" in doc:
            if "siteUrl" in doc:
                merchantData[str(doc["merchantId"])] = [doc["siteUrl"], False]
            if "isActive" in doc:
                merchantData[str(doc["merchantId"])][1] = doc["isActive"]
    return merchantData

@app.route("/", methods = ['GET'])
def index():
    monthStart, monthEnd = getBasicStartEndDates(request.args.get("start"), request.args.get("end"))
    mongoData = mongo.db.TransactionData.find({"createdDate":{"$gte":monthStart, "$lt": monthEnd}})
    merchantmongoData = mongo.db.MerchantData.find()

    templateView = {}
    templateView["labels"] = []
    templateView["tranCx"] = []
    templateView["pageCx"] = []
    merchantData = mapMerchantMongoCursorToDict(merchantmongoData)

    monthlyData = {}
    for doc in mongoData:
        if "transactions" in doc:
            pagesum = 0
            transum = 0
            for merchantId in doc["transactions"]:
                transum += doc["transactions"][merchantId][0]
                pagesum += doc["transactions"][merchantId][1]
                if merchantId not in monthlyData:
                    monthlyData[merchantId] = doc["transactions"][merchantId]
                    if merchantId in merchantData:
                        monthlyData[merchantId].append(merchantData[merchantId][0])
                        monthlyData[merchantId].append(merchantData[merchantId][1])
                else:
                    monthlyData[merchantId][0] += doc["transactions"][merchantId][0]
                    monthlyData[merchantId][1] += doc["transactions"][merchantId][1]
            if "createdDate" in doc:
                #print(doc["createdDate"])
                templateView["labels"].append(doc["createdDate"].strftime("%d %b %y"))
                templateView["tranCx"].append(transum)
                templateView["pageCx"].append(pagesum)
                
    templateView["data"] = monthlyData
    templateView["startDate"] = monthStart.strftime("%Y-%m-%d")
    templateView["endDate"] = (monthEnd - timedelta(days=1)).strftime("%Y-%m-%d")
    templateView["minDate"], templateView["maxDate"] = getMinMaxDates()
    
    return render_template("index.html", templateView = templateView)

@app.route("/getinsights/<mid>", methods = ['GET'])
def getBasicsInsights(mid):
    returnDict = {}
    template = None
    try:
        merchantmongoData = mongo.db.MerchantData.find_one({"merchantId": UUID(mid)})
        starttime, endtime = getBasicStartEndDates(request.args.get("start"), request.args.get("end"))
        mongoData = mongo.db.TransactionData.find({"createdDate":{"$gte":starttime, "$lt": endtime}})

        if merchantmongoData != None:
            returnDict["merchantId"] = str(merchantmongoData["merchantId"])
            returnDict["siteUrl"] = merchantmongoData["siteUrl"].replace("https://www.", "").capitalize()
            returnDict["isActive"] = merchantmongoData["isActive"]
            returnDict["updatedDate"] = merchantmongoData["createdDate"]
            labels = []
            pageView = []
            transactions = []
            for doc in mongoData:
                if "transactions" in doc and "createdDate" in doc:
                    if mid in doc["transactions"]:
                        labels.append(doc["createdDate"].strftime("%d %b %y"))
                        transactions.append(doc["transactions"][mid][0])
                        pageView.append(doc["transactions"][mid][1])
            returnDict["labels"] = labels
            returnDict["pageViews"] = pageView
            returnDict["transactions"] = transactions
            returnDict["status"] = "200"
            template = render_template("quickview.html", merchantData = returnDict)
            returnDict["html"] = template
        else:
            returnDict["status"] = "400"
    except Exception as ex:
        print(ex)
        returnDict["status"] = "400"
    return jsonify(returnDict)

def getPercentageChange(currVal, baseVal):
    if baseVal == 0:
        return (True, 100)
    if currVal == 0:
        return(False, 100)
    changePer = round(((currVal - baseVal)*100/baseVal), 3)
    if changePer < 0:
        return (False, abs(changePer))
    return (True, changePer)


@app.route("/insights/<mid>", methods = ['GET'])
def getComprehensiveInsights(mid):
    returnDict = {}
    template = None
    try:
        merchantmongoData = mongo.db.MerchantData.find_one({"merchantId": UUID(mid)})
        endtime = datetime.utcnow()
        #change to 7 after testing
        starttime = endtime - timedelta(days=70)
        argstart1 = request.args.get("start1")
        argend1 = request.args.get("end1")
        if argstart1 != None and argend1 != None:
            print(argstart1, argend1)
            starttime = datetime.strptime(argstart1, "%Y-%m-%d")
            endtime = datetime.strptime(argend1, "%Y-%m-%d") + timedelta(days= 1)

        mongoData1 = mongo.db.TransactionData.find({"createdDate":{"$gte":starttime, "$lt": endtime}})
        
        endtime2 = starttime - timedelta(days=1)
        starttime2 = endtime2 - timedelta(days=31)
        argstart2 = request.args.get("start2")
        argend2 = request.args.get("end2")
        if argstart2 != None and argend2 != None:
            print(argstart2, argend2)
            starttime2 = datetime.strptime(argstart2, "%Y-%m-%d")
            endtime2 = datetime.strptime(argend2, "%Y-%m-%d") + timedelta(days= 1)
            
        mongoData2 = mongo.db.TransactionData.find({"createdDate":{"$gte":starttime2, "$lt": endtime2}})
        
        if merchantmongoData != None:
            returnDict["merchantId"] = str(merchantmongoData["merchantId"])
            returnDict["siteUrl"] = merchantmongoData["siteUrl"].replace("https://www.", "").capitalize()
            returnDict["isActive"] = merchantmongoData["isActive"]
            returnDict["updatedDate"] = merchantmongoData["createdDate"]
            labels = []
            pageView = []
            transactions = []
            sumtran1 = 0
            sumpage1 = 0
            for doc in mongoData1:
                if "transactions" in doc and "createdDate" in doc:
                    if mid in doc["transactions"]:
                        labels.append(doc["createdDate"].strftime("%d %b %y"))
                        transactions.append(doc["transactions"][mid][0])
                        pageView.append(doc["transactions"][mid][1])
                        sumtran1 += doc["transactions"][mid][0]
                        sumpage1 += doc["transactions"][mid][1]

            returnDict["labels"] = labels
            returnDict["pageViews1"] = pageView
            returnDict["transactions1"] = transactions
            returnDict["sumTran1"] = sumtran1
            returnDict["sumPage1"] = sumpage1

            pageView1 = []
            transactions1 = []
            sumtran2 = 0
            sumpage2 = 0
            for doc in mongoData2:
                if "transactions" in doc and "createdDate" in doc:
                    if mid in doc["transactions"]:
                        #labels.append(doc["createdDate"].strftime("%d %b %y"))
                        transactions1.append(doc["transactions"][mid][0])
                        pageView1.append(doc["transactions"][mid][1])
                        sumtran2 += doc["transactions"][mid][0]
                        sumpage2 += doc["transactions"][mid][1]
            returnDict["pageViews2"] = pageView1
            returnDict["transactions2"] = transactions1
            returnDict["sumTran2"] = sumtran2
            returnDict["sumPage2"] = sumpage2
            returnDict["isPosTran"], returnDict["chnTran"] = getPercentageChange(sumtran1, sumtran2)
            returnDict["isPosPage"], returnDict["chnPage"] = getPercentageChange(sumpage1, sumpage2)
            returnDict["avgPage"] = (sumpage1 + sumpage2)/((endtime - starttime).days + (endtime2 - starttime2).days)

            returnDict["minDate"] = (datetime.utcnow() - timedelta(days = 180)).strftime("%Y-%m-%d")
            returnDict["maxDate"] = (datetime.utcnow() + timedelta(days = 1)).strftime("%Y-%m-%d")
            returnDict["s1"] = starttime.strftime("%Y-%m-%d")
            returnDict["e1"] = endtime.strftime("%Y-%m-%d")
            returnDict["s2"] = starttime2.strftime("%Y-%m-%d")
            returnDict["e2"] = endtime2.strftime("%Y-%m-%d")

            returnDict["status"] = "200"
            template = render_template("insights.html", merchantData = returnDict)
            returnDict["html"] = template
        else:
            returnDict["status"] = "400"
    except Exception as ex:
        print(ex)
        returnDict["status"] = "400"
    return template


@app.route("/download", methods = ['GET'])
def downloadReport():
    monthlyData = {}
    csvData = []
    fields = ("MerchantId", "TransactionCount", "PageViewCount")
    argstart = request.args.get("start")
    argend = request.args.get("end")
    filename = "report.csv"
    if argstart != None and argend != None:
        monthStart = datetime.strptime(argstart, "%Y-%m-%d")
        monthEnd = datetime.strptime(argend, "%Y-%m-%d") + timedelta(days=1)
        filename = "report_" + argstart + "_to_" + argend + ".csv"
        mongoData = mongo.db.TransactionData.find({"createdDate":{"$gte":monthStart, "$lt": monthEnd}})
        for doc in mongoData:
            if "transactions" in doc:
                for merchantId in doc["transactions"]:
                    if merchantId not in monthlyData:
                        monthlyData[merchantId] = doc["transactions"][merchantId]
                    else:
                        monthlyData[merchantId][0] += doc["transactions"][merchantId][0]
                        monthlyData[merchantId][1] += doc["transactions"][merchantId][1]
        for merchantId in monthlyData:
            merchantData = [merchantId, monthlyData[merchantId][0], monthlyData[merchantId][1]]
            csvData.append(merchantData)


    def generate():
        data = StringIO()
        w = csv.writer(data)

        w.writerow(fields)
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)
        
        w.writerows(csvData)
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

    # stream the response as the data is generated
    response = Response(generate(), mimetype='text/csv')
    # add a filename
    response.headers.set("Content-Disposition", "attachment", filename=filename)
    return response

        

@app.template_filter()
def numberFormat(value):
    return format(int(value), ',d')

    
if __name__ == "__main__":
    app.run(debug=True)