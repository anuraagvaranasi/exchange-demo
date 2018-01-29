#!/usr/bin/python3
import os
from flask import Flask, render_template, request, url_for, redirect
from urllib.request import urlopen
import json
import requests
import fileinput

app=Flask(__name__)

#routed page functions are first

#home page, shows basic overview of everything
@app.route('/')
def home():
	funds = get_funds()
	accounts = get_accounts()
	stocks = get_stocks()
	values = owned_stock_values()
	#get total of all stocks
	total = 0
	for name in stocks:
		total += values[name]*stocks[name] 
	return render_template("home.html",funds=funds,accounts=accounts,stocks=stocks,values=values,total=total)

#depost/widthdraw from accounts 
#only adds/takes away from funds (as it obviously cannot access a bank account)
@app.route('/funds',methods=['GET','POST'])
def funds():
	if(request.method == 'GET'):
		funds = get_funds()
		accounts = get_accounts()
		return render_template("funds.html",funds=funds,accounts=accounts)
	else:
		funds = get_funds()
		form = request.form
		
		#add/take away depending on value
		if(form.get('type') == "withdraw"):
			funds -= int(form.get('amount'))
		else:
			funds += int(form.get('amount'))
		#now change funds and return
		edit_funds(funds)
		
		return redirect(url_for('home'))

@app.route('/addAcc',methods=['POST'])
def add_acc():
	form = request.form
	path = os.path.join("data","cash_accounts.txt")
	f = open(path,'a')
	f.write("\n")#dont forget to add a new line!!
	f.write(form.get('name'))
	f.close()
	return redirect(url_for('funds'))

#buy/sell stocks
@app.route('/market', methods=['POST','GET'])
def market():
	if(request.method == 'GET'):
		stocks = get_stocks()
		values = owned_stock_values()
		print(values)
		funds = get_funds()
		return render_template("market.html",stocks=stocks,funds=funds,values=values,search=[])
	else:
		form = request.form
		#check if they serached for anything, if they did, display it		
		if(form.get('search') != ""):
			stocks = get_stocks()
			values = owned_stock_values()
			funds = get_funds()
			search = get_stock_values(form.get('search'))
			return render_template("market.html",stocks=stocks,funds=funds,values=values,search=search)
		#check if buy/sell order exists then get stock values
		else:
			stock_string = ""
			if(form.get('buy')):
				buy = form.get('buy')
				stock_string += buy + ","
			if(form.get('sell')):
				sell = form.get('sell')
				stock_string += sell
			stocks_values = get_stock_values(stock_string)
			#now process payments
			#sell first so that you can buy and sell stocks at same time
			#modify owned_stocks and pass that into edit_stocks file
			funds = get_funds()
			owned_stocks = get_stocks()


			if(form.get('sell')):
				sell_amount = int(form.get('sell_amount'))
				#change to max amount owned
				if(sell_amount > owned_stocks[sell]):
					sell_amount = owned_stocks[sell]
				#change funds value depending on what is sold
				funds += sell_amount * stocks_values[sell]
				#then change amount of the stock that is now owned
				owned_stocks[sell] = owned_stocks[sell] - sell_amount

			#now buy stocks
			if(form.get('buy')):
				buy_amount = int(form.get('buy_amount'))
				#if they are trying to buy more than the amount of funds they have, cap it at max possible
				while(buy_amount*stocks_values[buy] > funds):
					buy_amount -= 1
				funds -= buy_amount * stocks_values[buy]
				#now change stock amount for however much was bought
				#have to check if its in the dict first though or else will cause an error
				if(buy in owned_stocks):
					owned_stocks[buy] = owned_stocks[buy] + buy_amount
				else:
					owned_stocks[buy] = buy_amount
				
			#change stocks file to reflect this
			edit_stocks(owned_stocks)
			#and finally change funds before returning
			edit_funds(funds)

			return redirect(url_for('market'))


#####functions that are not routed are below here#####


#get funds from "server" for account
def get_funds():
	path = os.path.join("data","cash_amount.txt")
	f = open(path,'r')
	ammount = f.readline()
	#assuming that data is correct
	ammount = float(ammount)
	f.close()
	return ammount

#get list of accounts from "server"
def get_accounts():
	path = os.path.join("data","cash_accounts.txt")
	f = open(path)
	accounts = []
	for line in f:
		accounts.append(line.rstrip())#remove trailing new line character
	f.close()
	return sorted(accounts)

#get list of stocks
def get_stocks():
	path = os.path.join("data","stocks.txt")
	f = open(path)
	stocks = {}
	for line in f:
		parts = line.split()
		if(len(parts) == 2): #so that empty lines are ignored
			stocks[parts[0].lower()] = int(parts[1]) #dont want to deal with case problems
	f.close()
	return stocks

#get the stock values for what is owned
def owned_stock_values():
	stocks = get_stocks()
	stock_names = ""
	#have to create string in correct format for api call
	for name in stocks:
		stock_names += name
		stock_names += "," #api allows for a trailing comma without affecting data
	return get_stock_values(stock_names)

#get stock information from string formatted with commas between stock names
def get_stock_values(symbols):
	url_start = "https://www.alphavantage.co/query?function=BATCH_STOCK_QUOTES&symbols="
	url_end = "&apikey=WFDSO8PV9QCX302F"
	url = url_start + symbols + url_end

	#get json object from url
	html = urlopen(url)
	json = requests.get(url).json()

	#turn json object into useful formatted information
	stock_dict = {}
	for stock in json['Stock Quotes']:
		stock_dict[stock['1. symbol'].lower()] = float(stock['2. price'])#lower to deal with case issues
	return stock_dict

#change funds value to what is given
def edit_funds(funds):
	path = os.path.join("data","cash_amount.txt")
	f = open(path,'w')
	f.write(str(funds))
	f.close()


#edit stocks file to contain what the current portfolio looks like
def edit_stocks(owned_stocks):
	path = os.path.join("data","stocks.txt")
	f = open(path,"w")
	#write the string in the correct format for every stock
	for element in owned_stocks:
		f.write(element + " " + str(owned_stocks[element]) + "\n")
	f.close()
	
#running the app
#defaults to host on port 5000
if(__name__ == '__main__'):
	app.run(debug=True)