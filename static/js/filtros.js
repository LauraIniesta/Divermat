function myFunction() {
var select = document.getElementById('curso');
select.addEventListener('change',
    function(){
    var selectedOption = this.options[select.selectedIndex];
    console.log(selectedOption.value + ': ' + selectedOption.text);
    $("#result").text(emailaddress + " is not correct, please retry:(");

    });
}  