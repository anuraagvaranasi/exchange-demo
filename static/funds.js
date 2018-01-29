function confirm_transaction(form){
	var acc = form.account.value;
	var trans = form.type.value;
	var amount = form.amount.value;
	if(amount == 0 || trans == "" || acc == ""){
		alert("Please complete the form");
	}
	else{
		if(trans == "withdraw"){
			var msg = "This will " + trans + " $" + amount + " into " + acc;
		}
		else{
			var msg = "This will " + trans + " $" + amount + " from " + acc;
		}
		var check = confirm(msg);
		if(check){
			document.getElementById("submit").click();
		}
	}
}

