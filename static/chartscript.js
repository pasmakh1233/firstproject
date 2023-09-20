let myChart // Declare a variable to hold the chart instance

function loadChart (data) {
  // Destroy the existing chart if it exists
  if (myChart) {
    myChart.destroy()
  }

  // Create a chart using Chart.js
  const ctx = document.getElementById('chart_canvas').getContext('2d')
  myChart = new Chart(ctx, {
    type: 'bar',
    data: data,
    options: {
      // Chart configuration options (e.g., title, axes)
    }
  })
}

function toggleForm () {
  // Show the form container
  const formContainer = document.getElementById('form_container')
  formContainer.style.display = 'block'

  // Hide the chart canvas
  const chartCanvas = document.getElementById('chart_canvas')
  chartCanvas.style.display = 'none'
}

function hideForm () {
  // Hide the form container
  const formContainer = document.getElementById('form_container')
  formContainer.style.display = 'none'
}

function loadChart1 () {
  hideForm()

  fetch('/chart_data1')
    .then(response => response.json())
    .then(data => {
      console.log(data)
      loadChart(data)
    })
    .catch(error => {
      console.error('Error fetching chart data:', error)
    })
}

function loadChart2 () {
  hideForm()

  fetch('/chart_data2')
    .then(response => response.json())
    .then(data => {
      console.log(data)
      loadChart(data)
    })
    .catch(error => {
      console.error('Error fetching chart data:', error)
    })
}
