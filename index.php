<?php include 'top.inc.php'; ?>

<div class="row">
    <!-- Small boxes (Stat box) -->
    <div class="col-lg-3 col-6">
      <!-- small box -->
      <div class="small-box bg-info">
        <div class="inner">
          <h3>150</h3>
          <p>New Orders</p>
        </div>
        <div class="icon">
          <i class="ion ion-bag"></i>
        </div>
        <a href="#" class="small-box-footer">More info <i class="fas fa-arrow-circle-right"></i></a>
      </div>
    </div>
    <!-- ./col -->
    <div class="col-lg-3 col-6">
      <!-- small box -->
      <div class="small-box bg-success">
        <div class="inner">
          <h3>53<sup style="font-size: 20px">%</sup></h3>
          <p>Bounce Rate</p>
        </div>
        <div class="icon">
          <i class="ion ion-stats-bars"></i>
        </div>
        <a href="#" class="small-box-footer">More info <i class="fas fa-arrow-circle-right"></i></a>
      </div>
    </div>
    <!-- ./col -->
    <div class="col-lg-3 col-6">
      <!-- small box -->
      <div class="small-box bg-warning">
        <div class="inner">
          <h3>44</h3>
          <p>User Registrations</p>
        </div>
        <div class="icon">
          <i class="ion ion-person-add"></i>
        </div>
        <a href="#" class="small-box-footer">More info <i class="fas fa-arrow-circle-right"></i></a>
      </div>
    </div>
    <!-- ./col -->
    <div class="col-lg-3 col-6">
      <!-- small box -->
      <div class="small-box bg-danger">
        <div class="inner">
          <h3>65</h3>
          <p>Unique Visitors</p>
        </div>
        <div class="icon">
          <i class="ion ion-pie-graph"></i>
        </div>
        <a href="#" class="small-box-footer">More info <i class="fas fa-arrow-circle-right"></i></a>
      </div>
    </div>
    <!-- ./col -->
</div>
<!-- /.row -->

<div class="row">
  <section class="col-lg-7 connectedSortable">
    <!-- Line chart card -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">
          <i class="fas fa-chart-line mr-1"></i>
          Sales Overview
        </h3>
      </div>
      <div class="card-body">
        <canvas id="lineChart" style="min-height: 250px; height: 250px; max-height: 250px; width: 100%;"></canvas>
      </div>
    </div>
  </section>
  <section class="col-lg-5 connectedSortable">
    <!-- Pie chart card -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">
          <i class="fas fa-chart-pie mr-1"></i>
          Traffic Sources
        </h3>
      </div>
      <div class="card-body">
        <canvas id="pieChart" style="min-height: 250px; height: 250px; max-height: 250px; width: 100%;"></canvas>
      </div>
    </div>
  </section>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
// Line Chart
var ctxL = document.getElementById('lineChart').getContext('2d');
var lineChart = new Chart(ctxL, {
    type: 'line',
    data: {
        labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
        datasets: [{
            label: 'Sales',
            backgroundColor: 'rgba(60,141,188,0.2)',
            borderColor: 'rgba(60,141,188,1)',
            pointRadius: false,
            pointColor: '#3b8bba',
            pointStrokeColor: 'rgba(60,141,188,1)',
            pointHighlightFill: '#fff',
            pointHighlightStroke: 'rgba(60,141,188,1)',
            data: [65, 59, 80, 81, 56, 55, 40]
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        legend: { display: false }
    }
});
// Pie Chart
var ctxP = document.getElementById('pieChart').getContext('2d');
var pieChart = new Chart(ctxP, {
    type: 'pie',
    data: {
        labels: ['Direct', 'Referral', 'Social'],
        datasets: [{
            data: [300, 50, 100],
            backgroundColor: ['#f56954', '#00a65a', '#f39c12'],
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        legend: { position: 'bottom' }
    }
});
</script>
<?php include './footer.inc.php'; ?>