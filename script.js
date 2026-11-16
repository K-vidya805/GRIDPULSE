document.addEventListener("DOMContentLoaded", function () {
    const API_URL = "http://127.0.0.1:5000";
    let dailyChart = null;
    let weeklyPredictions = [];
    let selectedDay = null;

    const taluks = {
        "Belagavi": ["Belagavi North", "Belagavi South", "Athani", "Bailhongal", "Chikkodi", "Gokak", "Hukkeri", "Khanapur", "Ramdurg", "Raybag", "Saundatti"],
        "Bagalkot": ["Bagalkot", "Badami", "Jamkhandi", "Mudhol"],
        "Dharwad": ["Dharwad", "Hubballi", "Kalghatgi", "Kundgol"],
        "Uttara Kannada": ["Karwar", "Sirsi", "Kumta", "Bhatkal"],
        "Vijayapura": ["Vijayapura", "Indi", "Sindagi", "Basavana Bagewadi"],
        "Gadag": ["Gadag", "Mundargi", "Nargund", "Ron"],
        "Haveri": ["Haveri", "Byadgi", "Ranebennur", "Savanur"]
    };

    const districtSelect = document.getElementById("district");
    const talukSelect = document.getElementById("taluk");
    const continueButton = document.getElementById("continueButton");
    const locationMessage = document.getElementById("locationMessage");
    const locationPage = document.getElementById("locationPage");
    const forecastPage = document.getElementById("forecastPage");
    const dayPage = document.getElementById("dayPage");
    const selectedLocation = document.getElementById("selectedLocation");
    
    // 1. DROPDOWN LOGIC
    districtSelect.addEventListener("change", function () {
        const selectedDistrict = this.value;
        talukSelect.innerHTML = '<option value="">Select Taluk</option>';
        
        if (selectedDistrict && taluks[selectedDistrict]) {
            taluks[selectedDistrict].forEach(function (name) {
                const option = document.createElement("option");
                option.value = name;
                option.textContent = name;
                talukSelect.appendChild(option);
            });
            talukSelect.disabled = false; 
        } else {
            talukSelect.innerHTML = '<option value="">Select District First</option>';
            talukSelect.disabled = true;
        }
    });

    // 2. CONTINUE BUTTON
    continueButton.addEventListener("click", async function () {
        const district = districtSelect.value;
        const taluk = talukSelect.value;

        if (!district || !taluk) {
            locationMessage.textContent = "Please select both district and taluk.";
            return;
        }

        if (district !== "Belagavi" || taluk !== "Belagavi North") {
            locationMessage.textContent = "Forecasting is currently available only for Belagavi North.";
            return;
        }

        this.disabled = true;
        this.textContent = "Generating...";
        locationMessage.textContent = "";

        try {
            const days = getNextSevenDays();
            weeklyPredictions = [];

            for (let i = 0; i < days.length; i++) {
                weeklyPredictions.push(await getPrediction(days[i], i));
            }

            selectedLocation.textContent = district + " District / " + taluk;
            displayWeeklyForecast();
            
            locationPage.classList.add("hidden");
            forecastPage.classList.remove("hidden");
            
        } catch (error) {
            locationMessage.textContent = "Error generating predictions.";
        } finally {
            this.disabled = false;
            this.textContent = "Continue →";
        }
    });

    // 3. BACK BUTTONS
    document.getElementById("backButton").addEventListener("click", function () {
        forecastPage.classList.add("hidden");
        locationPage.classList.remove("hidden");
    });

    document.getElementById("forecastBackButton").addEventListener("click", function () {
        dayPage.classList.add("hidden");
        forecastPage.classList.remove("hidden");
    });

    // 4. HELPER FUNCTIONS
    function getNextSevenDays() {
        const days = [];
        for (let i = 0; i < 7; i++) {
            const date = new Date();
            date.setDate(date.getDate() + i);
            days.push({
                date: date,
                dateString: date.toISOString().split('T')[0],
                label: date.toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "short" })
            });
        }
        return days;
    }

    async function getPrediction(day, index, temperatureOverride = null) {
        const baseTemp = temperatureOverride !== null ? temperatureOverride : 28 + (index % 4) * 2;
        const weather = {
            "RAINFALL (mm)": index % 3 === 0 ? 0 : 1.5,
            temp_max: baseTemp + 5,
            temp_min: baseTemp - 5,
            temp_mean: baseTemp
        };

        const inputData = {
            ...weather,
            month: day.date.getMonth() + 1,
            day: day.date.getDate(),
            day_of_week: day.date.getDay(),
            day_of_year: Math.floor((day.date - new Date(day.date.getFullYear(), 0, 0)) / 86400000)
        };

        try {
            const response = await fetch(`${API_URL}/api/predict`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(inputData)
            });
            if (!response.ok) throw new Error("API Error");
            const result = await response.json();
            return { ...day, demand: Number(result.predicted_demand_MW), weather: weather };
        } catch (error) {
            // Fallback if API is offline
            const simDemand = 85 + (index * 3) + (temperatureOverride ? (temperatureOverride - 30) * 1.5 : 0);
            return { ...day, demand: simDemand, weather: weather };
        }
    }

    function displayWeeklyForecast() {
        const container = document.getElementById("weeklyForecast");
        container.innerHTML = "";

        weeklyPredictions.forEach(function (day, index) {
            const card = document.createElement("button");
            card.className = "daily-item";
            card.innerHTML = `
                <span>
                    <strong>${index === 0 ? "Today" : day.label}</strong>
                    <small>${day.dateString}</small>
                </span>
                <span class="daily-value">${day.demand.toFixed(2)} MW</span>
                <span>→</span>
            `;
            card.addEventListener("click", () => showDailyDetails(index));
            container.appendChild(card);
        });
    }

    function showDailyDetails(index) {
        selectedDay = index;
        const day = weeklyPredictions[index];
        
        forecastPage.classList.add("hidden");
        dayPage.classList.remove("hidden");

        document.getElementById("dayTitle").textContent = index === 0 ? "Today's Forecast" : day.label + " Forecast";
        document.getElementById("daySubtitle").textContent = `Belagavi North | ${day.dateString}`;
        document.getElementById("dailyDemand").textContent = `${day.demand.toFixed(2)} MW`;
        document.getElementById("weatherDescription").textContent = `Simulated weather input: ${day.weather.temp_mean}°C`;
        
        document.getElementById("temperatureSlider").value = day.weather.temp_mean;
        document.getElementById("temperatureValue").textContent = `${day.weather.temp_mean}°C`;
        document.getElementById("simWeatherText").textContent = `${day.weather.temp_max}°C, Sunny`;
        
        drawDailyGraph(day);
        updateAdvice(day.demand);
    }

    function drawDailyGraph(day) {
        const canvas = document.getElementById("dailyChart");
        if (dailyChart) dailyChart.destroy();

        const base = day.demand;
        const hourlyValues = [base * 0.70, base * 0.72, base * 0.80, base * 0.95, base * 0.78];
        const peakValue = Math.max(...hourlyValues);
        const peakIndex = hourlyValues.indexOf(peakValue);

        dailyChart = new Chart(canvas, {
            type: "line",
            data: {
                labels: ["12 AM", "6 AM", "12 PM", "6 PM", "12 AM"],
                datasets: [{
                    data: hourlyValues,
                    borderColor: "#EF4444",
                    borderWidth: 3,
                    backgroundColor: "rgba(239, 68, 68, 0.15)",
                    fill: true,
                    tension: 0.4,
                    pointRadius: (ctx) => ctx.dataIndex === peakIndex ? 7 : 4,
                    pointBackgroundColor: "#EF4444"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
                scales: {
                    y: { beginAtZero: false, grid: { color: "#E2E8F0" } },
                    x: { grid: { display: false } }
                }
            },
            plugins: [{
                id: 'customPeakLabel',
                afterDraw: (chart) => {
                    const ctx = chart.ctx;
                    const meta = chart.getDatasetMeta(0);
                    const peakPoint = meta.data[peakIndex];
                    
                    if (peakPoint) {
                        const text = `${Math.round(peakValue)} units`;
                        ctx.font = 'bold 12px Arial';
                        const textWidth = ctx.measureText(text).width;
                        const boxWidth = textWidth + 16;
                        const x = peakPoint.x - (boxWidth / 2);
                        const y = peakPoint.y - 35;

                        ctx.fillStyle = "#EF4444";
                        ctx.beginPath();
                        ctx.roundRect(x, y, boxWidth, 24, 6);
                        ctx.fill();

                        ctx.beginPath();
                        ctx.moveTo(peakPoint.x - 5, y + 24);
                        ctx.lineTo(peakPoint.x + 5, y + 24);
                        ctx.lineTo(peakPoint.x, y + 30);
                        ctx.fill();

                        ctx.fillStyle = "#FFFFFF";
                        ctx.textAlign = "center";
                        ctx.textBaseline = "middle";
                        ctx.fillText(text, peakPoint.x, y + 12);
                    }
                }
            }]
        });
    }

    // 5. SLIDER
    const slider = document.getElementById("temperatureSlider");
    slider.addEventListener("input", function () {
        document.getElementById("temperatureValue").textContent = this.value + "°C";
    });

    slider.addEventListener("change", async function () {
        if (selectedDay === null) return;

        const temperature = Number(this.value);
        const day = weeklyPredictions[selectedDay];
        const resultText = document.getElementById("simulationResult");
        
        resultText.textContent = "Simulating...";

        try {
            const result = await getPrediction(day, selectedDay, temperature);
            
            document.getElementById("dailyDemand").textContent = `${result.demand.toFixed(2)} MW`;
            document.getElementById("simWeatherText").textContent = `${temperature}°C, Sunny`;
            
            day.demand = result.demand; 
            drawDailyGraph(day);
            updateAdvice(result.demand);
            
            resultText.textContent = `Simulated demand at ${temperature}°C: ${result.demand.toFixed(2)} MW`;
        } catch (error) {
            resultText.textContent = "Simulation failed.";
        }
    });

    function updateAdvice(demand) {
        const adviceTitle = document.getElementById("adviceTitle");
        const adviceText = document.getElementById("adviceText");
        const alertBox = document.querySelector(".alert-box");

        if (demand >= 95) {
            adviceTitle.textContent = "High Demand Expected!";
            adviceText.textContent = "Start backup power plant at 2:00 PM.";
            alertBox.style.borderColor = "#EF4444";
        } else if (demand >= 90) {
            adviceTitle.textContent = "Moderate to High Demand";
            adviceText.textContent = "Monitor electricity consumption and review available resources.";
            alertBox.style.borderColor = "#F59E0B";
        } else {
            adviceTitle.textContent = "Normal Demand Expected";
            adviceText.textContent = "Continue routine electricity demand monitoring.";
            alertBox.style.borderColor = "#10B981";
        }
    }
});