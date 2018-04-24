$(function(){
	// sign up register button
	$('#register_btn').click(function(){
		clearMessage();
		disableButton();
		var formValid = validateFields();
		if (formValid) {
			$.ajax({
				url: '/signUpUser',
				data: $('form').serialize(),
				type: 'POST',
				success: function(response){
					var resp = JSON.parse(response);
					if (resp.status == 'OK'){
						$('#confirmationMessage').prop('class', 'alert alert-success');
						$('#confirmationMessage').html("Successful registration");
						$('#confirmationMessage').css("visibility", "visible");
					} else {
						$('#confirmationMessage').prop('class', 'alert alert-danger');
						$('#confirmationMessage').html("Unsuccessful registration");
						$('#confirmationMessage').css("visibility", "visible");
					}
					enableButton();
				},
				error: function(error){
					console.log(error);
				}
			});
		} else {
			$('#confirmationMessage').prop('class', 'alert alert-warning');
			$('#confirmationMessage').html("Please fill in all required fields.");
			$('#confirmationMessage').css("visibility", "visible");
			enableButton();
		}
	});

	$('#token_btn').click(function() {
		clearMessage();
		// execute this function when click on token button
		$.ajax({
			url: '/checkToken',
			type: 'GET',
			success: function(data){
				var resp = JSON.parse(data);
				//console.log(resp);
				if (resp.status == '200'){
					$('#confirmationMessage').prop('class', 'alert alert-success');
					$('#confirmationMessage').html("Token is valid");
					$('#confirmationMessage').css("visibility", "visible");
				} else {
					$('#confirmationMessage').prop('class', 'alert alert-danger');
					$('#confirmationMessage').html("Token is not valid");
					$('#confirmationMessage').css("visibility", "visible");
				}
			},
			error: function(error){
				console.error(error);
			}
		});
	});

	$('#database_btn').click(function() {
		clearTable();
		// execute this function when click on database button
		$.ajax({
			url: '/loadDatabase',
			type: 'GET',
			success: function(data){
				var resp = JSON.parse(data);
				var rows = resp.rows;
				fillTable(rows);
			},
			error: function(error){
				console.log(error);
			}
		});
	});

	$('#download_btn').click(function() {
		// execute this function when click on database button
		$.ajax({
			url: '/downloadDatabase',
			type: 'GET',
			success: function(){
				console.log('Table successfully downloaded');
			},
			error: function(error){
				console.log(error);
			}
		});
	});

	function clearMessage() {
		$('#confirmationMessage').css("visibility", "hidden");
	}

	function disableButton() {
		$('button').prop('disabled', true);
	}

	function enableButton() {
		$('button').prop('disabled', false);
	}

	function validateFields() {
		var user = $('#txtUsername').val();
		var pass = $('#txtPassword').val();
		var fname = $('#txtfname').val();
		var lname = $('#txtlname').val();
		var lname = $('#txtlname').val();
		var tbox = $('#tickbox').is(':checked');

		if (user == "" || pass == "" || fname == "" || lname == "" || tbox == false) {
			return false;
		}
		return true;
	}

	function fillTable(rows) {
		var numrows = Object.keys(rows).length,
	      table = document.getElementById("database_table").getElementsByTagName('tbody')[0];

		// iteratively add rows to table
    for (var i = 0; i < numrows - 1; i++) {
      var row = table.insertRow(i),
          no = row.insertCell(0),
          date = row.insertCell(1),
          email = row.insertCell(2),
          active = row.insertCell(3);

      no.innerHTML = (i+1).toString();
      date.innerHTML = rows[i][1];
      email.innerHTML = rows[i][0];
      active.innerHTML = rows[i][2]
    }
		$('#database_div').css('visibility', 'visible');
		$('#filterDate').css('visibility', 'visible');
	}

	function clearTable() {
		var table = document.getElementById('database_table');
		var numRows = table.rows.length;
		for (var i = 0; i < numRows-1; i++) {
			table.deleteRow(1);
		}
	}
});
