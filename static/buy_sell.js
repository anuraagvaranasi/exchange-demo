function confirm_buy_sell(form){
	var buy = form.buy.value;
	var sell = form.sell.value;
	//only send form data for 
	if(buy){
		form.buy_amount.value = prompt("How many would you like to buy?\n(Buying more than max funds will buy maximum amount", "0");
	}
	if(sell){
		form.sell_amount.value = prompt("How many would you like to sell?\n(Selling more than max will automatically sell max", "0");
	}
	if(buy || sell){
		document.getElementById("submit").click();
	}
}

