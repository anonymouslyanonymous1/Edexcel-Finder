const specMapping = {
    New: ["Chemistry", "Physics", "Biology"],
    Old: ["Chemistry", "Physics", "Biology"],
    Both: ["Chemistry", "Physics", "Biology"]
}
const codeMapping = {
    "Chemistry": "Chemistry",
    "Physics": "Physics",
    "Biology": "Biology",
}
const units = {"New": {
    "Chemistry": ["Unit 1", "Unit 2", "Unit 4", "Unit 5"],
    "Physics": ["Unit 1", "Unit 2", "Unit 4", "Unit 5"],
    "Biology": ["Unit 1", "Unit 2", "Unit 4", "Unit 5"],
},
"Old": {
    "Chemistry": ["Unit 1", "Unit 2", "Unit 4", "Unit 5"],
    "Physics": ["Unit 1", "Unit 2", "Unit 4", "Unit 5"],
    "Biology": ["Unit 1", "Unit 2", "Unit 4", "Unit 5"],
},
"Both": {
    "Chemistry": ["Unit 1", "Unit 2", "Unit 4", "Unit 5"],
    "Physics": ["Unit 1", "Unit 2", "Unit 4", "Unit 5"],
    "Biology": ["Unit 1", "Unit 2", "Unit 4", "Unit 5"],
}}
window.addEventListener('pageshow', (event) => {
    document.querySelector('.search-button').disabled = false;
})
let Spec = ""
function handleSpec(radio){
    Spec = radio.id
    const unitlist = document.querySelector("#unit-list")
    unitlist.innerHTML = ""
    const radios = document.getElementsByName('subject');
    const checkedRadio = Array.from(radios).find(radio => radio.checked);
    if (checkedRadio) {
        checkedRadio.checked = false;
    }
}
let Subject = ""
let Unit = ""
function handleSubject(radio){
    Subject = radio.id
    Unit = ""
    const list = document.querySelector("#unit-list")
    if(Spec === ""){
        list.innerHTML = `<p style="font-family: Coolvetica; color: white">Choose a specification</p>`
    }
    else{
        list.innerHTML = ""
        const Units = units[Spec][radio.id]
        for (let unit of Units){
            list.innerHTML = list.innerHTML +`<input type="radio" name="unit" class="unit-input" onclick="handleUnit(this)" id="Unit ${unit[unit.length-1]}"></input><label for="Unit ${unit[unit.length-1]}" class="unit-label"><div>${unit}</div></label>`
        }
    }
}
function handleUnit(radio){
    Unit = radio.id
}
let Search = ""
function handleSearch(event){
    Search = event.target.value
}
function handleSubmit(){
    if (Spec === "" || Subject === "" || Unit === "" || Search === ""){
        window.alert("⛔ You haven't chosen either the specification, subject, unit or haven't entered a search term!")
    }
    else{
        document.querySelector('.search-button').disabled = true
        window.location.href = `/SixMarkSearchresults?subject=${Subject}&unit=${Unit}&search=${Search}&choice=${Spec.toLowerCase()}`
    }
}
document.addEventListener("DOMContentLoaded", () => {    
    const blob = document.getElementById("blob");

    window.onpointermove = event => { 
    const { clientX, clientY } = event;
    
    blob.animate({
        left: `${clientX}px`,
        top: `${clientY}px`
    }, { duration: 3000, fill: "forwards" });
    }
})
