$(document).ready(function() {
    $('#frmBMI').submit(function(e) {
        e.preventDefault();
        
        var heightFt = $('input[name="height_ft"]').val(),
            heightIn = $('input[name="height_in"]').val(),
            height = parseFloat(heightFt * 12) + parseFloat(heightIn);
            weight = $('input[name="weight"]').val(),
            BMI = calculateBMI(height, weight);
        
        $('#response').text('Your BMI is '+BMI);
    });
});

function calculateBMI(height, weight) {
	var BMI = (weight / (height * height)) * 703
	
	return Math.round(BMI * Math.pow(10, 2)) / Math.pow(10, 2);
}