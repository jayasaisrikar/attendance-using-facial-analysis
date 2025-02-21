function initializeCharts(attendanceData) {
    // Monthly Attendance Chart
    const monthlyCtx = document.getElementById('monthlyAttendanceChart').getContext('2d');
    new Chart(monthlyCtx, {
        type: 'line',
        data: {
            labels: attendanceData.months,
            datasets: [{
                label: 'Attendance Percentage',
                data: attendanceData.percentages,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });

    // Subject-wise Attendance Chart
    const subjectCtx = document.getElementById('subjectAttendanceChart').getContext('2d');
    new Chart(subjectCtx, {
        type: 'bar',
        data: {
            labels: attendanceData.subjects,
            datasets: [{
                label: 'Attendance Percentage',
                data: attendanceData.subjectPercentages,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgb(54, 162, 235)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}