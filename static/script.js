const specMapping = {
    New: ["WFM0", "WMA1", "WME0", "WST0", "WDM", "Chemistry", "Physics", "Biology"],
    Old: ["WFM0", "WME0", "WST0", "WDM", "Chemistry", "Physics", "Biology"],
    Both: ["WFM0", "WME0", "WST0", "WDM", "Chemistry", "Physics", "Biology"]
}
const codeMapping = {
    "WFM0": "Further Maths",
    "WMA1": "Pure Maths",
    "WDM": "Decision",
    "WME0": "Mechanics",
    "WST0": "Statistics",
    "Chemistry": "Chemistry",
    "Physics": "Physics",
    "Biology": "Biology",
}
const units = {"New": {
    "WFM0": ["FP1", "FP2", "FP3"],
    "WME0": ["M1", "M2", "M3"],
    "WST0": ["S1", "S2", "S3"],
    "WMA1": ["P1", "P2", "P3", "P4"],
    "WDM": ["D1"],
    "Chemistry": ["Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5", "Unit 6"],
    "Physics": ["Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5", "Unit 6"],
    "Biology": ["Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5", "Unit 6"],
},
"Old": {
    "WFM0": ["FP1", "FP2", "FP3"],
    "WME0": ["M1", "M2", "M3"],
    "WST0": ["S1", "S2", "S3"],
    "WDM": ["D1"],
    "Chemistry": ["Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5", "Unit 6", "Unit 7"],
    "Physics": ["Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5", "Unit 6", "Unit 7"],
    "Biology": ["Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5", "Unit 6", "Unit 7"],
},
"Both": {
    "WFM0": ["FP1", "FP2", "FP3"],
    "WME0": ["M1", "M2", "M3"],
    "WST0": ["S1", "S2", "S3"],
    "WDM": ["D1"],
    "Chemistry": ["Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5", "Unit 6", "Unit 7"],
    "Physics": ["Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5", "Unit 6", "Unit 7"],
    "Biology": ["Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5", "Unit 6", "Unit 7"],
}}
window.addEventListener('pageshow', (event) => {
    document.querySelector('.search-button').disabled = false;
})
let Spec = ""
function handleSpec(radio){
    Spec = radio.id
    const radios = document.getElementsByName('subject');
    const checkedRadio = Array.from(radios).find(radio => radio.checked);
    if (checkedRadio) {
        checkedRadio.checked = false;
    }
    const subjects = specMapping[radio.id]
    const list = document.querySelector("#subject-list")
    list.innerHTML = ""
    const unitlist = document.querySelector("#unit-list")
    unitlist.innerHTML = ""
    for (let subject of subjects){
        list.innerHTML = list.innerHTML + `<input type="radio" onclick="handleSubject(this)" name="subject" id="${subject}"><label for="${subject}"><p>${codeMapping[subject]}</p></label>`
    }
}
let Subject = ""
let Unit = ""
function handleSubject(radio){
    Subject = radio.id
    Unit = ""
    const list = document.querySelector("#unit-list")
    list.innerHTML = ""
    const Units = units[Spec][radio.id]
    for (let unit of Units){
        list.innerHTML = list.innerHTML +`<input type="radio" name="unit" class="unit-input" onclick="handleUnit(this)" id="Unit ${unit[unit.length-1]}"></input><label for="Unit ${unit[unit.length-1]}" class="unit-label"><div>${unit}</div></label>`
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
        window.location.href = `/results?subject=${Subject}&unit=${Unit}&search=${Search}&choice=${Spec.toLowerCase()}`
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