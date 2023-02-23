from flask import Flask, render_template, request, send_file, redirect, url_for, Response, send_from_directory
import flask
import requests
import bs4
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import os
import urllib.parse
from datetime import datetime

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def MainPage():
	return render_template('POMS_Landing.html')


@app.route('/PortStatus', methods=['GET', 'POST'])
def Track():
	contReq = request.form['contNos'].replace('"','')
	if (len(contReq)<=0):
		return "No Container Numbers Found!"
	
	if ("," in contReq):
		contSplits = contReq.split(",")
	else:
		contSplits = contReq.split("\n")
	#print(contSplits)
	s = requests.Session()
	result = "<table>"
	nthContainer = 1
	foundCont = 0
	r = s.get("https://kdseodb.smportkolkata.in/ccuPomsPosWeb/index.jsp")
	id1 = r.cookies['JSESSIONID']
	#print("id1="+str(id1))
	r2 = s.get("https://kdseodb.smportkolkata.in/ccuPomsPosWeb/apps/dos/PosCTS.xhtml")
	soup1 = bs4.BeautifulSoup(r2.text)
	viewState = (soup1.find(id='j_id__v_0:javax.faces.ViewState:1'))['value']
	viewState = urllib.parse.quote(viewState.encode('utf8'))
	id2 = r2.cookies['oam.Flash.RENDERMAP.TOKEN']
	#print("*viewState = " + viewState)


	#print("***id2="+str(id2))
	headers = {'Accept': 'application/xml, text/xml, */*; q=0.01', 'Accept-Language': 'en-US,en;q=0.9', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Faces-Request': 'partial/ajax', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36', 'X-Requested-With': 'XMLHttpRequest', 'Cookie': 'JSESSIONID='+id1+'; oam.Flash.RENDERMAP.TOKEN=-'+id2+''}

	
	for cont in contSplits:
		print("Current Cont: ["+str(nthContainer) +"]"+cont)
		if(len(cont) == 11 and "**" not in cont):
			payload = 'javax.faces.partial.ajax=true&javax.faces.source=form1%3AbtnSearch&javax.faces.partial.execute=form1&javax.faces.partial.render=form1&form1%3AbtnSearch=form1%3AbtnSearch&form1%3AcomMloCd_focus=&form1%3AcomMloCd_input=NONE&form1%3AtxtCntNo='+str(cont)+'&form1%3AtblData_scrollState=0%2C0&form1_SUBMIT=1&javax.faces.ViewState='+str(viewState)
			r3 = s.post("https://kdseodb.smportkolkata.in/ccuPomsPosWeb/apps/dos/PosCTS.xhtml", cookies=r.cookies, headers=headers, data=payload)
			
			print("========== CONT RESPONSE START FROM POMS ================")
			#print(r3.text)
			soup = bs4.BeautifulSoup(r3.text, "lxml")
			#print(soup)
			#print("Soup Above ^^^")
			print("========== CONT RESPONSE END FROM POMS ================")
			contData = str(soup.find(id='form1:tblData'))
			containerFound = soup.find(text='No records found.')
			#print(contData)
			#print("containerFound = "+str(containerFound))
			if (len(contData) > 2318 and containerFound==None):
				#contData = contData[2318:]
				result += "<tr><td role=\"failcell2\">"+str(nthContainer)+"</td><td>" + contData[2318:] + "</tr>"
				foundCont += 1
			else:
				contData = str(soup.find(text="No records found."))
				if(contData!=None):
					result += "<tr><td role=\"failcell\">"+str(nthContainer)+"</td><td>"+str(cont)+" - Missing Container - (No records found.)</td></tr>"
		if ("**" in cont):
			result += "<tr><td role=\"failcell\">"+str(nthContainer)+"</td><td style='font-size:150%'><b>"+str(cont.replace("**",""))+"</b></td></tr>"
		nthContainer+=1
	now = now = datetime.now()
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
	foundStr =  "<p style='font-size: 150%'>[Checked @ "+str(dt_string)+" ] Result Found :"+ str(foundCont) +" of "+ str(nthContainer - 1) +" Containers <p>"
	result += '</table>'		
	result = foundStr + result
	return result 


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080, debug=True)

