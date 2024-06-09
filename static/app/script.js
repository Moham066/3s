const search_input = document.getElementById("search_input");
const rows = document.querySelectorAll(".info table tbody tr");

search_input.addEventListener("keyup", function(event){
const q = event.target.value.toLowerCase();  
rows.forEach((row) => {
row.querySelector("td.produit_name").textContent.toLowerCase().startsWith(q) ?(row.style.display="table-row") : (row.style.display="none");

});
 
});