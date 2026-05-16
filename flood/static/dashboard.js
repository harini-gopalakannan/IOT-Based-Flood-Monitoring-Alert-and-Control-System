let rainChart
let waterChart
let lastTimestamp = null

let map
let marker


// ===== CHART INITIALIZATION =====
function initCharts(){

const rainCtx = document.getElementById("rainChart")
const waterCtx = document.getElementById("waterChart")

if(!rainCtx || !waterCtx) return

rainChart = new Chart(rainCtx,{
type:"line",
data:{
labels:[],
datasets:[{
label:"Rain Sensor Value",
data:[],
borderColor:"#2b6eff",
backgroundColor:"rgba(43,110,255,0.1)",
fill:true
}]
},
options:{responsive:true,animation:false}
})

waterChart = new Chart(waterCtx,{
type:"line",
data:{
labels:[],
datasets:[{
label:"Water Level (cm)",
data:[],
borderColor:"#f39c12",
backgroundColor:"rgba(243,156,18,0.1)",
fill:true
}]
},
options:{responsive:true,animation:false}
})

}


// ===== MAP INITIALIZATION =====
function initMap(){

const mapDiv = document.getElementById("map")
if(!mapDiv) return

const lat = 13.0827
const lon = 80.2707

map = L.map('map').setView([lat, lon], 12)

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
attribution:'© OpenStreetMap'
}).addTo(map)

marker = L.marker([lat, lon]).addTo(map)

marker.bindPopup("Flood Monitoring Station").openPopup()

}


// ===== FETCH DATA FROM FLASK =====
async function fetchData(){

try{

const response = await fetch("/data")
const data = await response.json()

// ===== SENSOR VALUES =====
const rainValue = document.getElementById("rainValue")
if(rainValue) rainValue.innerText = data.rainfall

const waterValue = document.getElementById("waterValue")
if(waterValue) waterValue.innerText = data.water + " cm"


// ===== WEATHER VALUES =====
const tempValue = document.getElementById("tempValue")
if(tempValue) tempValue.innerText = data.temperature + " °C"

const humidityValue = document.getElementById("humidityValue")
if(humidityValue) humidityValue.innerText = data.humidity + " %"

const pressureValue = document.getElementById("pressureValue")
if(pressureValue) pressureValue.innerText = data.pressure + " hPa"


// ===== FLOOD RISK SCORE =====
const riskScore = document.getElementById("riskScore")
if(riskScore) riskScore.innerText = data.risk_score + " %"


// ===== EMAIL STATUS (NEW FIX) =====
const emailStatus = document.getElementById("emailStatus")
if(emailStatus) emailStatus.innerText = data.email_status


// ===== RAIN STATUS =====
const rainStatusElement = document.getElementById("rainStatus")

if(rainStatusElement){

rainStatusElement.innerText = data.rain_status
rainStatusElement.className = "rain-status"

if(data.rain_status === "RAIN DETECTED")
rainStatusElement.classList.add("rain-heavy")

else
rainStatusElement.classList.add("rain-normal")

}


// ===== FLOOD RISK LEVEL =====
const riskElement = document.getElementById("riskStatus")
const riskCard = document.getElementById("riskCard")

if(riskElement)
riskElement.innerText = data.risk

if(riskCard){

riskCard.className = "card"

if(data.risk==="DANGER")
riskCard.classList.add("danger")

else if(data.risk==="WARNING")
riskCard.classList.add("warning")

else
riskCard.classList.add("safe")

}


// ===== RAIN PROGRESS BAR =====
const rainBar = document.getElementById("rainBar")

if(rainBar)
rainBar.style.width = Math.min(data.rainfall/40,100) + "%"


// ===== PUMP STATUS =====
const toggle = document.getElementById("motorToggle")

if(toggle){

if(data.motor==="ON")
toggle.classList.add("active")

else
toggle.classList.remove("active")

}


// ===== UPDATE CHARTS =====
if(rainChart && waterChart && data.time !== lastTimestamp){

rainChart.data.labels.push(data.time)
rainChart.data.datasets[0].data.push(data.rainfall)

waterChart.data.labels.push(data.time)
waterChart.data.datasets[0].data.push(data.water)

rainChart.update()
waterChart.update()

lastTimestamp = data.time

}


// ===== MAP POPUP =====
if(marker){

marker.setPopupContent(

`<b>Flood Monitoring Station</b><br>
Rain Sensor: ${data.rainfall}<br>
Water Level: ${data.water} cm<br>
Temperature: ${data.temperature} °C<br>
Humidity: ${data.humidity}%<br>
Pressure: ${data.pressure} hPa<br>
Risk Level: ${data.risk}`

)

}

}catch(error){
console.log("Dashboard fetch error:",error)
}

}


// ===== INITIALIZE =====
initCharts()
initMap()
fetchData()

setInterval(fetchData,5000)